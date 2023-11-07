import logging


class MyFormat(logging.Formatter):
    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    green = "\x1b[32m"
    asctime = "%(asctime)s"
    name = "[%(name)s]"
    levelname = "[%(levelname)-4s]"
    message = "%(message)s"

    FORMATS = {
        logging.DEBUG: f"{asctime} {grey} {name} {levelname} {reset} {message}",
        logging.INFO: f"{asctime} {green} {name} {levelname} {reset} {message}",
        logging.WARNING: f"{asctime} {yellow} {name} {levelname} {message} {reset}",
        logging.ERROR: f"{asctime} {red} {name} {levelname} {message} {reset}",
        logging.CRITICAL: f"{asctime} {bold_red} {name} {levelname} {message} {reset}",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger(mod_name: str) -> logging.Logger:
    log = logging.getLogger(mod_name)
    handler = logging.StreamHandler()
    handler.setFormatter(MyFormat())
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)
    return log