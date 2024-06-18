"""Utilities for argparse_translator module."""

from argparse import Action, ArgumentParser
from typing import List, Optional, Tuple


def in_group(parser: ArgumentParser, argument_name: str, group_title: str) -> bool:
    """Check if an argument is in a group of an ArgumentParser."""
    for action_group in parser._action_groups:  # pylint: disable=protected-access
        if action_group.title == group_title:
            for (
                action
            ) in action_group._group_actions:  # pylint: disable=protected-access
                opts = action.option_strings
                if (opts and opts[0] == argument_name) or action.dest == argument_name:
                    return True
    return False


def remove_argument(parser: ArgumentParser, argument_name: str) -> List[Optional[str]]:
    """Remove an argument from an ArgumentParser."""
    groups_w_arg = []

    # remove the argument from the parser
    for action in parser._actions:  # pylint: disable=protected-access
        opts = action.option_strings
        if (opts and opts[0] == argument_name) or action.dest == argument_name:
            parser._remove_action(action)  # pylint: disable=protected-access
            break

    # remove from all groups
    for action_group in parser._action_groups:  # pylint: disable=protected-access
        for action in action_group._group_actions:  # pylint: disable=protected-access
            opts = action.option_strings
            if (opts and opts[0] == argument_name) or action.dest == argument_name:
                action_group._group_actions.remove(  # pylint: disable=protected-access
                    action
                )
                groups_w_arg.append(action_group.title)

    # remove from _action_groups dict
    parser._option_string_actions.pop(  # pylint: disable=protected-access
        f"--{argument_name}", None
    )

    return groups_w_arg


def get_argument_choices(parser: ArgumentParser, argument_name: str) -> Tuple:
    """Get the choices of an argument from an ArgumentParser."""
    for action in parser._actions:  # pylint: disable=protected-access
        opts = action.option_strings
        if (opts and opts[0] == argument_name) or action.dest == argument_name:
            return tuple(action.choices or ())
    return ()


def get_argument_optional_choices(parser: ArgumentParser, argument_name: str) -> bool:
    """Get the optional_choices attribute of an argument from an ArgumentParser."""
    for action in parser._actions:  # pylint: disable=protected-access
        opts = action.option_strings
        if (
            (opts and opts[0] == argument_name)
            or action.dest == argument_name
            and hasattr(action, "optional_choices")
        ):
            return (
                action.optional_choices  # type: ignore[attr-defined] # this is a custom attribute
            )
    return False


def set_optional_choices(action: Action, optional_choices: bool):
    """Set the optional_choices attribute of an action."""
    if not hasattr(action, "optional_choices") and optional_choices:
        setattr(action, "optional_choices", optional_choices)
