"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""


import subprocess
import sys


class CommandError(Exception):
    @property
    def cmd(self):
        return self.__cmd

    @property
    def errno(self):
        return self.__errno

    def __init__(self, *args, **kwargs) -> None:
        self.__cmd = kwargs.pop("cmd", None)
        self.__errno = kwargs.pop("errno", None)

        super().__init__(*args)


class CalledProcessError(subprocess.CalledProcessError):
    def __init__(self, *args, **kwargs) -> None:
        if sys.version_info[0:2] <= (3, 4):
            # stdout and stderr attribute added to subprocess.CalledProcessError since Python 3.5
            self.stdout = kwargs.pop("stdout", None)
            self.stderr = kwargs.pop("stderr", None)

        super().__init__(*args, **kwargs)
