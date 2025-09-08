import logging

from src.core.utils.schema import BaseResponse, CamelCaseModel


def setup_logger(name: str) -> logging.Logger:
    """
    Set up and return a logger with the specified name.

    This function configures a logger to output logs to the console with a
    predefined format that includes the timestamp, log level, logger name,
    and message. It ensures that multiple handlers are not added if the
    logger is already configured.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: A configured logger instance.
    """

    logger = logging.getLogger(name)
    if not logger.handlers:  # Prevent duplicate handlers
        logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # Console Handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


core_logger = setup_logger("core_logger")

__all__ = [
    "BaseResponse",
    "CamelCaseModel",
    "core_logger",
]
