# -*- coding: utf-8 -*-

import tornado.httpclient
import tornado.ioloop
import tornado.gen
import tornado.escape
from util import log

logger = log.LogService().getLogger()


@tornado.gen.coroutine
def inner_call(url, method='GET', headers=None, params=None,
               as_form=False, cookies=None, body=None):
    method = method.upper()
    params = params or {}
    headers = headers or {}

    cookies and headers.update({'Cookie': cookies})

    query_str = '&'.join('{0}={1}'.format(
        tornado.escape.url_escape(k),
        tornado.escape.url_escape(v))
        for k, v in params.iteritems()
        if v is not None
    )

    if as_form and method not in ['GET', 'HEAD']:
        body, true_url = query_str, url
    else:
        if url.find('?') == -1:
            true_url = url + '?' + query_str
        else:
            true_url = url + '&' + query_str

    logger.info('Request %s %s', method, true_url)
    logger.debug('Request Body: %s', body)
    logger.debug('Request headers: {0}'.format(headers))
    request = tornado.httpclient.HTTPRequest(
        url=true_url,
        method=method,
        headers=headers,
        body=body
    )

    http = tornado.httpclient.AsyncHTTPClient()
    try:
        # response = yield http.fetch(request, handle_response)
        response = yield http.fetch(request)
    except Exception as e:
        logger.error(e)
        response = e.response
        logger.error('Sohu Http Error - %s %s', method, true_url)
        logger.error('Sohu Http Response - %s %s', e.code, e.response.body)

    raise tornado.gen.Return(response.body)


def handle_response(response):
    logger.info(
        'Response code: %s, reason: %s\n%s',
        response.code, response.reason, response.body)
