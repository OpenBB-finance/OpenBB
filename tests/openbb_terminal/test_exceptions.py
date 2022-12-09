import logging
import os

import pytest

from openbb_terminal.decorators import log_start_end
from openbb_terminal.core.exceptions.exceptions import (
    OpenBBBaseError,
    handle_exception,
    OpenBBAPIError,
    OpenBBUserError,
)

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def function_that_raises(error_type: str, debug_mode: str):
    os.environ["DEBUG_MODE"] = debug_mode
    if error_type == "OpenBBUserError":
        raise OpenBBUserError("User failure")
    elif error_type == "OpenBBAPIError":
        raise OpenBBAPIError("API failure")
    elif error_type == "OpenBBBaseError":
        raise OpenBBBaseError("Base failure")
    elif error_type == "Exception":
        raise Exception("Bug failure")
    elif error_type == "ValueError":
        raise ValueError("Value failure")


@pytest.mark.record_stdout
def test_OpenBBUserError():
    with pytest.raises(OpenBBUserError) as e:
        function_that_raises(error_type="OpenBBUserError", debug_mode="false")
    handle_exception(e.value)


@pytest.mark.record_stdout
def test_OpenBBAPIError():
    with pytest.raises(OpenBBAPIError) as e:
        function_that_raises(error_type="OpenBBAPIError", debug_mode="false")
    handle_exception(e.value)


@pytest.mark.record_stdout
def test_OpenBBBaseError():
    with pytest.raises(OpenBBBaseError) as e:
        function_that_raises(error_type="OpenBBBaseError", debug_mode="false")
    handle_exception(e.value)


@pytest.mark.record_stdout
def test_Exception_debug_false():
    with pytest.raises(Exception) as e:
        function_that_raises(error_type="Exception", debug_mode="false")
    handle_exception(e.value)


def test_Exception_debug_true():
    with pytest.raises(Exception) as e:
        function_that_raises(error_type="Exception", debug_mode="true")

    # In debug mode, built-in exceptions are not caught
    with pytest.raises(Exception):
        handle_exception(e.value)


@pytest.mark.record_stdout
def test_ValueError_debug_false():
    with pytest.raises(ValueError) as e:
        function_that_raises(error_type="ValueError", debug_mode="false")
    handle_exception(e.value)


def test_ValueError_debug_true():
    with pytest.raises(ValueError) as e:
        function_that_raises(error_type="ValueError", debug_mode="true")

    # In debug mode, built-in exceptions are not caught
    with pytest.raises(ValueError):
        handle_exception(e.value)


if __name__ == "__main__":
    test_OpenBBUserError()
