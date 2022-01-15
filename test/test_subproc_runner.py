"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""


import errno
import os
import platform
import re
import sys
from subprocess import PIPE

import pytest
from typepy import is_not_null_string, is_null_string

from subprocrunner import SubprocessRunner
from subprocrunner._logger._null_logger import NullLogger
from subprocrunner.error import CalledProcessError
from subprocrunner.retry import Retry


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


BACKOFF_FACTOR = 0.01
JITTER = 0.01


class Test_SubprocessRunner_repr:
    @pytest.mark.parametrize(
        ["command", "dry_run", "expected"],
        [
            [
                ["ls", "hoge"],
                False,
                "SubprocessRunner(command='ls hoge', returncode='not yet executed')",
            ],
            [
                ["ls", "hoge"],
                True,
                "SubprocessRunner(command='ls hoge', returncode='not yet executed', dry_run=True)",
            ],
        ],
    )
    def test_normal(self, command, dry_run, expected):
        assert str(SubprocessRunner(command=["ls", "hoge"], dry_run=dry_run)) == expected


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
        ["command", "expected"],
        [
            ["echo test", "test"],
            [["echo", "test"], "test"],
        ],
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
        print(f"[sys stdout]\n{out}\n")
        print(f"[sys stderr]\n{err}\n")
        print(f"[proc stdout]\n{runner.stdout}\n")
        print(f"[proc stderr]\n{runner.stderr}\n")

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

    def test_input_kwarg(self, mocker):
        mocked_communicate = mocker.patch("subprocess.Popen.communicate")
        mocked_communicate.return_value = ("", "")

        runner = SubprocessRunner(list_command)
        runner.run(input="test input")

        mocked_communicate.assert_called_with(input=b"test input", timeout=None)

    def test_timeout_kwarg(self, mocker):
        mocked_communicate = mocker.patch("subprocess.Popen.communicate")
        mocked_communicate.return_value = ("", "")

        mocker.patch("subprocrunner.Which.verify")
        runner = SubprocessRunner("dummy")
        runner.run(timeout=1)

        mocked_communicate.assert_called_with(input=None, timeout=1)

    def test_unicode(self, mocker):
        mocked_communicate = mocker.patch("subprocess.Popen.communicate")
        mocked_communicate.return_value = (
            "",
            "'dummy' は、内部コマンドまたは外部コマンド、" "操作可能なプログラムまたはバッチ ファイルとして認識されていません",
        )

        runner = SubprocessRunner(list_command)
        runner.run()

    def test_retry(self, mocker):
        mocker.patch("subprocrunner.Which.verify")

        runner = SubprocessRunner("always-failed-command")
        retry_ct = 3

        # w/ retry: check=False
        mocked_run = mocker.patch("subprocrunner.SubprocessRunner._run")
        mocked_run.return_value = 1
        runner.run(
            check=False,
            retry=Retry(total=retry_ct, backoff_factor=BACKOFF_FACTOR, jitter=JITTER),
        )
        assert mocked_run.call_count == retry_ct + 1

        # w/ retry: check=True
        mocked_run = mocker.patch("subprocrunner.SubprocessRunner._run")
        mocked_run.return_value = 1
        try:
            runner.run(
                check=True,
                retry=Retry(total=retry_ct, backoff_factor=BACKOFF_FACTOR, jitter=JITTER),
            )
        except CalledProcessError:
            pass
        assert mocked_run.call_count == retry_ct + 1

        # w/o retry: check=False
        mocked_run = mocker.patch("subprocrunner.SubprocessRunner._run")
        mocked_run.return_value = 1
        runner.run(check=False, retry=None)
        assert mocked_run.call_count == 1

        # w/o retry: check=True
        mocked_run = mocker.patch("subprocrunner.SubprocessRunner._run")
        mocked_run.return_value = 1
        try:
            runner.run(check=True, retry=None)
        except CalledProcessError:
            pass
        assert mocked_run.call_count == 1

    def test_no_retry_returncodes(self, mocker):
        mocker.patch("subprocrunner.Which.verify")

        runner = SubprocessRunner("always-failed-command")
        mocked_run = mocker.patch("subprocrunner.SubprocessRunner._run")
        mocked_run.return_value = 2
        runner.run(
            check=True,
            retry=Retry(
                total=3,
                backoff_factor=BACKOFF_FACTOR,
                jitter=JITTER,
                no_retry_returncodes=[2],
            ),
        )
        assert mocked_run.call_count == 1

    def test_retry_success_ater_failed(self, mocker):
        mocker.patch("subprocrunner.Which.verify")

        def failed_first_call(*args, **kwargs):
            attempt = kwargs.get(SubprocessRunner._RETRY_ATTEMPT_KEY)
            if attempt is None:
                return 1

            return 0

        runner = SubprocessRunner("always-failed-command")
        mocked_run = mocker.patch("subprocrunner.SubprocessRunner._run")
        mocked_run.side_effect = failed_first_call
        runner.run(check=True, retry=Retry(total=3, backoff_factor=BACKOFF_FACTOR, jitter=JITTER))
        assert mocked_run.call_count == 2


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
        ["command", "dry_run"],
        [
            [list_command, False],
            [list_command, True],
        ],
    )
    def test_normal(self, command, dry_run):
        loop_count = 3

        SubprocessRunner.is_save_history = False
        SubprocessRunner.clear_history()
        for _i in range(loop_count):
            SubprocessRunner(command, dry_run=dry_run).run()
        assert SubprocessRunner.get_history() == []

        SubprocessRunner.is_save_history = True
        SubprocessRunner.clear_history()
        for _i in range(loop_count):
            SubprocessRunner(command, dry_run=dry_run).run()
        assert SubprocessRunner.get_history() == [list_command] * loop_count

    def test_normal_retry(self, mocker):
        SubprocessRunner.clear_history()
        SubprocessRunner.is_save_history = True
        command = [list_command, "not_exist_dir"]
        runner = SubprocessRunner(command)
        retry_ct = 3

        runner.run(retry=Retry(total=retry_ct, backoff_factor=BACKOFF_FACTOR, jitter=JITTER))
        assert runner.get_history() == [" ".join(command)] * (retry_ct + 1)
