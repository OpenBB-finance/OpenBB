import logging
import os

import pytest

from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def function_that_fails():
    raise ValueError("Failure")


def test_debug_false():
    os.environ["DEBUG_MODE"] = "false"
    function_that_fails()


def test_debug_true():
    os.environ["DEBUG_MODE"] = "true"
    with pytest.raises(ValueError):
        function_that_fails()
