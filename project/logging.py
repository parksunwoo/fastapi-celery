import logging
import logging.config

from celery.utils.log import get_task_logger
from celery.signals import task_postrun, setup_logging
from celery.signals import after_setup_logger


# @setup_logging.connect()
# def on_setup_logging(**kwargs):
def configure_logging():
    logging_dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "[%(asctime)s: %(levelname)s] [%(pathname)s:%(lineno)d] %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "loggers": {
            "project": {
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "propagate": True,
            },
        },
    }
    # logging_dict = {
    #     'version': 1,
    #     'disable_existing_loggers': False,
    #     'handlers': {
    #         'file_log': {
    #             'class': 'logging.FileHandler',
    #             'filename': 'celery.log',
    #         },
    #         'console': {
    #             'class': 'logging.StreamHandler',
    #         }
    #     },
    #     'loggers': {
    #         'celery': {
    #             'handlers': ['console', 'file_log'],
    #             'propagate': False,
    #         },
    #     },
    #     'root': {
    #         'handlers': ['console'],
    #         'level': 'INFO',
    #     },
    # }

    logging.config.dictConfig(logging_dict)

    # from celery.app.log import TaskFormatter
    # celery_logger = logging.getLogger('celery')
    # for handler in celery_logger.handlers:
    #     handler.setFormatter(
    #         TaskFormatter(
    #             '[%(asctime)s: %(levelname)s/%(processName)s/%(thread)d] [%(task_name)s(%(task_id)s)] %(message)s'
    #         )
    #     )


@after_setup_logger.connect()
def on_after_setup_logger(logger, **kwargs):
    formatter = logger.handlers[0].formatter
    file_handler = logging.FileHandler('celery.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)