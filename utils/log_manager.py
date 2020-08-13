import logging
import os


formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')


class log_manager():

    def __init__(self, tag):
        self.__tag = tag
        self.__logger = self.setup_logger(tag, f"{tag}.log", logging.DEBUG)

    def setup_logger(self, name, log_file, level=logging.INFO):
        """Function setup as many loggers as you want"""
        if not os.path.exists("logs/"):
            os.mkdir("logs/")
        log_path = "logs/{}".format(log_file)
        handler = logging.FileHandler(log_path, encoding='utf-8')
        handler.setFormatter(formatter)

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)

        return logger

    def debug(self, message):

        self.__logger.debug(message)

    def info(self, message):

        self.__logger.info(message)

    def error(self, message):

        self.__logger.error(message)

    def warn(self, message):

        self.__logger.warning(message)