# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals


class CommandError(Exception):

    @property
    def errno(self):
        return self.__errno

    def __init__(self, *args, **kwargs):
        self.__errno = kwargs.pop("errno", None)

        super(CommandError, self).__init__(*args, **kwargs)


class InvalidCommandError(CommandError):
    pass


class CommandNotFoundError(CommandError):
    pass
