import logging
import os

import pytest

from openbb_terminal.decorators import log_start_end
from openbb_terminal.core.exceptions.exceptions import (
    handle_exception,
    OpenBBUserError,
    shout,
)

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def function_that_raises(error_type: str, debug_mode: str):
    os.environ["DEBUG_MODE"] = debug_mode
    if error_type == "shout":
        shout("User failure")
    if error_type == "Exception":
        raise Exception("Bug failure")
    if error_type == "ValueError":
        raise ValueError("Value failure")


@pytest.mark.record_stdout
def test_OpenBBUserError():
    with pytest.raises(OpenBBUserError) as e:
        function_that_raises(error_type="shout", debug_mode="false")
    handle_exception(e.value)


@pytest.mark.record_stdout
def test_Exception_debug_false():
    with pytest.raises(Exception) as e:
        function_that_raises(error_type="Exception", debug_mode="false")
    handle_exception(e.value)


def test_Exception_debug_true():
    with pytest.raises(Exception) as e:
        function_that_raises(error_type="Exception", debug_mode="true")

    # In debug mode, external (i.e. not OpenBBUserError) exceptions are not caught
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

    # In debug mode, external (i.e. not OpenBBuserError) exceptions are not caught
    with pytest.raises(ValueError):
        handle_exception(e.value)
