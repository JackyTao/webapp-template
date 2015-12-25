# -*- coding:utf-8 -*-

import json
import sys

import tornado.gen
import tornado.web
from tornado import httputil
from tornado.log import gen_log
from tornado.web import HTTPError

from conf.config import DATA_PATH


class BaseHandler(tornado.web.RequestHandler):

    def _get_data_loader(self):
        return tornado.template.Loader(DATA_PATH)

    def _write_error(self, status_code, **kwargs):
        pass

    def get_current_user(self):
        #return None
        # Kz user authentication
        return True

    def _handle_request_exception(self, e):
        self.log_exception(*sys.exc_info())
        if self._finished:
            return
        if isinstance(e, HTTPError):
            if e.status_code not in httputil.responses and not e.reason:
                gen_log.error("Bad HTTP status code: %d", e.status_code)
                self.finish({'code': 500, 'msg': 'Internal Error'})
            else:
                system_exception = sys.exc_info()[1]
                self.finish({'code': e.status_code, 'msg': system_exception.reason})
        else:
            self.finish({'code': 500, 'msg': 'Internal Error'})

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Credentials', 'true')

    def options(self):
        # Cors would check first by OPTIONS
        self.set_header('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE')
        self.finish()

    def wrap_response(self, data):
        data['uri'] = self.request.uri
        return json.dumps(data)

    def gen_params(self, keys_def):
        return {
            x[0]: x[1]
            for x in map(lambda x: self._transform(x), keys_def)
            if x[1] is not None
        }

    def _transform(self, key_def):
        key, rename, default, transform, validate, need = key_def

        # `default` is for the init input value
        # Query string as: 'a=&b=c', get_argument('a', None)
        # would get '' instead of None
        v = self.get_argument(key, '') or default

        if v is None and need:
            raise MissingArgumentError(key)

        if validate and (v is not None):
            v = validate(key, v)

        if transform and (v is not None):
            v = transform(v)

        return rename, v
