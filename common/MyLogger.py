import os,sys
import errno
import time
from datetime import datetime
import logging
from utils_common import create_dir_if_not_exist

class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    blue = "\x1b[34;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s %(levelname)-2s %(message)s"

    FORMATS = {
        logging.DEBUG: blue + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(fmt=log_fmt, datefmt='%H:%M:%S')
        return formatter.format(record)

def setup_logger(name, log_file, print_console = True, level=logging.DEBUG):
        """Function setup as many loggers as you want"""

        logger = logging.getLogger(name)

        if log_file :
            formatter = logging.Formatter(
                '%(asctime)s %(levelname)s %(message)s', "%Y-%m-%d %H:%M:%S")
            handler = logging.FileHandler(log_file)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        if not print_console:
            logger.propagate = False

        # create console handler with a higher log level
        # for color logging
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(CustomFormatter())
        logger.addHandler(ch)

        logger.setLevel(level)

        return logger

class MyLogger():
    __logger = None
    __start_time = time.time()

    def __init__(self, log_file:str=None, level=logging.INFO, logger_name:str="glob"):

        if not log_file:
            pathname = os.path.dirname(sys.argv[0])
            work_dir=os.path.abspath(pathname)
            log_dir = work_dir +"/log"
            log_file = log_dir+"/application.log"
        create_dir_if_not_exist(log_file)

        try:
            if os.getpgrp() == os.tcgetpgrp(sys.stdout.fileno()):
                print('Running in foreground. '+str(datetime.now()))
                logger = setup_logger(logger_name, log_file, True, level)
                # logging.basicConfig(level=level)
            else:
                # Don't! If you catch, likely to hide bugs.
                raise EnvironmentError('background detected')
        except Exception as e:
            print('Running in background. '+str(datetime.now()))
            logger = setup_logger(logger_name, log_file, False, level)
            logging.propagate = False
            #logging.basicConfig(stream=sys.stderr, filename=log_file,level=_level)
            if str(e) != "background detected":
                logging.exception("unk exception:")

        logger.info("--------------------------- STARTED ----------------------------------")

        #disabling def logging handlers to error only"
        logging.getLogger("urllib3").setLevel(logging.ERROR)
        logging.getLogger("requests").setLevel(logging.ERROR)
        logging.getLogger("TeleBot").setLevel(logging.CRITICAL)
        self.__logger = logger

    def debug(self, text:str):
        self.__logger.debug(text)

    def info(self, text:str):
        self.__logger.info(text)

    def info_starttime(self, text:str):
        self.__logger.info(f"{time.time() - self.__start_time} s, {text}")

    def warn(self, text:str):
        self.__logger.warn(text)

    def error(self, text:str):
        self.__logger.error(text)

    def critical(self, text:str):
        self.__logger.critical(text)

    def exception(self, text:str):
        self.__logger.exception(text)




