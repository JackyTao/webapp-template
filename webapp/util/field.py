# -*- coding: utf-8 -*-

import re
import json
from lxml.html import clean

from .error import (
    InvalidArgumentError,
    ArgumentEncodingError,
    NotValidTokenError,
    InternalError,
)
from . import crypt
from . import log

logger = log.LogService().getLogger()


def IntegerField(number_type='all', minv=None, maxv=None):

    number_types = {
        'all': lambda x: ((minv is None) or (x >= minv)) and ((maxv is None) or (x <= maxv)),
        'pos': lambda x: x > 0,
        'neg': lambda x: x < 0,
    }

    def _(key, value):
        try:
            v = int(value)
            if number_types[number_type](v):
                return v
        except:
            pass
        raise InvalidArgumentError(key)
    return _


def StringField(char_type='all', min_len=0, max_len=''):

    pattern = {
        'char': r'^[a-zA-Z]{%s,%s}$' % (min_len, max_len),
        'word': r'^\w{%s,%s}$' % (min_len, max_len),
        'cell': r'^1\d{10}$',
        'digit': r'^\d{%s,%s}$' % (min_len, max_len),
        'email': r'^(\w)+(\.\w+)*@(\w)+((\.\w{2,3}){1,3})$',
        # with (?s) . can match \n in the string
        'all': r'^(?s).{%s,%s}$' % (min_len, max_len),
    }

    def _(key, value):
        try:
            # Chinese unicode can not be decoded twice
            if not isinstance(value, unicode):
                v = value.decode('utf-8')
            else:
                v = value
            if re.search(pattern.get(char_type, pattern['all']), v):
                return value
            else:
                raise InvalidArgumentError(key)
        except UnicodeDecodeError:
            raise ArgumentEncodingError(key)
        except:
            raise InvalidArgumentError(key)
    return _


def TokenField():

    def _(key, value):
        r = crypt.decrypt(value)
        if r is None:
            raise NotValidTokenError()
        return value

    return _


def HtmlField():
    cleaner = clean.Cleaner()
    cleaner.page_structure = True
    cleaner.kill_tags = ['script']
    cleaner.allow_tags = [
        'div', 'p', 'h1', 'h2', 'h3', 'font', 'b', 'i', 'u',
        'strike', 'ol', 'li', 'ul', 'a', 'img', 'hr', 'span']
    cleaner.safe_attrs_only = True
    cleaner.safe_attrs = cleaner.safe_attrs.union(['style', 'data-indent'])
    cleaner.remove_unknown_tags = False

    def _(key, value):
        # if len(value.encode('utf-8')) > 65535:
        if len(value) > 10000:
            raise InvalidArgumentError(key, msg='Too long')
        value = cleaner.clean_html(value)
        return value
    return _


def check_num(vtype, maxv=None, minv=None, trans=None):
    def _(v):
        try:
            logger.debug('check %s %s', vtype, v)
            v = vtype(v)
            if ((minv is None) or (v >= minv)) and ((maxv is None) or (v <= maxv)):
                if trans is not None:
                    v = trans(v)
                return True, v
        except:
            pass
        return False, 0
    return _


