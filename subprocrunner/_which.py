"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""


import errno
import shutil
from typing import Optional

from .error import CommandError


class Which:
    @property
    def command(self):
        return self.__command

    def __init__(self, command: str) -> None:
        if not command:
            raise CommandError(
                "invalid command {}: ".format(command), cmd=command, errno=errno.EINVAL
            )

        self.__command = command
        self.__abspath = None  # type: Optional[str]

    def __repr__(self) -> str:
        item_list = ["command={}".format(self.command), "is_exist={}".format(self.is_exist())]

        if self.is_exist():
            item_list.append("abspath={}".format(self.abspath()))

        return ", ".join(item_list)

    def is_exist(self) -> bool:
        return self.abspath() is not None

    def verify(self) -> None:
        if not self.is_exist():
            raise CommandError(
                "command not found: '{}'".format(self.command), cmd=self.command, errno=errno.ENOENT
            )

    def abspath(self) -> Optional[str]:
        if self.__abspath:
            return self.__abspath

        self.__abspath = shutil.which(self.command)

        return self.__abspath
