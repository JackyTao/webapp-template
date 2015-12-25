# -*- coding: utf-8 -*-

import inspect
from . import log

logger = log.LogService.getLogger()


def gen_get_argument(func):
    arg_names, varargs, varkws, defaults = inspect.getargspec(func)

    arg_names = arg_names or []
    defaults = defaults or []
    offset = len(arg_names) - len(defaults)

    def partial_get_argument(args, kws):
        def get_argument(arg_name, default=None):
            if arg_name in arg_names:
                i = arg_names.index(arg_name)
                if i < len(args):
                    return args[i]
                elif arg_name in kws:
                    return kws.get(arg_name)
                elif i >= offset:
                    return defaults[i - offset]
                else:
                    return default
            else:
                return default
        return get_argument

    return partial_get_argument


def gen_remove_argument(func):
    arg_names, varargs, varkws, defaults = inspect.getargspec(func)
    arg_names = arg_names or []
    defaults = defaults or []

    def remove_argument(args, kws, names):
        remove_args_index = []
        for arg_name in names:
            if arg_name in arg_names:
                i = arg_names.index(arg_name)
                if i < len(args):
                    remove_args_index.append(i)
                elif arg_name in kws:
                    kws.pop(arg_name)
        args = [v for k, v in enumerate(args) if k not in remove_args_index]
        return args, kws

    return remove_argument
