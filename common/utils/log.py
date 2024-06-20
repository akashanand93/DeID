import os, sys
from loguru import logger
from common.utils.base import singleton


class LogConstants:
    """Misc Collection of constants!"""

    VERBOSITY = float(os.getenv("VERBOSITY", "0.01"))
    # <level> tag takes the value of color.
    DEFAULT_FORMAT = (
        "<level>{time:HH:mm:ss} {level.icon} | {name}:{function}:{line} | {message}</>"
    )


@singleton
class ConfigureLogging:
    """
    Configures logging for console by default and optionally to a file.
    Console Color Scheme is best suited for dark backgrounds.
    """

    def __init__(
        self,
        level="DEBUG",
        console=True,
        file=None,
        format=LogConstants.DEFAULT_FORMAT,
    ):
        log_level = os.getenv("LOG_LEVEL", level).upper()
        logger.remove()
        if console:
            logger.add(sys.stdout, colorize=True, format=format, level=log_level)
            # Make debug level less distracting.
            logger.level("DEBUG", color="<dim>", icon="🐞")
            # Make INFO level normal instead of bold
            logger.level("INFO", color="<white>", icon="ℹ️")

        if file:
            os.makedirs(os.path.dirname(file), exist_ok=True)
            logger.add(file, format=format, colorize=False, level=log_level)

        logger.info(
            f"Logger Initialized. Log level: {log_level}. Use $LOG_LEVEL to override"
        )
