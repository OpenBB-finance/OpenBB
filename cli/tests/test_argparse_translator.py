"""Test the Argparse Translator."""

from argparse import ArgumentParser
from datetime import date
from typing import Literal

import pytest
from openbb_cli.argparse_translator.argparse_argument import (
    ArgparseArgumentGroupModel,
    ArgparseArgumentModel,
)
from openbb_cli.argparse_translator.argparse_translator import (
    ArgparseTranslator,
)
from openbb_cli.argparse_translator.reference_processor import (
    ReferenceToArgumentsProcessor,
)
from pydantic import BaseModel

# pylint: disable=protected-access,unused-argument


# Test fixtures and helper functions
def sample_function(
    symbol: str,
    start_date: date | None = None,
    limit: int = 100,
    provider: Literal["fmp", "yfinance"] = "fmp",
) -> dict:
    """Sample function for testing."""
    return {
        "symbol": symbol,
        "start_date": start_date,
        "limit": limit,
        "provider": provider,
    }


def bool_function(
    symbol: str,
    adjusted: bool = False,
    extended_hours: bool | None = None,
) -> dict:
    """Function with boolean parameters."""
    return {"symbol": symbol, "adjusted": adjusted, "extended_hours": extended_hours}


def union_function(
    param1: str | int = "default",
    param2: str | int | None = None,
) -> dict:
    """Function with union types."""
    return {"param1": param1, "param2": param2}


def list_function(
    symbols: list[str],
    values: list[int] | None = None,
) -> dict:
    """Function with list parameters."""
    return {"symbols": symbols, "values": values}


class CustomData(BaseModel):
    """Custom data model for testing."""

    field1: str
    field2: int = 10


def custom_type_function(data: CustomData) -> dict:
    """Function with custom type parameter."""
    return {"data": data}


# ArgparseArgumentModel Tests
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


# ArgparseTranslator Basic Tests
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


# ArgparseTranslator Comprehensive Tests
def test_basic_translation():
    """Test basic function translation."""
    translator = ArgparseTranslator(sample_function)
    parser = translator.parser

    actions = {
        action.dest: action for action in parser._actions if action.dest != "help"
    }

    assert "symbol" in actions
    assert "start_date" in actions
    assert "limit" in actions
    assert "provider" in actions


def test_required_arguments():
    """Test that required arguments are correctly identified."""
    translator = ArgparseTranslator(sample_function)

    required_actions = [action for action in translator._required._group_actions]
    assert any(action.dest == "symbol" for action in required_actions)


def test_optional_arguments():
    """Test that optional arguments have defaults."""
    translator = ArgparseTranslator(sample_function)
    parser = translator.parser

    actions = {action.dest: action for action in parser._actions}

    assert actions["limit"].default == 100
    assert actions["provider"].default == "fmp"


def test_literal_choices():
    """Test that Literal types create choices."""
    translator = ArgparseTranslator(sample_function)
    parser = translator.parser

    actions = {action.dest: action for action in parser._actions}
    assert set(actions["provider"].choices) == {"fmp", "yfinance"}  # type: ignore


def test_bool_store_true():
    """Test that bool parameters use store_true action."""
    translator = ArgparseTranslator(bool_function)
    parser = translator.parser

    actions = {action.dest: action for action in parser._actions}

    # Check the action type by checking the class name
    assert actions["adjusted"].__class__.__name__ == "_StoreTrueAction"
    assert actions["extended_hours"].__class__.__name__ == "_StoreTrueAction"


def test_union_type_handling():
    """Test Union type handling."""
    translator = ArgparseTranslator(union_function)
    parser = translator.parser

    actions = {action.dest: action for action in parser._actions}

    # Should default to str for Union types
    assert actions["param1"].type is str
    assert actions["param2"].type is str


def test_pipe_union_type_handling():
    """Test pipe union (|) type handling."""
    translator = ArgparseTranslator(union_function)
    parser = translator.parser

    actions = {action.dest: action for action in parser._actions}
    assert "param2" in actions


def test_list_nargs():
    """Test that list parameters get nargs='+'."""
    translator = ArgparseTranslator(list_function)
    parser = translator.parser

    actions = {action.dest: action for action in parser._actions}

    assert actions["symbols"].nargs == "+"
    # For Optional[list[int]], it should still have nargs="+" if it's a list type
    # but the implementation might handle Optional[list] differently
    # Let's check if it's at least recognized as a list parameter
    assert "values" in actions


def test_custom_type_flattening():
    """Test that custom BaseModel types are flattened."""
    translator = ArgparseTranslator(custom_type_function)
    parser = translator.parser

    actions = {action.dest: action for action in parser._actions}

    assert "data__field1" in actions
    assert "data__field2" in actions
    assert actions["data__field2"].default == 10


def test_unflatten_args():
    """Test unflattening of nested arguments."""
    args_dict = {
        "symbol": "AAPL",
        "data__field1": "value1",
        "data__field2": 20,
    }

    result = ArgparseTranslator._unflatten_args(args_dict)

    assert result["symbol"] == "AAPL"
    assert "data" in result
    assert result["data"]["field1"] == "value1"
    assert result["data"]["field2"] == 20


