# -*- coding:utf-8 -*-

import functools
import time

import tornado.gen
from tornado.concurrent import TracebackFuture

from util import log
from util.error import NotValidCORS

logger = log.LogService().getLogger()

AUTH_ORIGIN_LIST = [
    # '' means not a cors request
    '',
    'http://debug.ec.t1.com:8000',
    'debug.ec.t1.com:8000',
]


def _check(role, user, resource=None):
    roles = {
        'seller': {
            # TODO:
            'is_role': lambda u: True,
            'has_auth': lambda u, r: u['id'] == resource['store_id']
        },
        'passenger': {
            'is_role': lambda u: False,
            'has_auth': lambda: True
        }
    }
    valid = True

    # Step 1. user is type of role
    valid = valid and roles[role]['is_role'](user)

    # Step 2. user has auth of resource
    if resource is not None and not roles[role]['has_auth'](user, resource):
        valid = False
    return valid


def auth(roles=None, check_resource=False):
    '''
    In one round, user act as at least one and only one !!!
    '''
    roles = roles or ['passenger']

    def wrapper(func):
        @functools.wraps(func)
        @tornado.gen.coroutine
        def _(handler, *args, **kwargs):
            # user = yield handler.get_kuaizhan_user()
            user = None

            # Check user
            if user is None:
                raise Exception()

            # Check user auth
            valid = True
            for role in roles:
                if check_resource:
                    # TODO: get resource by role type
                    resource = None
                    valid = valid and _check(role, user, resource)
                else:
                    valid = valid and _check(role, user)
            if not valid:
                raise Exception()

            # Other place of this function 'yield' used,
            # So, we should decorate function with 'coroutine',
            # So, we should use tornado.gen.Return
            # So, we should use r = yield r if r isinstanceof TracebackFuture
            # Call real stuff
            r = func(handler, *args, **kwargs)
            if isinstance(r, TracebackFuture):
                r = yield r
            raise tornado.gen.Return(r)
        return _
    return wrapper


def exe_time(func):
    @functools.wraps(func)
    def _(*args, **kwargs):
        start = time.time()
        r = func(*args, **kwargs)
        logger.debug(
            '%s exec time is: %d',
            func.__name__,
            1000 * (time.time() - start)
        )
        return r
    return _


def cors(allow=True, simple=True, with_credentials=False):
    def wrapper(method):
        @functools.wraps(method)
        def _(handler, *args, **kwargs):
            # Not cross domain
            origin = handler.request.headers.get('origin', '')
            host = handler.request.headers.get('host', '')
            if (origin == '' or origin.endswith(host) or
                    origin.startswith('chrome-extension')):
                return method(handler, *args, **kwargs)

            need_check_origin = False
            '''
            For POST, there may be csrf problems,
            Server side may handle it as same-orgin request,
            So, must be decorated with cors in default to check the origin

            So, there are 4 types of request:
                1. simple cross site
                2. cross site but not simple
                3. post not allow cors(may have problems)
                4. not allow cors: get, put, ...
            '''
            if not allow:
                # Decorate `post() with cors(allow=False)`, to make
                # it the strict cors request, thus prevent csrf prolem
                need_check_origin = True
            elif with_credentials:
                need_check_origin = True
                handler.set_header('Access-Control-Allow-Credentials', 'true')
            elif simple:
                handler.set_header('Access-Control-Allow-Origin', '*')
            else:
                need_check_origin = True
            if need_check_origin:
                # Request from browser would come with 'origin' to check
                # If from backend, unless you can steal the cookie
                origin = handler.request.headers.get('origin', '')
                if origin in AUTH_ORIGIN_LIST:
                    handler.set_header('Access-Control-Allow-Origin', origin)
                else:
                    logger.warn('Not allowed cors request, Origin: %s', origin)
                    # Terminate the request process to prevent side effect
                    raise NotValidCORS()
            return method(handler, *args, **kwargs)
        return _
    return wrapper
