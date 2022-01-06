import functools
import sys
import io


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
