from MyLogger import MyLogger

logger = MyLogger()

def debug(text:str):
    logger.debug(text)

def info(text:str):
    logger.info(text)

def warn(text:str):
    logger.warn(text)

def error(text:str):
    logger.error(text)

def exception(text:str):
    logger.exception(text)
