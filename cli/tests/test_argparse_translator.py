"""Test the Argparse Translator."""

from argparse import ArgumentParser

import pytest
from openbb_cli.argparse_translator.argparse_argument import (
    ArgparseArgumentGroupModel,
    ArgparseArgumentModel,
)
from openbb_cli.argparse_translator.argparse_translator import (
    ArgparseTranslator,
)

# pylint: disable=protected-access


def test_custom_argument_action_validation():
    """Test that CustomArgument raises an error for invalid actions."""
    with pytest.raises(ValueError) as excinfo:
        ArgparseArgumentModel(
            name="test",
            type=bool,
            dest="test",
            default=False,
            required=True,
            action="store",
            help="Test argument",
            nargs=None,
            choices=None,
        )
    assert 'action must be "store_true"' in str(excinfo.value)


def test_custom_argument_remove_props_on_store_true():
    """Test that CustomArgument removes type, nargs, and choices on store_true."""
    argument = ArgparseArgumentModel(
        name="verbose",
        type=None,
        dest="verbose",
        default=None,
        required=False,
        action="store_true",
        help="Verbose output",
        nargs=None,
        choices=None,
    )
    assert argument.type is None
    assert argument.nargs is None
    assert argument.choices is None


def test_custom_argument_group():
    """Test the CustomArgumentGroup class."""
    args = [
        ArgparseArgumentModel(
            name="test",
            type=int,
            dest="test",
            default=1,
            required=True,
            action="store",
            help="Test argument",
            nargs=None,
            choices=None,
        )
    ]
    group = ArgparseArgumentGroupModel(name="Test Group", arguments=args)
    assert group.name == "Test Group"
    assert len(group.arguments) == 1
    assert group.arguments[0].name == "test"


def test_argparse_translator_setup():
    """Test the ArgparseTranslator setup."""

    def test_function(test_arg: int):
        """A test function."""
        return test_arg * 2

    translator = ArgparseTranslator(func=test_function)
    parser = translator.parser
    assert isinstance(parser, ArgumentParser)
    assert "--test_arg" in parser._option_string_actions


def test_argparse_translator_execution():
    """Test the ArgparseTranslator execution."""

    def test_function(test_arg: int) -> int:
        """A test function."""
        return test_arg * 2

    translator = ArgparseTranslator(func=test_function)
    parsed_args = translator.parser.parse_args(["--test_arg", "3"])
    result = translator.execute_func(parsed_args)
    assert result == 6
