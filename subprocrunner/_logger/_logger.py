# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

from ._null_logger import NullLogger


try:
    import logbook

    logger = logbook.Logger("subprocrunner")
    logger.disable()
    LOGBOOK_INSTALLED = True
    DEFAULT_ERROR_LOG_LEVEL = logbook.WARNING
except ImportError:
    logger = NullLogger()
    LOGBOOK_INSTALLED = False
    DEFAULT_ERROR_LOG_LEVEL = 13


def get_logging_method(log_level=None):
    if not LOGBOOK_INSTALLED:
        return logger.debug

    if log_level is None:
        log_level = logbook.DEBUG

    method_table = {
        logbook.NOTSET: lambda _x: None,
        logbook.DEBUG: logger.debug,
        logbook.INFO: logger.info,
        logbook.WARNING: logger.warning,
        logbook.ERROR: logger.error,
        logbook.CRITICAL: logger.critical,
    }

    method = method_table.get(log_level)
    if method is None:
        raise ValueError("unknown log level: {}".format(log_level))

    return method


def set_logger(is_enable):
    if not LOGBOOK_INSTALLED:
        return

    if is_enable:
        logger.enable()
    else:
        logger.disable()


def set_log_level(log_level):
    """
    Set logging level of this module. Using
    `logbook <https://logbook.readthedocs.io/en/stable/>`__ module for logging.

    :param int log_level:
        One of the log level of
        `logbook <https://logbook.readthedocs.io/en/stable/api/base.html>`__.
        Disabled logging if ``log_level`` is ``logbook.NOTSET``.
    :raises LookupError: If ``log_level`` is an invalid value.
    """

    if not LOGBOOK_INSTALLED:
        return

    # validate log level
    logbook.get_level_name(log_level)

    if log_level == logbook.NOTSET:
        set_logger(is_enable=False)
    else:
        set_logger(is_enable=True)

    logger.level = log_level
