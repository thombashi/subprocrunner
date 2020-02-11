"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""


import errno
import shutil
import warnings

from .error import CommandError


class Which:
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

        self.__abspath = shutil.which(self.command)

        return self.__abspath
