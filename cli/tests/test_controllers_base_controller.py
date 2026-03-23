"""Test the base controller."""

import argparse
from unittest.mock import MagicMock, patch

import pytest
from openbb_cli.controllers.base_controller import BaseController

# pylint: disable=unused-argument, unused-variable


class DummyBaseController(BaseController):
    """Testable Base Controller."""

    def __init__(self, queue=None):
        """Initialize the TestableBaseController."""
        self.PATH = "/valid/path/"
        super().__init__(queue=queue)

    def print_help(self):
        """Print help."""


def test_base_controller_initialization():
    """Test the initialization of the base controller."""
    with patch.object(DummyBaseController, "check_path", return_value=None):
        controller = DummyBaseController()
        assert controller.path == ["valid", "path"]  # Checking for correct path split


def test_path_validation():
    """Test the path validation method."""
    controller = DummyBaseController()

    with pytest.raises(ValueError):
        controller.PATH = "invalid/path"
        controller.check_path()

    with pytest.raises(ValueError):
        controller.PATH = "/invalid/path"
        controller.check_path()

    with pytest.raises(ValueError):
        controller.PATH = "/Invalid/Path/"
        controller.check_path()

    controller.PATH = "/valid/path/"


def test_parse_input():
    """Test the parse input method."""
    controller = DummyBaseController()
    input_str = "cmd1/cmd2/cmd3"
    expected = ["cmd1", "cmd2", "cmd3"]
    result = controller.parse_input(input_str)
    assert result == expected


def test_switch():
    """Test the switch method."""
    controller = DummyBaseController()
    with patch.object(controller, "call_exit", MagicMock()) as mock_exit:
        controller.queue = ["exit"]
        controller.switch("exit")
        mock_exit.assert_called_once()


def test_call_help():
    """Test the call help method."""
    controller = DummyBaseController()
    with patch("openbb_cli.controllers.base_controller.session.console.print"):
        controller.call_help(None)


def test_call_exit():
    """Test the call exit method."""
    controller = DummyBaseController()
    with patch.object(controller, "save_class", MagicMock()):
        controller.queue = ["quit"]
        controller.call_exit(None)


@pytest.fixture
def mock_base_session():
    """Mock the session for parse_known_args_and_warn tests."""
    with patch("openbb_cli.controllers.base_controller.session") as mock_session:
        mock_session.settings.USE_CLEAR_AFTER_CMD = False
        yield mock_session


def _make_parser(*args_spec):
    """Create an argparse parser from a list of add_argument kwargs."""
    parser = argparse.ArgumentParser(add_help=False)
    for spec in args_spec:
        flags = spec.pop("flags")
        parser.add_argument(*flags, **spec)
    return parser


def test_comma_split_flagged_value_not_split(mock_base_session):
    """Simple test: --symbol AAPL,MSFT must stay as one value."""
    parser = _make_parser({"flags": ["--symbol", "-s"], "dest": "symbol", "type": str})
    result = BaseController.parse_known_args_and_warn(parser, ["--symbol", "AAPL,MSFT"])
    assert result is not None
    assert result.symbol == "AAPL,MSFT"


def test_comma_split_short_flag_not_split(mock_base_session):
    """Short flag -s AAPL,MSFT must also stay as one value."""
    parser = _make_parser({"flags": ["--symbol", "-s"], "dest": "symbol", "type": str})
    result = BaseController.parse_known_args_and_warn(parser, ["-s", "AAPL,MSFT"])
    assert result is not None
    assert result.symbol == "AAPL,MSFT"


def test_comma_split_equals_syntax_not_split(mock_base_session):
    """--symbol=AAPL,MSFT must not be split."""
    parser = _make_parser({"flags": ["--symbol", "-s"], "dest": "symbol", "type": str})
    result = BaseController.parse_known_args_and_warn(parser, ["--symbol=AAPL,MSFT"])
    assert result is not None
    assert result.symbol == "AAPL,MSFT"


def test_comma_split_nargs_plus_all_values_protected(mock_base_session):
    """nargs='+': all consecutive values after --symbols are protected."""
    parser = _make_parser(
        {"flags": ["--symbols"], "dest": "symbols", "nargs": "+", "type": str}
    )
    result = BaseController.parse_known_args_and_warn(
        parser, ["--symbols", "AAPL,MSFT", "GOOG,AMZN"]
    )
    assert result is not None
    assert result.symbols == ["AAPL,MSFT", "GOOG,AMZN"]


def test_comma_split_nargs_star_values_protected(mock_base_session):
    """nargs='*': consecutive values after --tags are protected."""
    parser = _make_parser(
        {"flags": ["--tags"], "dest": "tags", "nargs": "*", "type": str}
    )
    result = BaseController.parse_known_args_and_warn(parser, ["--tags", "a,b", "c,d"])
    assert result is not None
    assert result.tags == ["a,b", "c,d"]


def test_comma_split_nargs_int_values_protected(mock_base_session):
    """nargs=2: both values after --pair are protected."""
    parser = _make_parser(
        {"flags": ["--pair"], "dest": "pair", "nargs": 2, "type": str}
    )
    result = BaseController.parse_known_args_and_warn(parser, ["--pair", "a,b", "c,d"])
    assert result is not None
    assert result.pair == ["a,b", "c,d"]


def test_comma_split_store_true_not_confused(mock_base_session):
    """store_true flags (nargs=0) should not protect the next token."""
    parser = _make_parser(
        {"flags": ["--symbol", "-s"], "dest": "symbol", "type": str},
        {"flags": ["--raw"], "dest": "raw", "action": "store_true", "default": False},
    )
    result = BaseController.parse_known_args_and_warn(
        parser, ["--raw", "--symbol", "AAPL,MSFT"]
    )
    assert result is not None
    assert result.raw is True
    assert result.symbol == "AAPL,MSFT"


def test_comma_split_no_comma_values_unchanged(mock_base_session):
    """Values without commas pass through unaffected."""
    parser = _make_parser({"flags": ["--symbol", "-s"], "dest": "symbol", "type": str})
    result = BaseController.parse_known_args_and_warn(parser, ["--symbol", "AAPL"])
    assert result is not None
    assert result.symbol == "AAPL"


def test_comma_split_multiple_flags_each_protected(mock_base_session):
    """Multiple flags each protect their own values independently."""
    parser = _make_parser(
        {"flags": ["--symbol", "-s"], "dest": "symbol", "type": str},
        {"flags": ["--raw"], "dest": "raw", "action": "store_true", "default": False},
        {"flags": ["--provider"], "dest": "provider", "type": str},
    )
    result = BaseController.parse_known_args_and_warn(
        parser,
        ["--symbol", "AAPL,MSFT", "--provider", "yfinance,polygon"],
    )
    assert result is not None
    assert result.symbol == "AAPL,MSFT"
    assert result.provider == "yfinance,polygon"
