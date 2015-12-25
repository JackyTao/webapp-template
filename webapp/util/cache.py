# -*- coding:utf-8 -*-

import redis
import json
import functools

from . import log
from . import argument
from conf.config import MOBILE_CACHE_REDIS_HOST

logger = log.LogService.getLogger()


CACHE_KEY_CONFIG = {
    'test': {'prefix': 'TEST_',},
    'default': {'prefix': 'DEFAULT_',},
    'store_is_open': {'prefix': 'STORE_IS_OPEN_',},
    'store_order_ids': {'prefix': 'STORE_ORDER_IDS_',},
    'store_goods_ids': {'prefix': 'STORE_GOODS_IDS_',},
    'store_category_ids': {'prefix': 'STORE_CATEGORY_IDS_',},
    'order': {'prefix': 'ORDER_',},
    'goods': {'prefix': 'GOODS_',},
    'category': {'prefix': 'CATEGORY_',}
    }


class CacheFactory():
    '''
    3 types of cache patterns:
        1. key - value
        2. key - [v1, v2, v3, ....]  extra op like: offset, limit
        3. keys - values
    '''

    cache = None

    @classmethod
    def getEcCache(cls):
        try:
            cls.cache.ping()
        except:
            cls.cache = redis.Redis(**MOBILE_CACHE_REDIS_HOST)
        return cls.cache

    @classmethod
    def clear(cls):
        cls.getEcCache().flushall()


def gen_trans_key(type_key):
    prefix = CACHE_KEY_CONFIG.get(type_key)['prefix']

    def trans_key(keys):
        return prefix + '_'.join(map(str, keys))
    return trans_key


def cache(fields, type_key='default', is_list=False,
          cache_anyway=False, expire=None):
    trans_key = gen_trans_key(type_key)

    def get_value(key, args, kws):
        try:
            value = CacheFactory.getEcCache().get(key)
            value = json.loads(value)
        except Exception as e:
            logger.error(e)
            value = None
        return value

    def check_value(key, value, func, expire, cache_anyway, args, kws):
        logger.debug('Value from cache, k - {0}, v - {1}'.format(key, value))
        if value is None:
            value = func(*args, **kws)
            if cache_anyway or value is not None:
                value_as_json = json.dumps(value)
                logger.debug('Not in cache, Calculated is - key: {0}, value: {1}'
                             .format(key, value_as_json))
                try:
                    if expire:
                        CacheFactory.getEcCache().setex(
                            key, value_as_json, int(expire))
                    else:
                        CacheFactory.getEcCache().set(key, value_as_json)
                except Exception as e:
                    logger.error(e)
        return value

    def get_list_value(key, get_argument):

        offset = get_argument('offset', 0)
        limit = get_argument('limit', None)
        start = offset
        end = offset + limit - 1 if limit else -1

        try:
            value = CacheFactory.getEcCache().zrange(
                key, start, end, desc=False)
            value = map(json.loads, value)
            total = CacheFactory.getEcCache().zcard(key)
        except Exception as e:
            logger.error(e)
            value, total = [], 0
        return value, total

    def check_list_value(key, value, total, func, expire, cache_anyway,
                         args, kws, get_argument, remove_argument):
        if not value:
            offset = get_argument('offset', 0)
            limit = get_argument('limit', default=None)
            args, kws = remove_argument(args, kws, ['offset', 'limit'])
            value, total = func(*args, **kws)
            logger.debug('Not in cache, Calculated is - k: {0}, v: {1} - [{2}:+{3}]'.format(
                key, value, offset, limit))
            if cache_anyway or value:
                try:
                    CacheFactory.getEcCache().delete(key)
                    CacheFactory.getEcCache().zadd(key,
                        **{json.dumps(k): index
                        for index, k in enumerate(value)})
                    if expire:
                        CacheFactory.getEcCache().expire(key, int(expire))
                except Exception as e:
                    logger.error(e)
            start, end = offset, offset + limit if limit is not None else None
            value = value[start:end]
        return value, total

    def wrapper(func):
        remove_argument = argument.gen_remove_argument(func)
        partial_get_argument = argument.gen_get_argument(func)

        @functools.wraps(func)
        def _list(*args, **kws):
            '''
                The function must be like:
                    func(arg1, arg2, ..., offset=0, limit=None)
                offset,limit must be the last 2 keyword argument
            '''
            get_argument = partial_get_argument(args, kws)
            key = trans_key(map(get_argument, fields))
            value_in_cache, total_in_cache = get_list_value(key, get_argument)
            logger.debug(
                'Value from cache list, k: %s, v: %s - [%s:+%s]',
                key,
                value_in_cache,
                get_argument('offset', 0),
                get_argument('limit', None))
            value, total = check_list_value(
                key, value_in_cache, total_in_cache, func, expire,
                cache_anyway, args, kws, get_argument, remove_argument)
            return value, total

        @functools.wraps(func)
        def _item(*args, **kws):
            get_argument = partial_get_argument(args, kws)
            key = trans_key(map(get_argument, fields))
            value_in_cache = get_value(key, args, kws)
            value = check_value(
                key, value_in_cache, func, expire,
                cache_anyway, args, kws)
            return value

        return _list if is_list else _item
    return wrapper


