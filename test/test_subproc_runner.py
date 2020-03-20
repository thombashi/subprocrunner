"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""


import errno
import os
import platform
import re
import subprocess
import sys
from subprocess import PIPE, CalledProcessError

import pytest
from typepy import is_not_null_string, is_null_string

from subprocrunner import SubprocessRunner
from subprocrunner._logger._null_logger import NullLogger


os_type = platform.system()
if os_type == "Linux":
    list_command = "ls"
    list_command_errno = [errno.ENOENT]
elif os_type == "Darwin":
    list_command = "ls"
    list_command_errno = [1, errno.ENOENT]
elif os_type == "Windows":
    list_command = "dir"
    list_command_errno = [1]
else:
    raise NotImplementedError(os_type)


class Test_SubprocessRunner_run:
    @pytest.mark.parametrize(
        ["command", "dry_run", "expected"],
        [
            [list_command, False, [0]],
            [list_command, True, [0]],
            [list_command + " __not_exist_dir__", False, list_command_errno],
            [list_command + " __not_exist_dir__", True, [0]],
        ],
    )
    def test_normal(self, monkeypatch, command, dry_run, expected):
        r = SubprocessRunner(command, dry_run=dry_run)
        r.run()

        if not dry_run:
            print(r.stderr, file=sys.stderr)

        assert r.returncode in expected

        monkeypatch.setattr("subprocrunner._logger._logger.logger", NullLogger())
        r.run()

    @pytest.mark.skipif(platform.system() == "Windows", reason="platform dependent tests")
    @pytest.mark.parametrize(
        ["command", "expected"], [[list_command + " -l", 0], [[list_command, "-l"], 0]]
    )
    def test_command(self, command, expected):
        assert SubprocessRunner(command).run() == expected

    @pytest.mark.parametrize(
        ["command", "expected"], [["echo test", "test"], [["echo", "test"], "test"]]
    )
    def test_stdout(self, command, expected):
        runner = SubprocessRunner(command)
        runner.run()

        assert runner.command == command
        assert isinstance(runner.command_str, str)
        assert runner.returncode == 0
        assert runner.stdout.strip() == expected
        assert is_null_string(runner.stderr)

    @pytest.mark.skip
    @pytest.mark.parametrize(
        ["command", "ignore_stderr_regexp", "out_regexp", "expected"],
        [
            [list_command + " __not_exist_dir__", None, re.compile("WARNING"), True],
            [
                list_command + " __not_exist_dir__",
                re.compile(re.escape("__not_exist_dir__")),
                re.compile("WARNING"),
                False,
            ],
        ],
    )
    def test_stderr(self, capsys, command, ignore_stderr_regexp, out_regexp, expected):
        from loguru import logger
        import subprocrunner

        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
        logger.enable("test")
        subprocrunner.set_logger(True)

        runner = SubprocessRunner(command, ignore_stderr_regexp=ignore_stderr_regexp)
        runner.run()

        assert is_null_string(runner.stdout.strip())
        assert is_not_null_string(runner.stderr.strip())
        assert runner.returncode != 0

        out, err = capsys.readouterr()
        print("[sys stdout]\n{}\n".format(out))
        print("[sys stderr]\n{}\n".format(err))
        print("[proc stdout]\n{}\n".format(runner.stdout))
        print("[proc stderr]\n{}\n".format(runner.stderr))

        actual = out_regexp.search(err) is not None
        assert actual == expected

    @pytest.mark.skipif(platform.system() == "Windows", reason="platform dependent tests")
    @pytest.mark.parametrize(
        ["command", "ignore_stderr_regexp", "expected"],
        [
            [[list_command, "__not_exist_dir__"], None, CalledProcessError],
            [[list_command, "__not_exist_dir__"], re.compile(re.escape("__not_exist_dir__")), None],
        ],
    )
    def test_stderr_check(self, command, ignore_stderr_regexp, expected):
        runner = SubprocessRunner(command, ignore_stderr_regexp=ignore_stderr_regexp)

        if ignore_stderr_regexp:
            runner.run(check=True)
        else:
            with pytest.raises(expected):
                runner.run(check=True)

    def test_unicode(self, monkeypatch):
        def monkey_communicate(input=None):
            return ("", "'dummy' は、内部コマンドまたは外部コマンド、" "操作可能なプログラムまたはバッチ ファイルとして認識されていません")

        monkeypatch.setattr(subprocess.Popen, "communicate", monkey_communicate)

        runner = SubprocessRunner(list_command)
        runner.run()


class Test_SubprocessRunner_popen:
    @pytest.mark.parametrize(
        ["command", "environ", "expected"],
        [["hostname", None, 0], ["hostname", dict(os.environ), 0]],
    )
    def test_normal(self, command, environ, expected):
        proc = SubprocessRunner(command).popen(env=environ)
        ret_stdout, ret_stderr = proc.communicate()
        assert is_not_null_string(ret_stdout)
        assert is_null_string(ret_stderr)
        assert proc.returncode == expected

    @pytest.mark.skipif(platform.system() == "Windows", reason="platform dependent tests")
    @pytest.mark.parametrize(["command", "pipe_input", "expected"], [["grep a", b"aaa", 0]])
    def test_normal_stdin(self, command, pipe_input, expected):
        proc = SubprocessRunner(command).popen(PIPE)
        ret_stdout, ret_stderr = proc.communicate(input=pipe_input)

        assert is_not_null_string(ret_stdout)
        assert is_null_string(ret_stderr)
        assert proc.returncode == expected


class Test_SubprocessRunner_command_history:
    @pytest.mark.parametrize(
        ["command", "dry_run", "expected"], [[list_command, False, 0], [list_command, True, 0]]
    )
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
