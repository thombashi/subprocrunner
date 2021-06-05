#!/usr/bin/env python3

from subprocrunner import Retry, SubprocessRunner, set_logger


set_logger(True)
SubprocessRunner("ls notexist").run(retry=Retry())
