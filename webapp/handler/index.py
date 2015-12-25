# -*- coding:utf-8 -*-

import json

import tornado.gen
import tornado.web

import service.sohuhttp
from . import base
from . import apiwrapper


class IndexHandler(base.BaseHandler):

    # @apiwrapper.auth()
    # @tornado.gen.coroutine
    def get(self):
        # self.render('index.html')
        # a, b = yield [
        #    service.sohuhttp.inner_call('http://www.baidu.com'),
        #    service.sohuhttp.inner_call('http://www.sohu.com')
        # ]
        # raise Exception()

        # self.finish(self.request.uri + 'Init Project OK!')
        self.finish(u'启动成功')

    def post(self):
        arg = self.get_arguments('arg', None)
        print 'arg:', arg
        self.finish('ok')


class HtmlHandler(base.BaseHandler):

    def get(self):
        print 'headers', self.request.headers
        self.render('index.html')


class DataHandler(base.BaseHandler):

    def get(self):
        loader = self._get_data_loader()

        try:
            html = loader.load('addr.json').generate()
        except Exception as e:
            print e
            html = ''
        self.set_header('Content-Type', 'application/json')
        self.finish(html)
