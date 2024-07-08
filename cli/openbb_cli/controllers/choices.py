"""This module contains functions to build the choice map for the controllers."""

from argparse import SUPPRESS, ArgumentParser
from contextlib import contextmanager
from inspect import isfunction, unwrap
from types import MethodType
from typing import Callable, List, Literal, Tuple
from unittest.mock import patch

from openbb_cli.controllers.utils import (
    check_file_type_saved,
    check_positive,
    validate_register_key,
)
from openbb_cli.session import Session

session = Session()


def __mock_parse_known_args_and_warn(
    controller,  # pylint: disable=unused-argument
    parser: ArgumentParser,
    other_args: List[str],
    export_allowed: Literal[
        "no_export", "raw_data_only", "figures_only", "raw_data_and_figures"
    ] = "no_export",
    raw: bool = False,
    limit: int = 0,
) -> None:
    """Add arguments.

    Add the arguments that would have normally added by :
        - openbb_cli.base_controller.BaseController.parse_known_args_and_warn

    Parameters
    ----------
    parser: argparse.ArgumentParser
        Parser with predefined arguments
    other_args: List[str]
        list of arguments to parse
    export_allowed: Literal["no_export", "raw_data_only", "figures_only", "raw_data_and_figures"]
            Export options
    raw: bool
        Add the --raw flag
    limit: int
        Add a --limit flag with this number default
    """
    _ = other_args

    parser.add_argument(
        "-h", "--help", action="store_true", help="show this help message"
    )

    if export_allowed != "no_export":
        choices_export = []
        help_export = "Does not export!"

        if export_allowed == "raw_data_only":
            choices_export = ["csv", "json", "xlsx"]
            help_export = "Export raw data into csv, json or xlsx."
        elif export_allowed == "figures_only":
            choices_export = ["png", "jpg"]
            help_export = "Export figure into png or jpg."
        else:
            choices_export = ["csv", "json", "xlsx", "png", "jpg"]
            help_export = (
                "Export raw data into csv, json, xlsx and figure into png or jpg."
            )

        parser.add_argument(
            "--export",
            default="",
            type=check_file_type_saved(choices_export),
            dest="export",
            help=help_export,
            choices=choices_export,
        )

    if raw:
        parser.add_argument(
            "--raw",
            dest="raw",
            action="store_true",
            default=False,
            help="Flag to display raw data",
        )
    if limit > 0:
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            default=limit,
            help="Number of entries to show in data.",
            type=check_positive,
        )

    parser.add_argument(
        "--register_obbject",
        dest="register_obbject",
        action="store_false",
        default=True,
        help="Flag to store data in the OBBject registry, True by default.",
    )
    parser.add_argument(
        "--register_key",
        dest="register_key",
        default="",
        help="Key to reference data in the OBBject registry.",
        type=validate_register_key,
    )


def __mock_parse_simple_args(parser: ArgumentParser, other_args: List[str]) -> Tuple:
    """Add arguments.

    Add the arguments that would have normally added by:
        - openbb_cli.parent_classes.BaseController.parse_simple_args

    Parameters
    ----------
    parser: argparse.ArgumentParser
        Parser with predefined arguments
    other_args: List[str]
        List of arguments to parse
    """
    parser.add_argument(
        "-h", "--help", action="store_true", help="show this help message"
    )
    _ = other_args
    return None, None


def __get_command_func(controller, command: str):
    """Get the function with the name `f"call_{command}"` from controller object.

    Parameters
    ----------
    controller: BaseController
        Instance of the CLI Controller.
    command: str
        A name from controller.CHOICES_COMMANDS

    Returns
    -------
    Callable: Command function.
    """
    if command not in controller.CHOICES_COMMANDS:
        raise AttributeError(
            f"The following command is not inside `CHOICES_COMMANDS` : '{command}'"
        )

    command = f"call_{command}"
    command_func = getattr(controller, command)
    command_func = unwrap(func=command_func)

    if isfunction(command_func):
        command_func = MethodType(command_func, controller)

    return command_func


def contains_functions_to_patch(command_func: Callable) -> bool:
    """Check command function.

    Check if a `command_func` actually contains the functions we want to mock, i.e.:
        - parse_simple_args
        - parse_known_args_and_warn

    Parameters
    ----------
    command_func: Callable
        Function to check.

    Returns
    -------
    bool: Whether or not `command_func` contains the mocked functions.
    """
    co_names = command_func.__code__.co_names

    return bool(
        "parse_simple_args" in co_names or "parse_known_args_and_warn" in co_names
    )


