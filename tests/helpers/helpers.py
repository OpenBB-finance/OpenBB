import functools
import io
import logging
import sys
from typing import Union

logger = logging.getLogger(__name__)


def calc_change(current: Union[float, int], previous: Union[float, int]):
    """Calculates change between two different values"""
    if current == previous:
        return 0
    try:
        return ((current - previous) / previous) * 100.0
    except ZeroDivisionError:
        logging.exception("zero division")
        return float("inf")


def check_print(assert_in: str = "", length: int = -1):
    """Captures output of print function and checks if the function contains a given string"""

    def checker(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            capturedOutput = io.StringIO()
            sys.stdout = capturedOutput
            func(*args, **kwargs)
            sys.stdout = sys.__stdout__
            capt = capturedOutput.getvalue()
            if assert_in:
                assert assert_in in capt
                return None
            if length >= 0:
                assert len(capt) > length
            return capt

        return wrapper

    return checker
