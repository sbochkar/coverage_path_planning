"""Everything to do with logging."""
import logging
from logging import Logger


def get_logger(logger_name: str) -> Logger:
    """Helper function for setting up the logger."""

    # logging module seems to use snake case
    # pylint: disable=invalid-name
    logger = logging.getLogger(logger_name)

    fileHandler = logging.FileHandler("logs/{}.log".format(logger_name))
    streamHandler = logging.StreamHandler()

    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    fileHandler.setFormatter(formatter)
    streamHandler.setFormatter(formatter)

    # Default logging level INFO
    logger.setLevel(logging.INFO)

    return logger