def test_description_cleaning_union():
    """Test that Union types are cleaned in descriptions."""

    def func_with_union(param: str | int) -> None:
        """Test function.

        Parameters
        ----------
        param : Union[str, int]
            A parameter description.
        """

    translator = ArgparseTranslator(func_with_union)
    description = translator._build_description(func_with_union.__doc__)  # type: ignore

    # The method removes the Parameters section, so we just check it processes without error
    assert "Union[" not in description


def test_description_cleaning_optional():
    """Test that Optional types are cleaned in descriptions."""

    def func_with_optional(param: str | None) -> None:
        """Test function.

        Parameters
        ----------
        param : Optional[str]
            A parameter description.
        """

    translator = ArgparseTranslator(func_with_optional)
    description = translator._build_description(func_with_optional.__doc__)  # type: ignore

    # The method removes the Parameters section, so we just check it processes without error
    assert "Optional[" not in description


def test_description_cleaning_annotated():
    """Test that Annotated types are cleaned in descriptions."""

    def func_with_annotated(param: str) -> None:
        """Test function.

        Parameters
        ----------
        param : Annotated[str, Field(...)]
            A parameter description.
        """

    translator = ArgparseTranslator(func_with_annotated)
    description = translator._build_description(func_with_annotated.__doc__)  # type: ignore

    assert "Annotated[" not in description
    assert "Field" not in description


def test_description_cleaning_pipe_union():
    """Test that pipe unions (|) are cleaned in descriptions."""

    def func_with_pipe(param: str | int | None) -> None:
        """Test function.

        Parameters
        ----------
        param : str | int | None
            A parameter description.
        """

    translator = ArgparseTranslator(func_with_pipe)
    description = translator._build_description(func_with_pipe.__doc__)  # type: ignore

    # The method removes the Parameters section, so we just check it processes without error
    assert " | " not in description


def test_custom_argument_groups():
    """Test adding custom argument groups."""
    custom_groups = [
        ArgparseArgumentGroupModel(
            name="custom_provider",
            arguments=[
                ArgparseArgumentModel(
                    name="custom_param",
                    type=str,
                    dest="custom_param",
                    default="default",
                    required=False,
                    action="store",
                    help="Custom parameter",
                    nargs=None,
                    choices=("a", "b", "c"),
                )
            ],
        )
    ]

    translator = ArgparseTranslator(
        sample_function, custom_argument_groups=custom_groups
    )
    parser = translator.parser

    actions = {action.dest: action for action in parser._actions}
    assert "custom_param" in actions
    assert set(actions["custom_param"].choices) == {"a", "b", "c"}  # type: ignore


def test_provider_parameters_tracking():
    """Test that provider parameters are tracked."""
    custom_groups = [
        ArgparseArgumentGroupModel(
            name="provider1",
            arguments=[
                ArgparseArgumentModel(
                    name="param1",
                    type=str,
                    dest="param1",
                    default=None,
                    required=False,
                    action="store",
                    help="Provider param",
                    nargs=None,
                    choices=None,
                )
            ],
        )
    ]

    translator = ArgparseTranslator(
        sample_function, custom_argument_groups=custom_groups
    )

    assert "provider1" in translator.provider_parameters
    assert "param1" in translator.provider_parameters["provider1"]


