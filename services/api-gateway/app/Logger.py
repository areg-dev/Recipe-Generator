import logging


class Logger:
    log = None

    @staticmethod
    def initialize_logger():
        Logger.log = logging.getLogger("API Gateway")
        Logger.log.setLevel(logging.INFO)
        log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s] - %(message)s', '%Y-%m-%d %H:%M:%S')
        file_handler = logging.FileHandler('app.log')
        file_handler.setFormatter(log_formatter)
        Logger.log.addHandler(file_handler)

    @staticmethod
    def error(msg):
        Logger.log.error(msg)

    @staticmethod
    def warning(msg):
        Logger.log.warning(msg)

    @staticmethod
    def info(msg):
        Logger.log.info(msg)

    @staticmethod
    def debug(msg):
        Logger.log.debug(msg)
