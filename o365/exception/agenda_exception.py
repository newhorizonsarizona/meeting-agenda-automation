from loguru import logger


class AgendaException(Exception):
    """This class is a custom exception for known errors"""

    def __init__(self, message):
        """initialize the agenda exception"""
        logger.error(message)
