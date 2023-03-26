"""Backoff decorators."""

import logging
from functools import wraps
from time import sleep
from typing import Any, Tuple

logger = logging.getLogger(__name__)


def compute_delay(
    start_sleep_time: float,
    factor: float,
    border_sleep_time: float,
    delay: float,
    retry: int,
) -> Tuple[int, float]:
    """Compute delay for the next itteration.
     Args:
        start_sleep_time: Initial time to repeat.
        factor: Multiplier of time.
        border_sleep_time: Max time.
        delay: Last delay.
        retry: Number of the itteration.
    Returns:
        Tuple[int, float]: Tuple calculated retry and delay.
    """
    if delay < border_sleep_time:
        delay = start_sleep_time * (factor ** retry)
    return retry + 1, delay


def backoff_method(start_sleep_time: float = 0.1, factor: int = 2,
                   border_sleep_time: int = 10, max_retries: int = None) -> Any:
    """Retry with reconnect and delay.
    The function tries to call an argument function after reconnect and delay if the argument
    function caused an exception.
    Args:
        start_sleep_time: Initial time to repeat.
        factor: Multiplier of time.
        border_sleep_time: Max time.
        max_retries: Max number of tries.
    Returns:
        Any: Result of calling function.
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            retry = 1
            delay = start_sleep_time
            while True:
                try:
                    return func(self, *args, **kwargs)
                except Exception as err:
                    logger.exception(
                        'Error in {func}. Next try in {sec} seconds'.format(
                            sec=min(delay, border_sleep_time),
                            func=str(func),
                        ),
                    )
                    if max_retries and retry >= max_retries:
                        raise err
                    sleep(min(delay, border_sleep_time))
                    retry, delay = compute_delay(
                        start_sleep_time=start_sleep_time,
                        factor=factor,
                        border_sleep_time=border_sleep_time,
                        delay=delay,
                        retry=retry,
                    )
        return inner
    return func_wrapper
