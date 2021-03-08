import coloredlogs
import logging
import os

def init_logger(name):
    logger = logging.getLogger(name)
    coloredlogs.install(level=os.getenv("LOG_LEVEL", "INFO"))
    return logger

if __name__ == "__main__":
    logger = init_logger("test_logger.py")
    # Some examples.
    logger.debug("this is a debugging message")
    logger.info("this is an informational message")
    logger.warning("this is a warning message")
    logger.error("this is an error message")
    logger.critical("this is a critical message")