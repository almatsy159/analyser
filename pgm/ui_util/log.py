from loguru import logger
from datetime import datetime as dt

log_file = "log.jsonl"
def init_log(log_file=log_file):
    logger.add(log_file,serialize=True,format="{time} : [{level} - {message} . {extra}]")


def log(method,message="",extra=""):
    time = dt.now()
    
    match method:
        case "i":
            logger.info(message)
            level = "INFO"
        case "t":
            logger.trace(message)
            level = "TRACE"
        case "d":
            logger.debug(message)
            level = "DEBUG"
        case "s":
            logger.success(message)
            level = "SUCCESS"
        case "w":
            logger.warning(message)
            level = "WARNING"
        case "e":
            logger.error(message)
            level = "ERROR"
        case "c":
            logger.critical(message)
        case _:
            logger.info(f"default_output : {message}")
            level = "INFO"



