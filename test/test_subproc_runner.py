# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import print_function
from __future__ import unicode_literals

import errno
import os
import platform
import re
from subprocess import PIPE
import subprocess

import pytest
import six
from subprocrunner import SubprocessRunner
from typepy import (
    is_null_string,
    is_not_null_string,
)


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
        assert SubprocessRunner(command, dry_run=dry_run).run() == expected

    @pytest.mark.parametrize(["command", "expected"], [
        ["echo test", "test"],
    ])
    def test_stdout(self, command, expected):
        runner = SubprocessRunner(command)
        runner.run()

        assert runner.stdout.strip() == expected
        assert is_null_string(runner.stderr)

    @pytest.mark.skipif("platform.system() == 'Windows'")
    @pytest.mark.parametrize(["command", "regexp", "out_regexp", "expected"], [
        [
            list_command + " __not_exist_dir__",
            None,
            re.compile("WARNING: "),
            True,
        ],
        [
            list_command + " __not_exist_dir__",
            re.compile("__not_exist_dir__"),
            re.compile("WARNING: ", re.DOTALL),
            False,
        ],
    ])
    def test_stderr(self, capsys, command, regexp, out_regexp, expected):
        runner = SubprocessRunner(command, ignore_stderr_regexp=regexp)
        runner.run()

        assert is_null_string(runner.stdout.strip())
        assert is_not_null_string(runner.stderr.strip())

    def test_unicode(self, monkeypatch):
        def monkey_communicate(input=None):
            return (
                u"",
                u"'dummy' は、内部コマンドまたは外部コマンド、"
                u"操作可能なプログラムまたはバッチ ファイルとして認識されていません",
            )

        monkeypatch.setattr(
            subprocess.Popen,
            "communicate", monkey_communicate)

        runner = SubprocessRunner(list_command)
        runner.run()


class Test_SubprocessRunner_popen:

    @pytest.mark.parametrize(["command", "environ", "expected"], [
        ["hostname", None, 0],
        ["hostname", dict(os.environ), 0],
    ])
    def test_normal(self, command, environ, expected):
        proc = SubprocessRunner(command).popen(environ=environ)
        ret_stdout, ret_stderr = proc.communicate()
        assert is_not_null_string(ret_stdout)
        assert is_null_string(ret_stderr)
        assert proc.returncode == expected

    @pytest.mark.skipif("platform.system() == 'Windows'")
    @pytest.mark.parametrize(["command", "pipe_input", "expected"], [
        ["grep a", six.b("aaa"), 0],
    ])
    def test_normal_stdin(self, command, pipe_input, expected):
        proc = SubprocessRunner(command).popen(PIPE)
        ret_stdout, ret_stderr = proc.communicate(input=pipe_input)

        assert is_not_null_string(ret_stdout)
        assert is_null_string(ret_stderr)
        assert proc.returncode == expected


class Test_SubprocessRunner_command_history:

    @pytest.mark.parametrize(["command", "dry_run", "expected"], [
        [list_command, False, 0],
        [list_command, True, 0],
    ])
    def test_normal(self, command, dry_run, expected):
        SubprocessRunner.is_save_history = False
        SubprocessRunner.clear_history()

        loop_count = 3
        for _i in range(loop_count):
            SubprocessRunner(command, dry_run=dry_run).run()
        assert len(SubprocessRunner.get_history()) == 0

        SubprocessRunner.is_save_history = True
        for _i in range(loop_count):
            SubprocessRunner(command, dry_run=dry_run).run()
        assert len(SubprocessRunner.get_history()) == loop_count
