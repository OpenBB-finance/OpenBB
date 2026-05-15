"""Test the Controller utils."""

import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from openbb_cli.controllers.utils import (
    check_file_type_saved,
    check_non_negative,
    check_positive,
    get_flair_and_username,
    get_user_agent,
    parse_and_split_input,
    parse_unknown_args_to_dict,
    print_goodbye,
    remove_file,
    validate_register_key,
    welcome_message,
)

# pylint: disable=redefined-outer-name, unused-argument


@pytest.fixture
def mock_session():
    """Mock the session and its dependencies."""
    with patch("openbb_cli.controllers.utils.session") as mock_session:
        mock_session.console.print = MagicMock()
        mock_session.settings.VERSION = "1.0"
        mock_session.settings.FLAIR = "rocket"
        yield mock_session


def test_remove_file_existing_file():
    """Test removing an existing file."""
    with patch("os.path.isfile", return_value=True), patch("os.remove") as mock_remove:
        assert remove_file(Path("/path/to/file"))
        mock_remove.assert_called_once()


def test_remove_file_directory():
    """Test removing a directory."""
    with (
        patch("os.path.isfile", return_value=False),
        patch("os.path.isdir", return_value=True),
        patch("shutil.rmtree") as mock_rmtree,
    ):
        assert remove_file(Path("/path/to/directory"))
        mock_rmtree.assert_called_once()


def test_remove_file_failure(mock_session):
    """Test removing a file that fails."""
    with (
        patch("os.path.isfile", return_value=True),
        patch("os.remove", side_effect=Exception("Error")),
    ):
        assert not remove_file(Path("/path/to/file"))
        mock_session.console.print.assert_called()


def test_print_goodbye(mock_session):
    """Test printing the goodbye message."""
    print_goodbye()
    mock_session.console.print.assert_called()


def test_parse_and_split_input():
    """Test parsing and splitting user input."""
    user_input = "ls -f /home/user/docs/document.xlsx"
    result = parse_and_split_input(user_input, [])
    assert "ls" in result[0]


@pytest.mark.parametrize(
    "input_command, expected_output",
    [
        ("/", ["home"]),
        ("ls -f /path/to/file.txt", ["ls -f ", "path", "to", "file.txt"]),
        ("rm -f /home/user/docs", ["rm -f ", "home", "user", "docs"]),
    ],
)
def test_parse_and_split_input_special_cases(input_command, expected_output):
    """Test parsing and splitting user input with special cases."""
    result = parse_and_split_input(input_command, [])
    assert result == expected_output


def test_welcome_message(mock_session):
    """Test printing the welcome message."""
    welcome_message()
    mock_session.console.print.assert_called_with(
        "\nWelcome to OpenBB Platform CLI v1.0"
    )


def test_get_flair_and_username(mock_session):
    """Test getting the flair and username."""
    result = get_flair_and_username()
    assert "rocket" in result


@pytest.mark.parametrize(
    "value, expected",
    [
        ("10", 10),
        ("0", 0),
        ("-1", pytest.raises(argparse.ArgumentTypeError)),
        ("text", pytest.raises(ValueError)),
    ],
)
def test_check_non_negative(value, expected):
    """Test checking for a non-negative value."""
    if isinstance(expected, int):
        assert check_non_negative(value) == expected
    else:
        with expected:
            check_non_negative(value)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("1", 1),
        ("0", pytest.raises(argparse.ArgumentTypeError)),
        ("-1", pytest.raises(argparse.ArgumentTypeError)),
        ("text", pytest.raises(ValueError)),
    ],
)
def test_check_positive(value, expected):
    """Test checking for a positive value."""
    if isinstance(expected, int):
        assert check_positive(value) == expected
    else:
        with expected:
            check_positive(value)


def test_get_user_agent():
    """Test getting the user agent."""
    result = get_user_agent()
    assert result.startswith("Mozilla/5.0")


# --- Tests for parse_unknown_args_to_dict ---


@pytest.mark.parametrize(
    "args, expected",
    [
        (["--key", "value"], {"key": "value"}),
        (["--a", "1", "--b", "hello"], {"a": 1, "b": "hello"}),
        (["--flag"], {}),
        (None, {}),
        ([], {}),
    ],
)
def test_parse_unknown_args_to_dict_basic(args, expected, mock_session):
    """Test basic key-value parsing and edge cases."""
    result = parse_unknown_args_to_dict(args)
    assert result == expected


@pytest.mark.parametrize(
    "args, expected",
    [
        (["--num", "42"], {"num": 42}),
        (["--pi", "3.14"], {"pi": 3.14}),
        (["--items", "[1, 2, 3]"], {"items": [1, 2, 3]}),
        (["--mapping", "{'a': 1}"], {"mapping": {"a": 1}}),
        (["--bool", "True"], {"bool": True}),
        (["--plain", "not-a-literal"], {"plain": "not-a-literal"}),
    ],
)
def test_parse_unknown_args_to_dict_literal_eval(args, expected, mock_session):
    """Test that ast.literal_eval correctly parses typed values."""
    result = parse_unknown_args_to_dict(args)
    assert result == expected


def test_parse_unknown_args_to_dict_missing_value(mock_session):
    """Test that a trailing --flag with no value prints a warning."""
    result = parse_unknown_args_to_dict(["--orphan"])
    assert result == {}
    mock_session.console.print.assert_called_once()


# --- Tests for validate_register_key ---


@pytest.mark.parametrize(
    "key, should_raise",
    [
        ("my_api_key", False),
        ("secret_123", False),
        ("OBB_KEY", True),
        ("my_OBB_key", True),
        ("OBB", True),
    ],
)
def test_validate_register_key(key, should_raise):
    """Test that keys containing 'OBB' are rejected."""
    if should_raise:
        with pytest.raises(argparse.ArgumentTypeError, match="OBB"):
            validate_register_key(key)
    else:
        assert validate_register_key(key) == key


# --- Tests for check_file_type_saved ---


def test_check_file_type_saved_valid(mock_session):
    """Test valid filenames are accepted."""
    checker = check_file_type_saved(valid_types=[".csv", ".json"])
    assert checker("report.csv") == "report.csv"
    assert checker("data.json") == "data.json"
    assert checker("a.csv,b.json") == "a.csv,b.json"


def test_check_file_type_saved_invalid(mock_session):
    """Test invalid filenames are rejected with a warning."""
    checker = check_file_type_saved(valid_types=[".csv"])
    result = checker("report.xlsx")
    assert result == ""
    mock_session.console.print.assert_called()


def test_check_file_type_saved_empty(mock_session):
    """Test empty input returns empty string."""
    checker = check_file_type_saved(valid_types=[".csv"])
    assert checker("") == ""
    assert checker() == ""


def test_check_file_type_saved_no_valid_types(mock_session):
    """Test that None valid_types returns empty string."""
    checker = check_file_type_saved(valid_types=None)
    assert checker("anything.csv") == ""
