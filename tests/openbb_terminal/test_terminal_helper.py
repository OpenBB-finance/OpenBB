import sys
import unittest
from contextlib import contextmanager
from unittest.mock import patch
import pytest

from openbb_terminal import terminal_helper
from tests.helpers.helpers import check_print


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
    @check_print(length=0)
    def test_print_goodbye(self):
        terminal_helper.print_goodbye()

    @check_print(assert_in="Welcome to OpenBB Terminal")
    def test_welcome_message(self):
        terminal_helper.welcome_message()

    @check_print(assert_in="Unfortunately, resetting wasn't")
    @patch("subprocess.run", side_effect=return_val)
    def test_reset(self, mock):
        # pylint: disable=unused-argument
        terminal_helper.reset()


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "last_release, current_release",
    [
        ("v0.0.1", "v0.0.1"),
        ("v0.0.2", "v0.0.1"),
        ("v0.0.1", "v0.0.2"),
        ("v1.9.0", "v1.10.0"),
        ("v1.10.0", "v1.9.0"),
        ("xyz", "v1.9.0"),
        ("2.0.0", "2.0.0rc1"),
        ("2.0.0rc1", "2.0.0"),
        ("2.0.0rc1", "2.0.0rc2"),
        ("2.0.0rc2", "2.0.0rc1"),
        ("3.41.99", "88.123.456"),
        ("88.123.456", "3.41.99"),
        ("3.41.99", "3.41.99"),
        ("3.41.99", "3.41.99rc1"),
        ("8.10.01", "8.1.01"),
    ],
)
def test_check_for_updates(mocker, last_release, current_release):
    # MOCK GET
    attrs = {
        "status_code": 200,
        "json.return_value": {
            "url": "mock_url",
            "assets_url": "mock_url",
            "upload_url": "mock_url",
            "html_url": "mock_url",
            "node_id": "mock_node_id",
            "tag_name": last_release,
            "name": "mock_terminal_name",
        },
    }
    mock_response = mocker.Mock(**attrs)
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    # MOCK FF VERSION
    mocker.patch(
        target="openbb_terminal.feature_flags.VERSION",
        new=current_release,
    )

    terminal_helper.check_for_updates()
