"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

# keep the following line for backward compatibility
from subprocess import CalledProcessError  # noqa
from typing import Any, Optional

from .typing import Command


class CommandError(Exception):
    @property
    def cmd(self) -> Optional[Command]:
        return self.__cmd

    @property
    def errno(self) -> Optional[int]:
        return self.__errno

    def __init__(self, *args: str, **kwargs: Any) -> None:
        self.__cmd = kwargs.pop("cmd", None)
        self.__errno = kwargs.pop("errno", None)

        super().__init__(*args)