def cache_multiple(field, type_key='default', expire=None):
    '''
    For function as:
        func(keys) -> values
        [k1, k2, k3,...] -> [v1, v2, v3]
    Make sure, keys and values are matched
    If can not get value for k, the v is None
        [k1, k2, k, ...] -> [v1, v2, None, ...]
    '''

    def get_mult(keys):
        try:
            value = CacheFactory.getEcCache().mget(keys)
            value = map(lambda x: json.loads(x) if x is not None else x, value)
        except Exception as e:
            logger.error(e)
            value = [None] * len(keys)
        return value

    def set_mult(pairs, expire=None):
        try:
            c = CacheFactory.getEcCache()
            p = c.pipeline()
            if expire:
                for k, v in pairs.iteritems():
                    p.setex(k, json.dumps(v), expire)
            else:
                for k, v in pairs.iteritems():
                    p.set(k, json.dumps(v))
            p.execute()
        except Exception as e:
            logger.error(e)

    trans_key = gen_trans_key(type_key)
    def wrapper(func):
        partial_get_argument = argument.gen_get_argument(func)

        @functools.wraps(func)
        def _(*args, **kws):
            keys = partial_get_argument(
                args, kws)(field, default=[])
            values = get_mult(map(trans_key, [(k,) for k in keys]))

            #logger.debug('Values from cache multiple: %s', values)

            miss_keys = [keys[i] for i, v in enumerate(values) if v is None]
            miss_values = func(miss_keys)
            miss_pairs = dict(zip(miss_keys, miss_values))
            set_mult(
                {trans_key([k]): miss_pairs[k]
                 for k in miss_pairs
                 if miss_pairs[k] is not None},
                expire)

            for i, v in enumerate(values):
                if v is None:
                    values[i] = miss_pairs[keys[i]]
            return values
        return _
    return wrapper


def _cache_dispose(spec_list):
    '''
        suffix_fields: to gen extre keys, key value from fields
        suffix_values: to gen extra keys for dispose

        new:
            fields: ('a', (param1, param2), [value1, value2], 'b')
    '''

    def wrapper(func):
        partial_get_argument = argument.gen_get_argument(func)

        @functools.wraps(func)
        def _(*args, **kws):
            get_argument = partial_get_argument(args, kws)

            for fields, type_key in spec_list:
                trans_key = gen_trans_key(type_key)

                #: raw_keys: would be like:
                #:  [['v1'], ['v2', 'v3'], ['v4']]
                raw_keys = []
                for field in fields:
                    if isinstance(field, tuple):
                        # param
                        raw_keys.append(map(get_argument, field))
                    elif isinstance(field, list):
                        # values
                        raw_keys.append(field)
                    else:
                        raw_keys.append([get_argument(field)])

                try:
                    c = CacheFactory.getEcCache()
                    p = c.pipeline()
                    for k in gen_key(raw_keys):
                        key = trans_key(k)
                        logger.debug('Dispose key: %s', key)
                        # ret - 0: fail, 1: success
                        p.delete(key)
                    p.execute()
                except Exception as e:
                    logger.error(e)
            return func(*args, **kws)
        return _
    return wrapper


def gen_key(raw_keys):
    l = len(raw_keys)
    cur_pattern = [0] * l
    len_pattern = [len(i) for i in raw_keys]
    is_over = False

    while not is_over:
        yield [raw_keys[i][k] for i, k in enumerate(cur_pattern)]

        # Go to next
        i = l - 1
        while i >= 0:
            cur_pattern[i] += 1
            cur_pattern[i] %= len_pattern[i]
            if cur_pattern[i] == 0:
                i -= 1
            else:
                break
        if i < 0:
            is_over = True


if __name__ == '__main__':
    #for i in gen_key([[8], [1, 2], [2, 3], [1]]):
    #    print i
    CacheFactory.clear()
