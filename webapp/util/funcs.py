# -*- coding: utf-8 -*-

import time


def gen_time_str(time_in_millis):
    now = time.localtime()
    target = time.localtime(time_in_millis)

    if now.tm_year != target.tm_year:
        format_str = '%Y-%m-%d'
    elif now.tm_yday != target.tm_yday:
        format_str = '%m-%d'
    else:
        format_str = '%H:%M'

    return time.strftime(format_str, target)


def format_str(code, msg, **data):
    response = {}
    response['code'] = code
    response['msg'] = msg
    response['data'] = data
    return response
