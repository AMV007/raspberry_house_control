import logging
import os, sys
from datetime import datetime
from time import sleep

#   LOGGING

pathname = os.path.dirname(sys.argv[0])
work_dir=os.path.abspath(pathname)
LOG_DIR = work_dir +"/log"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

glob_logger_name = "glob"
logger = None
logger_print_console = True


def setup_logger(name, log_file, level=logging.DEBUG):
    """Function setup as many loggers as you want"""

    logger = logging.getLogger(name)

    if log_file != None:
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s', "%Y-%m-%d %H:%M:%S")
        handler = logging.FileHandler(log_file)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    if not logger_print_console:
        logger.propagate = False

    logger.setLevel(level)
    return logger


def check_dir_exist(filename):
    if not os.path.exists(os.path.dirname(filename)):
        logging.info("log path not exist, trying to recreate it")
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def my_init_logging(_level=logging.INFO):
    global logger
    global logger_print_console

    log_file = work_dir+"/log/application.log"
    check_dir_exist(log_file)

    try:
        if os.getpgrp() == os.tcgetpgrp(sys.stdout.fileno()):
            print('Running in foreground. '+str(datetime.now()))
            logger_print_console = True
            logger = setup_logger(glob_logger_name, log_file, _level)
            # logging.basicConfig(level=_level)
        else:
            # Don't! If you catch, likely to hide bugs.
            raise Exception('background detected')
    except Exception as e:
        print('Running in background. '+str(datetime.now()))
        logger_print_console = False
        logger = setup_logger(glob_logger_name, log_file, _level)
        logging.propagate = False
        #logging.basicConfig(stream=sys.stderr, filename=log_file,level=_level)
        logger.info(
            "----------------------------------------------------------------------")
        if str(e) != "background detected":
            logging.exception("unk exception:")

    logging.info("enabling def logging handlers")
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("requests").setLevel(logging.ERROR)
    logging.getLogger("TeleBot").setLevel(logging.CRITICAL)
    return logger
