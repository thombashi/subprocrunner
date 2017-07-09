# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals

import shutil
import warnings

import six
import typepy

from ._error import CommandNotFoundError
from ._error import InvalidCommandError


class Which(object):

    @property
    def command(self):
        return self.__command

    def __init__(self, command):
        if not typepy.is_not_null_string(command):
            raise InvalidCommandError("invalid str {}: ".format(command))

        self.__command = command

    def is_exist(self):
        return self.which() is not None

    def verify(self):
        if not self.is_exist():
            raise CommandNotFoundError(
                "command not found: '{}'".format(self.command))

    def full_path(self):
        if six.PY2:
            from distutils.spawn import find_executable
            return find_executable(self.command)

        return shutil.which(self.command)

    def which(self):
        warnings.warn(
            "which() deleted in the future, "
            "use full_path() instead.",
            DeprecationWarning
        )

        return self.full_path()
