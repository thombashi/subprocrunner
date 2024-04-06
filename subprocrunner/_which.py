"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import errno
import os
import shutil
from typing import Optional

from .error import CommandError
from .typing import Command


class Which:
    @property
    def command(self) -> Command:
        return self.__command

    def __init__(self, command: str, follow_symlinks: bool = False) -> None:
        if not command:
            raise ValueError("require a command")

        if not command:
            raise ValueError("require a command")

        self.__command = command
        self.__follow_symlinks = follow_symlinks
        self.__abspath: Optional[str] = None

    def __repr__(self) -> str:
        item_list = [
            f"command={self.command}",
            f"is_exist={self.is_exist()}",
            f"follow_symlinks={self.__follow_symlinks}",
        ]

        if self.is_exist():
            item_list.append(f"abspath={self.abspath()}")

        return ", ".join(item_list)

    def is_exist(self) -> bool:
        return self.abspath() is not None and os.path.exists(str(self.abspath()))

    def verify(self) -> None:
        if not self.is_exist():
            raise CommandError(
                f"command not found: {self.command}",
                cmd=self.command,
                errno=errno.ENOENT,
            )

    def abspath(self) -> Optional[str]:
        if self.__abspath:
            return self.__abspath

        self.__abspath = shutil.which(self.command)  # type: ignore
        if self.__abspath is None:
            return self.__abspath

        if self.__follow_symlinks and os.path.islink(self.__abspath):
            self.__abspath = os.path.realpath(self.__abspath)

        return self.__abspath
