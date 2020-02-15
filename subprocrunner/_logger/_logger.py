"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""


from typing import Callable, Optional

from ._null_logger import NullLogger


MODULE_NAME = "subprocrunner"
DEFAULT_ERROR_LOG_LEVEL = "WARNING"


try:
    from loguru import logger

    LOGURU_INSTALLED = True
    logger.disable(MODULE_NAME)
except ImportError:
    LOGURU_INSTALLED = False
    logger = NullLogger()  # type: ignore


def get_logging_method(log_level: Optional[str] = None) -> Callable:
    if not LOGURU_INSTALLED:
        return logger.debug

    if log_level is None:
        log_level = "DEBUG"

    method_table = {
        "QUIET": lambda _x: None,
        "TRACE": logger.trace,
        "DEBUG": logger.debug,
        "INFO": logger.info,
        "SUCCESS": logger.success,
        "WARNING": logger.warning,
        "ERROR": logger.error,
        "CRITICAL": logger.critical,
    }

    method = method_table.get(log_level)
    if method is None:
        raise ValueError("unknown log level: {}".format(log_level))

    return method


def set_logger(is_enable: bool, propagation_depth: int = 1) -> None:
    if is_enable:
        logger.enable(MODULE_NAME)
    else:
        logger.disable(MODULE_NAME)


def set_log_level(log_level):
    # deprecated
    return
