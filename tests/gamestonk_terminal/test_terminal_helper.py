import sys
import unittest
from contextlib import contextmanager
from unittest.mock import patch

import vcr

from gamestonk_terminal import terminal_helper
from tests.helpers import check_print


def return_val(x, shell, check):
    # pylint: disable=unused-argument
    # pylint: disable=R0903
    class ReturnVal:
        def __init__(self, code):
            self.returncode = code

    return ReturnVal(2)


@contextmanager
def replace_stdin(target):
    orig = sys.stdin
    sys.stdin = target
    yield
    sys.stdin = orig


class TestMainHelper(unittest.TestCase):
    @check_print(assert_in="ALPHA")
    @vcr.use_cassette(
        "tests/gamestonk_terminal/cassettes/test_terminal_helper/test_check_api_keys.yaml",
        record_mode="new_episodes",
    )
    def test_check_api_keys(self):
        terminal_helper.check_api_keys()

    @check_print(length=0)
    def test_print_goodbye(self):
        terminal_helper.print_goodbye()

    @patch("subprocess.run", side_effect=return_val)
    def test_update_terminal(self, mock):
        # pylint: disable=unused-argument
        value = terminal_helper.update_terminal()
        self.assertEqual(value, 2)

    @check_print(assert_in="Thanks for using Gamestonk Terminal.")
    def test_about_us(self):
        terminal_helper.about_us()

    @check_print(assert_in="Welcome to Gamestonk Terminal Beta")
    def test_bootup(self):
        terminal_helper.bootup()

    @check_print(assert_in="Unfortunately, resetting wasn't")
    @patch("subprocess.run", side_effect=return_val)
    def test_reset(self, mock):
        # pylint: disable=unused-argument
        terminal_helper.reset()
