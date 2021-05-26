"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""


import errno
import os
import platform
import subprocess
import traceback
from subprocess import PIPE
from typing import Sequence, Union  # noqa
from typing import Dict, List, Optional, Pattern, cast

from mbstrdecoder import MultiByteStrDecoder

from ._logger import DEFAULT_ERROR_LOG_LEVEL, get_logging_method
from ._which import Which
from .error import CalledProcessError, CommandError
from .retry import Retry
from .typing import Command


class SubprocessRunner:
    """
    .. py:attribute:: default_is_dry_run

        Class wide dry-run setting default value.
        dry-run if ``True``.

    .. py:attribute:: is_save_history

        Save executed command history if ``True``.
    """

    _DRY_RUN_OUTPUT = ""

    default_error_log_level = DEFAULT_ERROR_LOG_LEVEL
    default_is_dry_run = False

    is_output_stacktrace = False

    is_save_history = False
    history_size = 512

    __command_history = []  # type: List[Command]

    @classmethod
    def get_history(cls) -> List[Command]:
        return cls.__command_history

    @classmethod
    def clear_history(cls) -> None:
        cls.__command_history = []

    def __init__(
        self,
        command: Command,
        error_log_level: Optional[str] = None,
        ignore_stderr_regexp: Optional[Pattern] = None,
        dry_run: Optional[bool] = None,
        quiet: bool = False,
    ) -> None:
        self.__command = []  # type: Union[str, Sequence[str]]

        if not command:
            raise ValueError("command is empty")

        if isinstance(command, (list, tuple)):
            self.__is_shell = False
            self.__command = [str(item) for item in command]
        else:
            self.__is_shell = True
            self.__command = command

        if dry_run is not None:
            self.__dry_run = dry_run
        else:
            self.__dry_run = self.default_is_dry_run
        self.__stdout = None  # type: Optional[str]
        self.__stderr = None  # type: Optional[str]
        self.__returncode = None  # type: Optional[int]

        self.__ignore_stderr_regexp = ignore_stderr_regexp
        self.__debug_logging_method = get_logging_method("QUIET" if quiet else "DEBUG")

        if quiet:
            self.error_log_level = "QUIET"
        elif error_log_level is not None:
            self.error_log_level = error_log_level
        else:
            self.error_log_level = self.default_error_log_level

        if self.is_save_history:
            if len(self.__command_history) >= self.history_size:
                self.__command_history.pop(0)

            self.__command_history.append(command)

        self.__quiet = quiet

    @property
    def dry_run(self) -> bool:
        return self.__dry_run

    @property
    def command(self) -> Command:
        return self.__command

    @property
    def command_str(self) -> str:
        if self.__is_shell:
            return cast(str, self.__command)

        return " ".join(self.__command)

    @property
    def stdout(self) -> Optional[str]:
        return self.__stdout

    @property
    def stderr(self) -> Optional[str]:
        return self.__stderr

    @property
    def returncode(self) -> Optional[int]:
        return self.__returncode

    @property
    def error_log_level(self):
        raise NotImplementedError()

    @error_log_level.setter
    def error_log_level(self, log_level: Optional[str]):
        self.__error_logging_method = get_logging_method(log_level)

    def _run(self, env, check: bool, timeout: Optional[float] = None, **kwargs) -> int:
        try:
            proc = subprocess.Popen(
                self.command,
                shell=self.__is_shell,
                env=env,
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
            )
        except TypeError:
            proc = subprocess.Popen(
                self.command, shell=self.__is_shell, stdin=PIPE, stdout=PIPE, stderr=PIPE
            )

        stdout, stderr = proc.communicate(timeout=timeout, **kwargs)
        self.__returncode = proc.returncode

        self.__stdout = MultiByteStrDecoder(stdout).unicode_str
        self.__stderr = MultiByteStrDecoder(stderr).unicode_str

        if self.returncode == 0:
            return 0

        try:
            if (
                self.__ignore_stderr_regexp
                and self.__ignore_stderr_regexp.search(self.stderr) is not None
            ):
                return self.__returncode
        except AttributeError:
            pass

        self.__error_logging_method(
            "command='{}', returncode={}, stderr={!r}".format(
                self.command, self.returncode, self.stderr
            )
        )

        if check is True:
            raise CalledProcessError(
                returncode=self.__returncode,
                cmd=self.command_str,
                output=self.stdout,
                stderr=self.stderr,
            )

        return self.__returncode

    def run(self, timeout: Optional[float] = None, retry: Retry = None, **kwargs) -> int:
        self.__verify_command()

        check = kwargs.pop("check", False)
        env = self.__get_env(kwargs.pop("env", None))

        if self.dry_run:
            self.__stdout = self._DRY_RUN_OUTPUT
            self.__stderr = self._DRY_RUN_OUTPUT
            self.__returncode = 0

            if not self.__quiet:
                self.__debug_logging_method("dry-run: {}".format(self.command))

            return self.__returncode

        self.__debug_print_command()
        self._run(env=env, check=check if retry is None else False, timeout=timeout, **kwargs)

        if self.__returncode == 0 or retry is None:
            return self.__returncode  # type: ignore

        for i in range(retry.total):
            self.__error_logging_method(self.stderr)

            retry.sleep_before_retry(
                attempt=i + 1,
                logging_method=self.__debug_logging_method,
                retry_target=self.command_str,
            )

            if self._run(env=env, check=False, timeout=timeout, **kwargs) == 0:
                break

        if check is True:
            raise CalledProcessError(
                returncode=self.__returncode,  # type: ignore
                cmd=self.command_str,
                output=self.stdout,
                stderr=self.stderr,
            )

        return self.__returncode  # type: ignore

    def popen(self, std_in: Optional[int] = None, env: Optional[Dict[str, str]] = None):
        self.__verify_command()

        if self.dry_run:
            self.__stdout = self._DRY_RUN_OUTPUT
            self.__stderr = self._DRY_RUN_OUTPUT
            self.__returncode = 0

            self.__debug_logging_method("dry-run: {}".format(self.command))

            return subprocess.CompletedProcess(
                args=[], returncode=self.__returncode, stdout=self.__stdout, stderr=self.__stderr
            )

        self.__debug_print_command()

        try:
            process = subprocess.Popen(
                self.command,
                env=self.__get_env(env),
                shell=self.__is_shell,
                stdin=std_in,
                stdout=PIPE,
                stderr=PIPE,
            )
        except TypeError:
            process = subprocess.Popen(
                self.command, shell=self.__is_shell, stdin=std_in, stdout=PIPE, stderr=PIPE
            )

        return process

    def __verify_command(self) -> None:
        if not self.command:
            raise CommandError(
                "invalid command: {}".format(self.command), cmd=self.command_str, errno=errno.EINVAL
            )

        if self.dry_run or platform.system() == "Windows":
            return

        if self.__is_shell:
            base_command = cast(str, self.command).split()[0].lstrip("(")
        else:
            base_command = self.command[0]

        Which(base_command).verify()

    @staticmethod
    def __get_env(env=None):
        if env is not None:
            return env

        if platform.system() == "Linux":
            return dict(os.environ, LC_ALL="C")

        return os.environ

    def __debug_print_command(self) -> None:
        message_list = [self.command_str]

        if self.is_output_stacktrace:
            message_list.append("".join(traceback.format_stack()[:-2]))

        if not self.__quiet:
            self.__debug_logging_method("\n".join(message_list))
