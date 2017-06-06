# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals

import os
import platform
import subprocess

import logbook
from mbstrdecoder import MultiByteStrDecoder
import typepy

from ._error import InvalidCommandError
from ._logger import logger
from ._which import Which


class SubprocessRunner(object):
    """
    .. py:attribute:: default_is_dry_run

        Class wide dry-run setting default value.
        dry-run if ``True``.

    .. py:attribute:: is_save_history

        Save executed command history if ``True``.
    """

    _DRY_RUN_OUTPUT = ""

    default_error_log_level = logbook.WARNING
    default_is_dry_run = False
    is_save_history = False
    history_size = 512
    __command_history = []

    @classmethod
    def get_history(cls):
        return cls.__command_history

    @classmethod
    def clear_history(cls):
        cls.__command_history = []

    @property
    def dry_run(self):
        return self.__dry_run

    @property
    def command(self):
        return self.__command

    @property
    def stdout(self):
        return self.__stdout

    @property
    def stderr(self):
        return self.__stderr

    @property
    def returncode(self):
        return self.__returncode

    @property
    def error_log_level(self):
        raise NotImplementedError()

    @error_log_level.setter
    def error_log_level(self, log_level):
        self.__error_logging_method = self.__get_logging_method(log_level)

    def __init__(self, command, ignore_stderr_regexp=None, dry_run=None):
        self.__command = command
        if dry_run is not None:
            self.__dry_run = dry_run
        else:
            self.__dry_run = self.default_is_dry_run
        self.__stdout = None
        self.__stderr = None
        self.__returncode = None

        self.__ignore_stderr_regexp = ignore_stderr_regexp
        self.__debug_logging_method = self.__get_logging_method(logbook.DEBUG)
        self.error_log_level = self.default_error_log_level

        if self.is_save_history:
            if len(self.__command_history) >= self.history_size:
                self.__command_history.pop(0)

            self.__command_history.append(command)

    def run(self):
        self.__verify_command()

        if self.dry_run:
            self.__stdout = self._DRY_RUN_OUTPUT
            self.__stderr = self._DRY_RUN_OUTPUT
            self.__returncode = 0

            self.__debug_logging_method("dry-run: {}".format(self.command))

            return self.__returncode

        self.__debug_logging_method(self.command)

        try:
            proc = subprocess.Popen(
                self.command, shell=True, env=self.__get_env(),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except TypeError:
            proc = subprocess.Popen(
                self.command, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        self.__stdout, self.__stderr = proc.communicate()
        self.__returncode = proc.returncode

        self.__stdout = MultiByteStrDecoder(self.__stdout).unicode_str
        self.__stderr = MultiByteStrDecoder(self.__stderr).unicode_str

        if self.returncode == 0:
            return 0

        try:
            if self.__ignore_stderr_regexp.search(self.stderr) is not None:
                return self.returncode
        except AttributeError:
            pass

        self.__error_logging_method(
            "command='{}', returncode={}, stderr={}".format(
                self.command, self.returncode, self.stderr))

        return self.returncode

    def popen(self, std_in=None, environ=None):
        self.__verify_command()

        if self.dry_run:
            self.__stdout = self._DRY_RUN_OUTPUT
            self.__stderr = self._DRY_RUN_OUTPUT
            self.__returncode = 0

            self.__debug_logging_method("dry-run: {}".format(self.command))

            return subprocess.CompletedProcess(
                args=[], returncode=self.__returncode,
                stdout=self.__stdout, stderr=self.__stderr)

        self.__debug_logging_method(self.command)

        try:
            process = subprocess.Popen(
                self.command, env=self.__get_env(environ), shell=True,
                stdin=std_in, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except TypeError:
            process = subprocess.Popen(
                self.command, shell=True,
                stdin=std_in, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return process

    def __verify_command(self):
        if typepy.is_null_string(self.command):
            raise InvalidCommandError("invalid str: {}".format(self.command))

        if self.dry_run or platform.system() == "Windows":
            return

        Which(self.command.split()[0].lstrip("(")).verify()

    def __get_env(self, env=None):
        if env is not None:
            return env

        if platform.system() == "Linux":
            return dict(os.environ, LC_ALL="C")

        return os.environ

    @staticmethod
    def __get_logging_method(log_level):
        method_table = {
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
