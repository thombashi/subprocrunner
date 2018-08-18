# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import errno
import shutil
import warnings

from ._six import PY2
from .error import CommandError


class Which(object):
    @property
    def command(self):
        return self.__command

    def __init__(self, command):
        if not command:
            raise CommandError(
                "invalid command {}: ".format(command), cmd=command, errno=errno.EINVAL
            )

        self.__command = command
        self.__abspath = None

    def __repr__(self):
        item_list = ["command={}".format(self.command), "is_exist={}".format(self.is_exist())]

        if self.is_exist():
            item_list.append("abspath={}".format(self.abspath()))

        return ", ".join(item_list)

    def is_exist(self):
        return self.abspath() is not None

    def verify(self):
        if not self.is_exist():
            raise CommandError(
                "command not found: '{}'".format(self.command), cmd=self.command, errno=errno.ENOENT
            )

    def abspath(self):
        if self.__abspath:
            return self.__abspath

        if PY2:
            from distutils.spawn import find_executable

            self.__abspath = find_executable(self.command)
        else:
            self.__abspath = shutil.which(self.command)

        return self.__abspath

    def full_path(self):
        warnings.warn(
            "full_path() deleted in the future, use abspath() instead.", DeprecationWarning
        )

        return self.abspath()

    def which(self):
        warnings.warn("which() deleted in the future, use abspath() instead.", DeprecationWarning)

        return self.abspath()
