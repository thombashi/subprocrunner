# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals
import os
import platform
import subprocess

import dataproperty
from logbook import Logger

from ._error import InvalidCommandError
from ._which import Which


logger = Logger("subprocrunner")


class SubprocessRunner(object):

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

    def __init__(self, command, dry_run=False):
        self.__command = command
        self.__dry_run = dry_run
        self.__stdout = None
        self.__stderr = None
        self.__returncode = None

    def run(self):
        self.__verify_command()

        if self.dry_run:
            logger.debug("dry-run: " + self.command)
            return 0

        logger.debug(self.command)
        proc = subprocess.Popen(
            self.command, shell=True, env=self.__get_env(),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.__stdout, self.__stderr = proc.communicate()
        self.__returncode = proc.returncode

        if self.returncode != 0:
            error_message = self.stderr.strip()
            if dataproperty.is_not_empty_string(error_message):
                logger.error(error_message)

        return self.returncode

    def popen(self, std_in=None, environ=None):
        self.__verify_command()

        if self.dry_run:
            logger.debug("dry-run: " + self.command)
            return None

        logger.debug(self.command)
        process = subprocess.Popen(
            self.command, env=self.__get_env(environ), shell=True,
            stdin=std_in, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return process

    def __verify_command(self):
        if dataproperty.is_empty_string(self.command):
            raise InvalidCommandError("invalid str: " + str(self.command))

        if platform.system() == "Windows":
            return

        Which(self.command.split()[0].lstrip("(")).verify()

    def __get_env(self, env=None):
        if env is not None:
            return env

        if platform.system() == "Linux":
            return dict(os.environ, LC_ALL="C")

        return os.environ
