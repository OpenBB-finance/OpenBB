"""Utilities for argparse_translator module."""

from argparse import Action, ArgumentParser


def in_group(parser: ArgumentParser, argument_name: str, group_title: str) -> bool:
    """Check if an argument is in a group of an ArgumentParser."""
    for action_group in parser._action_groups:
        if action_group.title == group_title:
            for action in action_group._group_actions:
                opts = action.option_strings
                if (opts and opts[0] == argument_name) or action.dest == argument_name:
                    return True
    return False


def remove_argument(parser: ArgumentParser, argument_name: str) -> list[str | None]:
    """Remove an argument from an ArgumentParser."""
    groups_w_arg = []
    action = next(
        (
            action
            for action in parser._actions
            if argument_name in action.option_strings or action.dest == argument_name
        ),
        None,
    )
    if action is None:
        return groups_w_arg
    parser._remove_action(action)
    for action_group in parser._action_groups:
        if action in action_group._group_actions:
            action_group._group_actions.remove(action)
            groups_w_arg.append(action_group.title)
    for option in action.option_strings:
        parser._option_string_actions.pop(option, None)
    for group in list(parser._mutually_exclusive_groups):
        if action in group._group_actions:
            group._group_actions.remove(action)
        if not group._group_actions:
            parser._mutually_exclusive_groups.remove(group)
    return groups_w_arg


def get_argument_choices(parser: ArgumentParser, argument_name: str) -> tuple:
    """Get the choices of an argument from an ArgumentParser."""
    for action in parser._actions:
        opts = action.option_strings
        if (opts and opts[0] == argument_name) or action.dest == argument_name:
            return tuple(action.choices or ())
    return ()


def get_argument_optional_choices(parser: ArgumentParser, argument_name: str) -> bool:
    """Get the optional_choices attribute of an argument from an ArgumentParser."""
    for action in parser._actions:
        opts = action.option_strings
        if (
            (opts and opts[0] == argument_name)
            or action.dest == argument_name
            and hasattr(action, "optional_choices")
        ):
            return action.optional_choices  # ty: ignore[unresolved-attribute]
    return False


def set_optional_choices(action: Action, optional_choices: bool):
    """Set the optional_choices attribute of an action."""
    if not hasattr(action, "optional_choices") and optional_choices:
        setattr(action, "optional_choices", optional_choices)
