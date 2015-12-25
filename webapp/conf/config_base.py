# -*- coding: utf-8 -*-

import os

# logging settings
CURRENT_DIR = os.path.dirname(__file__) or '.'
DATA_PATH = os.path.join(CURRENT_DIR, '../data/')
LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simpleFormatter': {
                'format': '%(asctime)s - [%(levelname)s] - %(module)s.%(funcName)s:%(lineno)d - %(message)s',
                'datefmt': '%Y%m%d %H:%M:%S'
                },
            'reactionFormatter': {
                'format': '%(asctime)s,%(module)s.%(funcName)s,%(message)s',
                'datefmt': '%Y%m%d %H:%M:%S'
                },
            },
        'handlers': {
            'consoleHandler': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simpleFormatter',
                },
            'standFileHandler': {
                'level': 'DEBUG',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'simpleFormatter',
                'filename': CURRENT_DIR + '/../../logs/stdout.log',
                'when': 'D',
                'interval': 1,
                'backupCount': 60,
                },
            'reactionFileHandler': {
                'level': 'INFO',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'reactionFormatter',
                'filename': CURRENT_DIR + '/../../logs/reaction.log',
                'when': 'D',
                'interval': 1,
                'backupCount': 60,
                },
            },
        'loggers': {
            'root': {
                'level': 'DEBUG',
                'handlers': ['standFileHandler'],
                },
            'reaction': {
                'level': 'INFO',
                'handlers': ['reactionFileHandler'],
                'qualname': 'reaction',
                'propagate': 0,
                },
            },
        }


settings = dict(
    template_path=os.path.join(CURRENT_DIR, '../', 'templates'),
    static_path=os.path.join(CURRENT_DIR, '../', 'static'),
    debug=True,
    login_url='/auth/login')
