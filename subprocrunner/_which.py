"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import errno
import os
import shutil
from typing import Optional

from .error import CommandError


class Which:
    @property
    def command(self):
        return self.__command

    def __init__(self, command: str, follow_symlinks: bool = False) -> None:
        if not command:
            raise ValueError("require a command")

        self.__command = command
        self.__follow_symlinks = follow_symlinks
        self.__abspath = None  # type: Optional[str]

    def __repr__(self) -> str:
        item_list = [
            "command={}".format(self.command),
            "is_exist={}".format(self.is_exist()),
            "follow_symlinks={}".format(self.__follow_symlinks),
        ]

        if self.is_exist():
            item_list.append("abspath={}".format(self.abspath()))

        return ", ".join(item_list)

    def is_exist(self) -> bool:
        return self.abspath() is not None and os.path.exists(str(self.abspath()))

    def verify(self) -> None:
        if not self.is_exist():
            raise CommandError(
                "command not found: '{}'".format(self.command), cmd=self.command, errno=errno.ENOENT
            )

    def abspath(self) -> Optional[str]:
        if self.__abspath:
            return self.__abspath

        self.__abspath = shutil.which(self.command)
        if self.__abspath is None:
            return self.__abspath

        if self.__follow_symlinks and os.path.islink(self.__abspath):
            self.__abspath = os.path.realpath(self.__abspath)

        return self.__abspath