@contextmanager
def __patch_controller_functions(controller):
    """Patch controller functions.

    Patch the following function from a BaseController instance:
        - parse_simple_args
        - parse_known_args_and_warn

    These functions take an 'argparse.ArgumentParser' object as parameter.
    We want to intercept this 'argparse.ArgumentParser' object.

    Parameters
    ----------
    controller: BaseController
        BaseController object that needs to be patched.

    Returns
    -------
    List[Callable]: List of mocked functions.
    """
    bound_mock_parse_known_args_and_warn = MethodType(
        __mock_parse_known_args_and_warn,
        controller,
    )

    rich = patch(
        target="openbb_cli.config.console.Console.print",
        return_value=None,
    )

    patcher_list = [
        patch.object(
            target=controller,
            attribute="parse_simple_args",
            side_effect=__mock_parse_simple_args,
            return_value=(None, None),
        ),
        patch.object(
            target=controller,
            attribute="parse_known_args_and_warn",
            side_effect=bound_mock_parse_known_args_and_warn,
            return_value=None,
        ),
    ]

    if not session.settings.DEBUG_MODE:
        rich.start()
    patched_function_list = []
    for patcher in patcher_list:
        patched_function_list.append(patcher.start())

    yield patched_function_list

    if not session.settings.DEBUG_MODE:
        rich.stop()
    for patcher in patcher_list:
        patcher.stop()


def _get_argument_parser(
    controller,
    command: str,
) -> ArgumentParser:
    """Intercept the ArgumentParser instance from the command function.

    A command function being a function starting with `call_`, like:
        - call_help
        - call_overview
        - call_load

    Parameters
    ----------
    controller: BaseController
        Instance of the CLI Controller.
    command: str
        A name from `controller.CHOICES_COMMANDS`.

    Returns
    -------
    ArgumentParser: ArgumentParser instance from the command function.
    """
    command_func: Callable = __get_command_func(controller=controller, command=command)

    if not contains_functions_to_patch(command_func=command_func):
        raise AssertionError(
            f"One of these functions should be inside `call_{command}`:\n"
            " - parse_simple_args\n"
            " - parse_known_args_and_warn\n"
        )

    with __patch_controller_functions(controller=controller) as patched_function_list:
        command_func([])

        call_count = 0
        for patched_function in patched_function_list:
            call_count += patched_function.call_count
            if patched_function.call_count == 1:
                args, kwargs = patched_function.call_args
                argument_parser = (
                    kwargs["parser"] if kwargs.get("parser", None) else args[0]
                )

        if call_count != 1:
            raise AssertionError(
                f"One of these functions should be called once inside `call_{command}`:\n"
                " - parse_simple_args\n"
                " - parse_known_args_and_warn\n"
            )

    # pylint: disable=possibly-used-before-assignment
    return argument_parser


def _build_command_choice_map(argument_parser: ArgumentParser) -> dict:
    """Build the choice map for a command."""
    choice_map: dict = {}
    for action in argument_parser._actions:  # pylint: disable=protected-access
        if action.help == SUPPRESS:
            continue
        if len(action.option_strings) == 1:
            long_name = action.option_strings[0]
            short_name = ""
        elif len(action.option_strings) == 2:
            short_name = action.option_strings[0]
            long_name = action.option_strings[1]
        else:
            raise AttributeError(f"Invalid argument_parser: {argument_parser}")

        if hasattr(action, "choices") and action.choices:
            choice_map[long_name] = {str(c): {} for c in action.choices}
        else:
            choice_map[long_name] = {}

        if short_name and long_name:
            choice_map[short_name] = long_name

    return choice_map


def build_controller_choice_map(controller) -> dict:
    """Build the choice map for a controller."""
    command_list = controller.CHOICES_COMMANDS
    controller_choice_map: dict = {c: {} for c in controller.controller_choices}

    for command in command_list:
        try:
            argument_parser = _get_argument_parser(
                controller=controller,
                command=command,
            )
            controller_choice_map[command] = _build_command_choice_map(
                argument_parser=argument_parser
            )
        except Exception as exception:
            if session.settings.DEBUG_MODE:
                raise Exception(
                    f"On command : `{command}`.\n{str(exception)}"
                ) from exception

    return controller_choice_map
