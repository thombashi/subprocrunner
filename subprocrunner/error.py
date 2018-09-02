# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import subprocess
import sys


class CommandError(Exception):
    @property
    def cmd(self):
        return self.__cmd

    @property
    def errno(self):
        return self.__errno

    def __init__(self, *args, **kwargs):
        self.__cmd = kwargs.pop("cmd", None)
        self.__errno = kwargs.pop("errno", None)

        super(CommandError, self).__init__(*args, **kwargs)


class CalledProcessError(subprocess.CalledProcessError):
    def __init__(self, *args, **kwargs):
        if sys.version_info[0:2] <= (3, 4):
            # stdout and stderr attribute added to subprocess.CalledProcessError since Python 3.5
            self.stdout = kwargs.pop("stdout", None)
            self.stderr = kwargs.pop("stderr", None)

        super(CalledProcessError, self).__init__(*args, **kwargs)


class InvalidCommandError(CommandError):
    # Deprecate in the future
    pass


class CommandNotFoundError(CommandError):
    # Deprecate in the future
    pass
