# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import unicode_literals

import platform  # noqa: W0611
import re

import pytest
import subprocrunner
from subprocrunner import Which
from typepy import is_not_null_string


class Test_Which_constructor(object):
    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            [0, subprocrunner.CommandError],
            ["", subprocrunner.CommandError],
            [None, subprocrunner.CommandError],
        ],
    )
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            Which(value)


class Test_Which_repr(object):
    @pytest.mark.skipif("platform.system() == 'Windows'")
    @pytest.mark.parametrize(
        ["value", "expected_regexp"],
        [
            ["ls", re.compile("^command=ls, is_exist=True, abspath=.*?bin/ls$")],
            [
                "__not_exist_command__",
                re.compile("^command=__not_exist_command__, is_exist=False$"),
            ],
        ],
    )
    def test_normal(self, value, expected_regexp):
        assert expected_regexp.search(str(Which(value))) is not None


class Test_Which_is_exist(object):
    @pytest.mark.skipif("platform.system() == 'Windows'")
    @pytest.mark.parametrize(
        ["value", "expected"], [["ls", True], ["/bin/ls", True], ["__not_exist_command__", False]]
    )
    def test_normal_linux(self, value, expected):
        assert Which(value).is_exist() == expected

    @pytest.mark.skipif("platform.system() != 'Windows'")
    @pytest.mark.parametrize(
        ["value", "expected"], [["ping", True], ["__not_exist_command__", False]]
    )
    def test_normal_windows(self, value, expected):
        which = Which(value)
        assert which.is_exist() == expected


class Test_Which_verify(object):
    @pytest.mark.skipif("platform.system() == 'Windows'")
    @pytest.mark.parametrize(["value"], [["ls"]])
    def test_normal_linux(self, value):
        Which(value).verify()

    @pytest.mark.skipif("platform.system() != 'Windows'")
    @pytest.mark.parametrize(["value"], [["ping"]])
    def test_normal_windows(self, value):
        Which(value).verify()

    @pytest.mark.parametrize(
        ["value", "expected"], [["__not_exist_command__", subprocrunner.CommandError]]
    )
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            Which(value).verify()


class Test_Which_abspath(object):
    @pytest.mark.skipif("platform.system() == 'Windows'")
    @pytest.mark.parametrize(["value"], [["ls"]])
    def test_normal_linux(self, value):
        assert is_not_null_string(Which(value).abspath())

    @pytest.mark.skipif("platform.system() != 'Windows'")
    @pytest.mark.parametrize(["value"], [["ping"]])
    def test_normal_windows(self, value):
        assert is_not_null_string(Which(value).abspath())

    @pytest.mark.parametrize(["value"], [["__not_exist_command__"]])
    def test_abnormal(self, value):
        assert Which(value).abspath() is None
