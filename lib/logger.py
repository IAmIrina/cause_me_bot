import os
import sys

log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'file': {
            'format': '%(asctime)s: [ %(levelname)s ]: %(module)s : [%(process)d]: %(message)s',
        },
    },
    'handlers': {
        'stdout': {
            'class': 'logging.StreamHandler',
            'formatter': 'file',
            'stream': sys.stdout
        }
    },
    'loggers': {
        '': {
            'level': log_level,
            'handlers': ['stdout'],
            'propagate': False,
        },
    },
    'root': {
        'level': log_level,
        'handlers': ['stdout'],
    },
}