def JSONField(json_type=None, need_transform=True):
    '''
        pattern for list:
            [pattern, check_conf]
    '''
    type_conf = {
        'order_sku_list': [{
            'sku_id': check_num(int, minv=0),
            'count': check_num(int, minv=1),
            },
            {'min': 1, 'max': 20, 'check': None}
        ],
        'goods_img_list': [
            {'img_url': (str, unicode), 'img_summary': (str, unicode),},
            {'min': 0, 'max': 10, 'check': None}
        ],
        'goods_spec': [
            (str, unicode), {'min': 0, 'max': 3, 'check': None}
        ],
        'sku_list': [{
            'sku_inventory': check_num(int, minv=0, maxv=999),
            'sku_spec': [(str, unicode), {'max': 3}],
            'sku_price': check_num(float, minv=0, maxv=1000000, trans=lambda x: int(x * 100)),
            },
            {'min': 1, 'max': 100, 'check': None}
        ],
        'update_sku_list': [{
            'sku_id': int,
            'sku_inventory': check_num(int, minv=0, maxv=999),
            'sku_price': check_num(float, minv=0, maxv=1000000, trans=lambda x: int(x * 100)),
            },
            {'min': 0, 'max': 100, 'check': None}
        ],
        'dict': dict,
        'cart_goods_list': [{
            'goods_id': lambda x: (isinstance(x, int) and x > 0, x),
            'goods_name': lambda x: (isinstance(x, int) and x > 0, x),
            'goods_index_img': str,
            'goods_spec': dict
            },
            {'min': 0, 'max': 20, 'check': None}
        ],
        # default
        'freight_tpl': [{
                'province_ids': [
                    int,
                    {'min': 0, 'max': 20, 'check': None}
                ],
                'content': {
                    'base_num': lambda x: (isinstance(x, int) and x > 0, x),
                    'base_fee': lambda x: (isinstance(x, int) and x > 0, x),
                    'incr_num': lambda x: (isinstance(x, int) and x > 0, x),
                    'incr_fee': lambda x: (isinstance(x, int) and x > 0, x),
                }
            },
            {'min': 1, 'max': 20, 'check': None}
        ],
    }

    def _(key, value):
        try:
            logger.debug('k: %s, v: %s, type: %s', key, value, type(value))
            v = json.loads(value)
            logger.debug('k: %s, v: %s, type: %s', key, v, type(v))
            if json_type not in type_conf:
                raise InternalError('Error check argument: %s, %s' % (key, value))
            else:
                valid, v = check_json(v, type_conf[json_type])
                if not valid:
                    raise InvalidArgumentError(key)
            return v if need_transform else value
        except Exception as e:
            logger.warn('%s %s %s', e, key, value)
            raise InvalidArgumentError(key)
    return _


def check_json(value, pattern):
    logger.debug('to check value: %s, pattern: %s' % (value, pattern))
    valid, v = False, value
    if isinstance(pattern, types.FunctionType):
        valid, v = pattern(value)
    elif isinstance(pattern, dict) and isinstance(value, dict):
        valid, v = True, {}
        for i in pattern:
            tvalid, tv = check_json(value.get(i), pattern[i])
            v[i] = tv
            valid = valid and tvalid
    elif isinstance(pattern, list) and isinstance(value, list):
        minlen = pattern[1].get('min')
        maxlen = pattern[1].get('max')
        check = pattern[1].get('check')
        valid, v = (
            ((minlen is None) or (len(value) >= minlen))
            and ((maxlen is None) or (len(value) <= maxlen))
            and ((check is None) or check(value))
        ), []
        for i in value:
            tvalid, tv = check_json(i, pattern[0])
            v.append(tv)
            valid = valid and tvalid
    elif isinstance(pattern, tuple):
        if type(value) in pattern:
            valid = True
    else:
        # raw types default
        if isinstance(value, pattern):
            valid = True
    logger.debug('value: %s, pattern: %s, valid: %s' % (value, pattern, valid))
    return valid, v


def _check_json(key, value, pattern):
    logger.debug('check value: %s, pattern: %s' % (value, pattern))
    v = value
    if isinstance(pattern, types.FunctionType):
        v = pattern(key, value)
    elif isinstance(pattern, dict) and isinstance(value, dict):
        v = [_check_json(i, value.get(i), pattern[i]) for i in pattern]
    elif isinstance(pattern, list) and isinstance(value, list):
        minlen = pattern[1].get('min')
        maxlen = pattern[1].get('max')
        check = pattern[1].get('check')
        if not (((minlen is None) or (len(value) >= minlen))
                and ((maxlen is None) or (len(value) <= maxlen))
                and ((check is None) or check(value))):
            raise InvalidArgumentError(key)
        v = [_check_json(key, i, pattern[0]) for i in value]
    elif isinstance(pattern, tuple):
        if type(value) not in pattern:
            raise InvalidArgumentError(key)
    else:
        # raw types default
        if not isinstance(value, pattern):
            raise InvalidArgumentError(key)
    return v


def _check_num(number_type, maxv=None, minv=None, trans=None):
    num_check = lambda x: ((minv is None) or (x >= minv)) and ((maxv is None) or (x <= maxv)),

    def _(key, value):
        try:
            v = number_type(value)
            if num_check(v):
                if trans is not None:
                    v = trans(v)
                return v
        except:
            pass
        raise InvalidArgumentError(key, str(value))
    return _


if __name__ == '__main__':
    print HtmlField()('k', '<html><div>aaaa</div></html>')
    print HtmlField()('k', '<div>aaaa</div><p>...</p><script>content of script!!</script>...')
    # print check_json({'a': 2, 'b': 'aaa'}, {'a': int, 'b': str})
    # print check_json({'a': 2, 'b': 2}, {'a': int, 'b': str})
