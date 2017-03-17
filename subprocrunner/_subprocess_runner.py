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

    is_save_history = False
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
    def logging_debug(self):
        raise NotImplementedError()

    @logging_debug.setter
    def logging_debug(self, log_level):
        self.__logging_debug = self.__get_logging_method(log_level)

    @property
    def logging_error(self):
        raise NotImplementedError()

    @logging_error.setter
    def logging_error(self, log_level):
        self.__logging_error = self.__get_logging_method(log_level)

    def __init__(self, command, ignore_stderr_regexp=None, dry_run=False):
        self.__command = command
        self.__dry_run = dry_run
        self.__stdout = None
        self.__stderr = None
        self.__returncode = None

        self.__ignore_stderr_regexp = ignore_stderr_regexp

        self.logging_debug = logbook.DEBUG
        self.logging_error = logbook.WARNING

        if self.is_save_history:
            self.__command_history.append(command)

    def run(self):
        self.__verify_command()

        if self.dry_run:
            self.__stdout = None
            self.__stderr = None
            self.__logging_debug("dry-run: " + self.command)
            return 0

        self.__logging_debug(self.command)

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

        self.__logging_error("returncode={}, stderr={}".format(
            self.returncode, self.stderr))

        return self.returncode

    def popen(self, std_in=None, environ=None):
        self.__verify_command()

        if self.dry_run:
            self.__stdout = None
            self.__stderr = None
            self.__logging_debug("dry-run: " + self.command)
            return None

        self.__logging_debug(self.command)

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

        if platform.system() == "Windows":
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
