# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals
import shutil

import dataproperty
import six

from ._error import InvalidCommandError
from ._error import CommandNotFoundError


class Which(object):

    @property
    def command(self):
        return self.__command

    def __init__(self, command):
        if dataproperty.is_empty_string(command):
            raise InvalidCommandError("invalid str: " + str(command))

        self.__command = command

    def is_exist(self):
        if self.which() is None:
            return False

        return True

    def verify(self):
        if not self.is_exist():
            raise CommandNotFoundError(
                "command not found: '{}'".format(self.command))

    def which(self):
        if six.PY2:
            from distutils.spawn import find_executable
            return find_executable(self.command)

        return shutil.which(self.command)
