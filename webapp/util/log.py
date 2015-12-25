# -*- coding: utf-8 -*-

import logging
import logging.config

from conf.config import LOGGING_CONFIG


class LogService():

    logging.config.dictConfig(LOGGING_CONFIG)

    @classmethod
    def getLogger(cls):
        return logging.getLogger('root')


def hc_request_func(handler):
    logger = LogService().getLogger()
    if handler.get_status() < 400:
        log_method = logger.info
    elif handler.get_status() < 500:
        log_method = logger.warning
    else:
        log_method = logger.error
    request_time = 1000.0 * handler.request.request_time()
    log_method(
        "%d %s %.2fms",
        handler.get_status(),
        handler._request_summary(),
        request_time
    )


if __name__ == '__main__':
    logger = LogService.getLogger()
    logger.info('a test log')
    print __file__
