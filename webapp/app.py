# -*- coding:utf-8 -*-

import tornado.ioloop
import tornado.web
import tornado.options
import tornado.httpclient

from handler import route
from util import log
from conf import config

settings = config.settings


class Application(tornado.web.Application):
    def __init__(self):
        if 'log_function' not in settings:
            settings['log_function'] = log.hc_request_func
        tornado.web.Application.__init__(
            self,
            route.handlers,
            **settings
        )

tornado.options.define('port', default=7000,
                       help="run on the given port", type=int)
tornado.httpclient.AsyncHTTPClient.configure(
    "tornado.simple_httpclient.SimpleAsyncHTTPClient", max_clients=5)


if __name__ == '__main__':
    tornado.options.parse_command_line()
    application = Application()
    application.listen(tornado.options.options.port, xheaders=True)
    tornado.ioloop.IOLoop.instance().start()
