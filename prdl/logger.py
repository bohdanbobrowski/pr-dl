import logging
import sys


class OnlyErrorFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.ERROR

class NotErrorFilter(logging.Filter):
    def filter(self, record):
        return not record.levelno == logging.ERROR


class Logger(logging.Logger):
    def __init__(self, name, level=logging.INFO):
        super(Logger, self).__init__(name, level)
        log_handler = logging.StreamHandler(sys.stdout)
        log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_handler.setFormatter(log_formatter)
        log_handler.addFilter(NotErrorFilter())
        self.addHandler(log_handler)

        error_handler = logging.StreamHandler(sys.stderr)
        error_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        error_handler.setFormatter(error_formatter)
        error_handler.addFilter(OnlyErrorFilter())
        self.addHandler(error_handler)
