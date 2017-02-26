# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import unicode_literals

import platform

import pytest
from subprocrunner import Which
import subprocrunner
from typepy import (
    is_null_string,
    is_not_null_string,
)


class Test_Which_constructor(object):

    @pytest.mark.parametrize(["value", "expected"], [
        [0, subprocrunner.InvalidCommandError],
        ["", subprocrunner.InvalidCommandError],
        [None, subprocrunner.InvalidCommandError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            Which(value)


class Test_Which_is_exist(object):

    @pytest.mark.skipif("platform.system() != 'Linux'")
    @pytest.mark.parametrize(["value", "expected"], [
        ["ls", True],
        ["__not_exist_command__", False],
    ])
    def test_normal_linux(self, value, expected):
        assert Which(value).is_exist() == expected

    @pytest.mark.skipif("platform.system() != 'Windows'")
    @pytest.mark.parametrize(["value", "expected"], [
        ["ping", True],
        ["__not_exist_command__", False],
    ])
    def test_normal_windows(self, value, expected):
        which = Which(value)
        assert which.is_exist() == expected


class Test_Which_verify(object):

    @pytest.mark.skipif("platform.system() != 'Linux'")
    @pytest.mark.parametrize(["value"], [
        ["ls"],
    ])
    def test_normal_linux(self, value):
        Which(value).verify()

    @pytest.mark.skipif("platform.system() != 'Windows'")
    @pytest.mark.parametrize(["value"], [
        ["ping"],
    ])
    def test_normal_windows(self, value):
        Which(value).verify()

    @pytest.mark.parametrize(["value", "expected"], [
        ["__not_exist_command__", subprocrunner.CommandNotFoundError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            Which(value).verify()


class Test_Which_which(object):

    @pytest.mark.skipif("platform.system() != 'Linux'")
    @pytest.mark.parametrize(["value"], [
        ["ls"],
    ])
    def test_normal_linux(self, value):
        assert is_not_null_string(Which(value).which())

    @pytest.mark.skipif("platform.system() != 'Windows'")
    @pytest.mark.parametrize(["value"], [
        ["ping"],
    ])
    def test_normal_windows(self, value):
        assert is_not_null_string(Which(value).which())

    @pytest.mark.parametrize(["value"], [
        ["__not_exist_command__"],
    ])
    def test_abnormal(self, value):
        assert is_null_string(Which(value).which())
