# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import unicode_literals
import errno
import os
import platform
from subprocess import PIPE

import dataproperty
import pytest
import six

from subprocrunner import SubprocessRunner


os_type = platform.system()
if os_type == "Linux":
    list_command = "ls"
    list_command_errno = errno.ENOENT
elif os_type == "Windows":
    list_command = "dir"
    list_command_errno = 1
else:
    raise NotImplementedError(os_type)


class Test_SubprocessRunner_run:

    @pytest.mark.parametrize(["command", "dry_run", "expected"], [
        [list_command, False, 0],
        [list_command, True, 0],
        [list_command + " __not_exist_dir__", False, list_command_errno],
        [list_command + " __not_exist_dir__", True, 0],
    ])
    def test_normal(self, command, dry_run, expected):
        assert SubprocessRunner(command, dry_run).run() == expected

    @pytest.mark.parametrize(["command", "expected"], [
        ["echo test", "test"],
    ])
    def test_stdout(self, command, expected):
        runner = SubprocessRunner(command)
        runner.run()
        assert runner.stdout.strip() == six.b(expected)
        assert dataproperty.is_empty_string(runner.stderr)

    @pytest.mark.parametrize(["command"], [
        [list_command + " __not_exist_dir__"],
    ])
    def test_stderr(self, command):
        runner = SubprocessRunner(command)
        runner.run()
        assert dataproperty.is_not_empty_string(runner.stderr.strip())


class Test_SubprocessRunner_popen:

    @pytest.mark.parametrize(["command", "environ", "expected"], [
        ["hostname", None, 0],
        ["hostname", dict(os.environ), 0],
    ])
    def test_normal(self, command, environ, expected):
        proc = SubprocessRunner(command).popen(environ=environ)
        ret_stdout, ret_stderr = proc.communicate()
        assert dataproperty.is_not_empty_string(ret_stdout)
        assert dataproperty.is_empty_string(ret_stderr)
        assert proc.returncode == expected

    @pytest.mark.skipif("platform.system() == 'Windows'")
    @pytest.mark.parametrize(["command", "input", "expected"], [
        ["grep a", six.b("aaa"), 0],
    ])
    def test_normal_stdin(self, command, input, expected):
        proc = SubprocessRunner(command).popen(PIPE)
        ret_stdout, ret_stderr = proc.communicate(input=input)
        assert dataproperty.is_not_empty_string(ret_stdout)
        assert dataproperty.is_empty_string(ret_stderr)
        assert proc.returncode == expected
