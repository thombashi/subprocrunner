import pytest

from subprocrunner.retry import Retry


class Test_Retry_repr:
    def test_normal(self):
        assert (
            str(Retry(backoff_factor=0.5, jitter=0.5))
            == "Retry(total=3, backoff-factor=0.5, jitter=0.5)"
        )


class Test_Retry_calc_backoff_time:
    @pytest.mark.parametrize(
        ["attempt"],
        [
            [0],
            [1],
            [2],
            [3],
            [4],
        ],
    )
    def test_normal(self, attempt):
        LOOP = 100
        coef = 2 ** max(0, attempt - 1)
        backoff_factor = 1
        jitter = 0.5
        base_time = backoff_factor * coef
        retry = Retry(backoff_factor=backoff_factor, jitter=jitter)

        for _i in range(LOOP):
            assert (
                (base_time - jitter * 0.5)
                <= retry.calc_backoff_time(attempt=attempt)
                <= (base_time + jitter * 1.5)
            )


class Test_Retry_sleep_before_retry:
    def test_normal(self):
        attempt = 1
        coef = 2 ** max(0, attempt - 1)
        backoff_factor = 0.1
        jitter = 0.1
        base_time = backoff_factor * coef
        retry = Retry(backoff_factor=backoff_factor, jitter=jitter)

        assert (
            (base_time - jitter * 0.5)
            <= retry.sleep_before_retry(attempt=attempt)
            <= (base_time + jitter * 1.5)
        )
