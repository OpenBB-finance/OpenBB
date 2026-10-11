"""Queued commands must not leak internal placeholder tokens."""

from openbb_cli.controllers.utils import parse_and_split_input


def test_multiple_paths_in_one_queued_command():
    command = "load -f /tmp/first.csv --file /tmp/second.csv"
    assert parse_and_split_input(command + "/echo done", []) == [command, "echo done"]


def test_custom_protected_arguments_are_all_restored():
    command = "echo [first/path] [second/path]"
    assert parse_and_split_input(command + "/echo done", [r"\[[^\]]+\]"]) == [
        command,
        "echo done",
    ]
