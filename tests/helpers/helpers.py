import functools
import sys
import io
from typing import Union


def calc_change(current: Union[float, int], previous: Union[float, int]):
    """Calculates change between two different values"""
    if current == previous:
        return 0
    try:
        return ((current - previous) / previous) * 100.0
    except ZeroDivisionError:
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
