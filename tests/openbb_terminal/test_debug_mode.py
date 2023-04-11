import logging

import pytest

from openbb_terminal.core.session.current_system import set_system_variable
from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def function_that_fails():
    raise ValueError("Failure")


def test_debug_false():
    set_system_variable("DEBUG_MODE", False)
    function_that_fails()


def test_debug_true():
    set_system_variable("DEBUG_MODE", True)
    with pytest.raises(ValueError):
        function_that_fails()