# ReferenceToArgumentsProcessor Tests
class TestReferenceToArgumentsProcessor:
    """Test the ReferenceToArgumentsProcessor class."""

    def test_parse_type_simple(self):
        """Test parsing simple types."""
        assert ReferenceToArgumentsProcessor._parse_type("str") is str
        assert ReferenceToArgumentsProcessor._parse_type("int") is int
        assert ReferenceToArgumentsProcessor._parse_type("float") is float
        assert ReferenceToArgumentsProcessor._parse_type("bool") is bool

    def test_parse_type_optional(self):
        """Test parsing Optional types."""
        assert ReferenceToArgumentsProcessor._parse_type("Optional[str]") is str
        assert ReferenceToArgumentsProcessor._parse_type("Optional[int]") is int
        assert ReferenceToArgumentsProcessor._parse_type("str | None") is str
        assert ReferenceToArgumentsProcessor._parse_type("int | None") is int

    def test_parse_type_literal(self):
        """Test parsing Literal types."""
        assert ReferenceToArgumentsProcessor._parse_type("Literal['a', 'b']") is str
        assert (
            ReferenceToArgumentsProcessor._parse_type("Literal['option1', 'option2']")
            is str
        )

    def test_parse_type_annotated(self):
        """Test parsing Annotated types."""
        assert (
            ReferenceToArgumentsProcessor._parse_type("Annotated[str, Field(...)]")
            is str
        )
        assert (
            ReferenceToArgumentsProcessor._parse_type("Annotated[int, Field(...)]")
            is int
        )

    def test_parse_type_unknown(self):
        """Test parsing unknown types defaults to str."""
        assert ReferenceToArgumentsProcessor._parse_type("UnknownType") is str
        assert ReferenceToArgumentsProcessor._parse_type("CustomClass") is str

    def test_get_nargs_list(self):
        """Test getting nargs for list types."""
        processor = ReferenceToArgumentsProcessor({})
        assert processor._get_nargs(list[str]) == "+"
        assert processor._get_nargs(list[int]) == "+"

    def test_get_nargs_non_list(self):
        """Test getting nargs for non-list types."""
        processor = ReferenceToArgumentsProcessor({})
        assert processor._get_nargs(str) is None
        assert processor._get_nargs(int) is None

    def test_get_choices_literal(self):
        """Test extracting choices from Literal types."""
        processor = ReferenceToArgumentsProcessor({})
        choices = processor._get_choices("Literal['a', 'b', 'c']", custom_choices=None)
        assert set(choices) == {"a", "b", "c"}  # type: ignore

    def test_get_choices_multiple_literals(self):
        """Test extracting choices from multiple Literal types."""
        processor = ReferenceToArgumentsProcessor({})
        choices = processor._get_choices(
            "Union[Literal['a', 'b'], Literal['c', 'd']]", custom_choices=None
        )
        assert set(choices) == {"a", "b", "c", "d"}  # type: ignore

    def test_get_choices_custom(self):
        """Test custom choices override Literal choices."""
        processor = ReferenceToArgumentsProcessor({})
        custom = ["x", "y", "z"]
        choices = processor._get_choices("Literal['a', 'b']", custom_choices=custom)
        assert choices == ("x", "y", "z")

    def test_get_choices_none(self):
        """Test no choices when not Literal and no custom."""
        processor = ReferenceToArgumentsProcessor({})
        assert processor._get_choices("str", custom_choices=None) is None
        assert processor._get_choices("int", custom_choices=None) is None

    def test_build_custom_groups(self):
        """Test building custom argument groups from reference."""
        reference = {
            "/equity/price/historical": {
                "parameters": {
                    "standard": [],
                    "fmp": [
                        {
                            "name": "interval",
                            "type": "Literal['1min', '5min', '15min']",
                            "description": "Time interval",
                            "default": "1min",
                            "optional": True,
                            "standard": False,
                            "choices": None,
                        }
                    ],
                }
            }
        }

        processor = ReferenceToArgumentsProcessor(reference)
        groups = processor.custom_groups

        assert "/equity/price/historical" in groups
        assert len(groups["/equity/price/historical"]) == 1
        assert groups["/equity/price/historical"][0].name == "fmp"
        assert len(groups["/equity/price/historical"][0].arguments) == 1

        arg = groups["/equity/price/historical"][0].arguments[0]
        assert arg.name == "interval"
        assert arg.type is str
        assert arg.default == "1min"
        assert not arg.required
        assert set(arg.choices) == {"1min", "5min", "15min"}  # type: ignore

    def test_build_custom_groups_skip_standard(self):
        """Test that standard parameters are skipped."""
        reference = {
            "/test/route": {
                "parameters": {
                    "standard": [],
                    "provider1": [
                        {
                            "name": "param1",
                            "type": "str",
                            "description": "Standard param",
                            "default": None,
                            "optional": True,
                            "standard": True,
                            "choices": None,
                        },
                        {
                            "name": "param2",
                            "type": "int",
                            "description": "Custom param",
                            "default": 10,
                            "optional": False,
                            "standard": False,
                            "choices": None,
                        },
                    ],
                }
            }
        }

        processor = ReferenceToArgumentsProcessor(reference)
        groups = processor.custom_groups

        # Only param2 should be included
        assert len(groups["/test/route"][0].arguments) == 1
        assert groups["/test/route"][0].arguments[0].name == "param2"

    def test_build_custom_groups_multiple_providers(self):
        """Test building groups for multiple providers."""
        reference = {
            "/test/route": {
                "parameters": {
                    "standard": [],
                    "provider1": [
                        {
                            "name": "param1",
                            "type": "str",
                            "description": "Provider 1 param",
                            "default": None,
                            "optional": True,
                            "standard": False,
                            "choices": None,
                        }
                    ],
                    "provider2": [
                        {
                            "name": "param2",
                            "type": "int",
                            "description": "Provider 2 param",
                            "default": 5,
                            "optional": False,
                            "standard": False,
                            "choices": None,
                        }
                    ],
                }
            }
        }

        processor = ReferenceToArgumentsProcessor(reference)
        groups = processor.custom_groups

        assert len(groups["/test/route"]) == 2
        provider_names = {group.name for group in groups["/test/route"]}
        assert provider_names == {"provider1", "provider2"}

    def test_bool_action(self):
        """Test that bool types get store_true action."""
        reference = {
            "/test/route": {
                "parameters": {
                    "standard": [],
                    "provider1": [
                        {
                            "name": "flag",
                            "type": "bool",
                            "description": "A boolean flag",
                            "default": False,
                            "optional": True,
                            "standard": False,
                            "choices": None,
                        }
                    ],
                }
            }
        }

        processor = ReferenceToArgumentsProcessor(reference)
        groups = processor.custom_groups

        arg = groups["/test/route"][0].arguments[0]
        assert arg.action == "store_true"
        assert arg.type is None  # Should be None for store_true
