import logging
from django.conf import settings

logger = logging.getLogger("root")


class Logger:

    def __init__(self, msg, type, *args, **kwargs):
        method = getattr(self, type, None)
        if callable(method):
            if settings.DEBUG:
                print(msg)
            method(msg, exc_info=kwargs.get('exc_info', True))
        else:
            print(f"No method named '{type}' exists.")

    def info(self, msg, exc_info=True):
        logger.info(msg, exc_info=exc_info, extra={"type": "info"})

    def debug(self, msg, exc_info=True):
        logger.debug(msg, exc_info=exc_info, extra={"type": "debug"})

    def log(self, msg, exc_info=True):
        logger.log(msg, exc_info=exc_info, extra={"type": "log"})

    def error(self, msg, exc_info=True):
        logger.error(msg, exc_info=exc_info, extra={"type": "error"})

    def warning(self, msg, exc_info=True):
        logger.warning(msg, exc_info=exc_info, extra={"type": "warning"})

    def exception(self, msg, exc_info=True):
        logger.exception(msg, exc_info=exc_info, extra={"type": "exception"})