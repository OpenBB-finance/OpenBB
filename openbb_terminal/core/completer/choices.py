from argparse import ArgumentParser
from inspect import unwrap
from os import environ
from types import MethodType
from typing import List
from unittest.mock import patch
from openbb_terminal.helper_funcs import check_file_type_saved, check_positive
from openbb_terminal.rich_config import get_ordered_list_sources


def __mock_parse_known_args_and_warn(
    controller,
    parser: ArgumentParser,
    other_args: List[str],
    export_allowed: int = 0,
    raw: bool = False,
    limit: int = 0,
) -> None:
    """Add the arguments that would have normally added by `parse_known_args_and_warn`.

    Parameters
    ----------
    parser: argparse.ArgumentParser
        Parser with predefined arguments
    other_args: List[str]
        list of arguments to parse
    export_allowed: int
        Choose from 0, 1,
        2 and EXPORT_BOTH_RAW_DATA_AND_FIGURES
    raw: bool
        Add the --raw flag
    limit: int
        Add a --limit flag with this number default
    """

    _ = other_args
    parser.add_argument(
        "-h", "--help", action="store_true", help="show this help message"
    )
    if export_allowed > 0:
        choices_export = []
        help_export = "Does not export!"

        if export_allowed == 1:
            choices_export = ["csv", "json", "xlsx"]
            help_export = "Export raw data into csv, json, xlsx"
        elif export_allowed == 2:
            choices_export = ["png", "jpg", "pdf", "svg"]
            help_export = "Export figure into png, jpg, pdf, svg "
        else:
            choices_export = ["csv", "json", "xlsx", "png", "jpg", "pdf", "svg"]
            help_export = "Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg "

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
    sources = get_ordered_list_sources(f"{controller.PATH}{parser.prog}")
    # Allow to change source if there is more than one
    if len(sources) > 1:
        parser.add_argument(
            "--source",
            action="store",
            dest="source",
            choices=sources,
            default=sources[0],  # the first source from the list is the default
            help="Data source to select from",
        )
    return None


def __mock_parse_simple_args(parser: ArgumentParser, other_args: List[str]) -> None:
    parser.add_argument(
        "-h", "--help", action="store_true", help="show this help message"
    )
    _ = other_args

    return None


def _get_argument_parser(
    controller,
    command: str,
) -> ArgumentParser:
    """Intercept the ArgumentParser instance from the command function.

    A command function being a function like : call_help, call_overview

    Args:
        controller (BaseController): Instance of the Terminal Controller.
        command (str): A name from controller.CHOICES_COMMANDS

    Returns:
        ArgumentParser: ArgumentParser instance from the command function.
    """

    if command not in controller.CHOICES_COMMANDS:
        raise AttributeError(f"Invalid command : '{command}'")

    bound_mock_parse_known_args_and_warn = MethodType(
        __mock_parse_known_args_and_warn, controller
    )

    patch_parse_simple_args = patch(
        target="openbb_terminal.helper_funcs.parse_simple_args",
        side_effect=__mock_parse_simple_args,
        return_value=None,
    )
    patch_parse_known_args_and_warn = patch.object(
        target=controller,
        attribute="parse_known_args_and_warn",
        side_effect=bound_mock_parse_known_args_and_warn,
        return_value=None,
    )

    parse_simple_args = patch_parse_simple_args.start()
    parse_known_args_and_warn = patch_parse_known_args_and_warn.start()

    command = "call_" + command
    command_func = getattr(controller, command)
    command_func = unwrap(command_func)
    command_func(controller, [])

    if parse_known_args_and_warn.call_count == 1:
        args = parse_known_args_and_warn.call_args.args
        argument_parser = args[0]
    elif parse_simple_args.call_count == 1:
        args = parse_simple_args.call_args.args
        argument_parser = args[0]
    else:
        raise AssertionError(
            "One of these functions should be called once:\n"
            " - parse_known_args_and_warn\n"
            " - parse_known_args_and_warn\n"
        )

    patch_parse_simple_args.stop()
    patch_parse_known_args_and_warn.stop()

    return argument_parser


def _build_command_choice_map(argument_parser: ArgumentParser) -> dict:
    choice_map: dict = {}
    for action in argument_parser._actions:  # pylint: disable=protected-access
        if len(action.option_strings) == 1:
            long_name = action.option_strings[0]
            short_name = ""
        elif len(action.option_strings) == 2:
            short_name = action.option_strings[0]
            long_name = action.option_strings[1]
        else:
            raise AttributeError(f"Invalid argument_parser: {argument_parser}")

        if action.choices:
            choice_map[long_name] = {c: {} for c in action.choices}
        else:
            choice_map[long_name] = {}

        if short_name and long_name:
            choice_map[short_name] = long_name

    return choice_map


def build_controller_choice_map(controller) -> dict:
    command_list = controller.CHOICES_COMMANDS
    controller_choice_map: dict = {c: {} for c in controller.controller_choices}
    controller_choice_map["support"] = controller.SUPPORT_CHOICES
    controller_choice_map["about"] = controller.ABOUT_CHOICES

    try:
        for command in command_list:
            argument_parser = _get_argument_parser(
                controller=controller,
                command=command,
            )
            controller_choice_map[command] = _build_command_choice_map(
                argument_parser=argument_parser
            )
    except Exception as exception:
        if environ["DEBUG_MODE"] == "true":
            raise exception

    return controller_choice_map
