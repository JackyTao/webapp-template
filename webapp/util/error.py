# -*- coding: utf-8 -*-


class ECError(Exception):
    def __init__(self, status_code, *args, **kwargs):
        self.status_code = status_code
        self.args = args
        self.kwargs = kwargs
        self.info = kwargs.get('info', None)

    def __str__(self):
        message = 'EC %d, %s' % (
            self.status_code,
            self.info)
        return message


class MissingArgumentError(ECError):

    def __init__(self, arg_name, info=''):
        super(MissingArgumentError, self).__init__(
            10101,
            info='Miss Argument: {0}. {1}'.format(arg_name, info))


class InvalidArgumentError(ECError):

    def __init__(self, arg_name, info=''):
        super(InvalidArgumentError, self).__init__(
            10102,
            info='Invalid Argument: {0}. {1}'.format(arg_name, info))


class ArgumentEncodingError(ECError):

    def __init__(self, arg_name, info=''):
        super(InvalidArgumentError, self).__init__(
            10103,
            info='Argument Encoding, UTF-8 needed: {0}. {1}'.format(arg_name, info))


class NotValidVcodeError(ECError):

    def __init__(self):
        super(NotValidVcodeError, self).__init__(
            10401,
            info='vcode not valid')


class NotValidSignError(ECError):

    def __init__(self):
        super(NotValidSignError, self).__init__(
            20401,
            info='sign not valid')


class NotValidTokenError(ECError):

    def __init__(self):
        super(NotValidTokenError, self).__init__(
            20402,
            info='token not valid')


class NotAllowedError(ECError):

    def __init__(self):
        super(NotAllowedError, self).__init__(
            20403,
            info='interface not allowed')


class NotValidCORS(ECError):

    def __init__(self):
        super(NotValidCORS, self).__init__(
            99999,
            info='not allow cors')
