import time
from random import uniform
from typing import Callable, Optional


class Retry:
    def __init__(
        self, total: int = 3, backoff_factor: float = 0.2, jitter: float = 0.2, quiet: bool = False
    ) -> None:
        self.total = total
        self.__backoff_factor = backoff_factor
        self.__jitter = jitter
        self.__quiet = quiet

        if self.total <= 0:
            raise ValueError("total must be greater than zero")

        if self.__backoff_factor <= 0:
            raise ValueError("backoff_factor must be greater than zero")

        if self.__jitter <= 0:
            raise ValueError("jitter must be greater than zero")

    def calc_backoff_time(self, attempt: int) -> float:
        sleep_duration = self.__backoff_factor * (2 ** max(0, attempt - 1))
        sleep_duration += uniform(0.5 * self.__jitter, 1.5 * self.__jitter)

        return sleep_duration

    def sleep_before_retry(
        self,
        attempt: int,
        logging_method: Optional[Callable] = None,
        retry_target: Optional[str] = None,
    ) -> float:
        sleep_duration = self.calc_backoff_time(attempt)

        if logging_method and not self.__quiet:
            if retry_target:
                msg = "Retrying '{}' in ".format(retry_target)
            else:
                msg = "Retrying in "

            msg += "{:.2f} seconds ... (attempt={}/{})".format(sleep_duration, attempt, self.total)

            logging_method(msg)

        time.sleep(sleep_duration)

        return sleep_duration
