from loguru import logger
from datetime import datetime as dt

log_file = "log.jsonl"
def init_log(log_file=log_file):
    logger.add(log_file,serialize=True,format="{time} : [{level} - {message} . {extra}]")
    return ""

"""
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
"""
"""
def log(method, message="", extra=""):
    logger_method = {
        "i": logger.info,
        "t": logger.trace,
        "d": logger.debug,
        "s": logger.success,
        "w": logger.warning,
        "e": logger.error,
        "c": logger.critical
    }.get(method, logger.info)

    # depth=1 ensures the log points to the caller of `log()`
    logger_method.opt(depth=1).log(message)

"""

def log(method, message="",depth=1):
    level_map = {
        "i": "INFO",
        "t": "TRACE",
        "d": "DEBUG",
        "s": "SUCCESS",
        "w": "WARNING",
        "e": "ERROR",
        "c": "CRITICAL"
    }

    level = level_map.get(method, "INFO")

    # Use logger.log() instead of calling logger.info/debug/etc.
    # depth=1 ensures caller info points to the caller of log()
    logger.opt(depth=depth).log(level, message)
    return ""
