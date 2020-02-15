"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""


import errno
import os
import platform
import subprocess
import traceback
from subprocess import PIPE
from typing import Dict, List, Optional, Pattern, Sequence, Union, cast

from mbstrdecoder import MultiByteStrDecoder

from ._logger import DEFAULT_ERROR_LOG_LEVEL, get_logging_method
from ._which import Which
from .error import CalledProcessError, CommandError


Command = Union[str, Sequence[str]]


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
        error_log_level: None = None,
        ignore_stderr_regexp: Optional[Pattern] = None,
        dry_run: Optional[bool] = None,
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
        self.__stdout = None  # type: Union[str, bytes, None]
        self.__stderr = None  # type: Union[str, bytes, None]
        self.__returncode = None

        self.__ignore_stderr_regexp = ignore_stderr_regexp
        self.__debug_logging_method = get_logging_method()

        if error_log_level is not None:
            self.error_log_level = error_log_level
        else:
            self.error_log_level = self.default_error_log_level

        if self.is_save_history:
            if len(self.__command_history) >= self.history_size:
                self.__command_history.pop(0)

            self.__command_history.append(command)

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
    def stdout(self) -> Union[str, bytes, None]:
        return self.__stdout

    @property
    def stderr(self) -> Union[str, bytes, None]:
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

    def run(self, **kwargs) -> Optional[int]:
        self.__verify_command()

        check = kwargs.pop("check", None)
        env = kwargs.pop("env", None)

        if self.dry_run:
            self.__stdout = self._DRY_RUN_OUTPUT
            self.__stderr = self._DRY_RUN_OUTPUT
            self.__returncode = 0

            self.__debug_logging_method("dry-run: {}".format(self.command))

            return self.__returncode

        self.__debug_print_command()

        try:
            proc = subprocess.Popen(
                self.command,
                shell=self.__is_shell,
                env=self.__get_env(env),
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
            )
        except TypeError:
            proc = subprocess.Popen(
                self.command, shell=self.__is_shell, stdin=PIPE, stdout=PIPE, stderr=PIPE
            )

        self.__stdout, self.__stderr = proc.communicate(**kwargs)
        self.__returncode = proc.returncode

        self.__stdout = MultiByteStrDecoder(self.__stdout).unicode_str
        self.__stderr = MultiByteStrDecoder(self.__stderr).unicode_str

        if self.returncode == 0:
            return 0

        try:
            if (
                self.__ignore_stderr_regexp
                and self.__ignore_stderr_regexp.search(self.stderr) is not None
            ):
                return self.returncode
        except AttributeError:
            pass

        if check is True:
            # stdout and stderr attributes added since Python 3.5
            raise CalledProcessError(
                returncode=self.returncode,
                cmd=self.command_str,
                output=self.stdout,
                stderr=self.stderr,
            )

        # pytype: disable=attribute-error
        self.__error_logging_method(
            "command='{}', returncode={}, stderr={!r}".format(
                self.command, self.returncode, self.stderr
            )
        )
        # pytype: enable=attribute-error

        return self.returncode

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

    def __verify_command(self):
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

    def __debug_print_command(self):
        message_list = [self.command_str]

        if self.is_output_stacktrace:
            message_list.append("".join(traceback.format_stack()[:-2]))

        self.__debug_logging_method("\n".join(message_list))
