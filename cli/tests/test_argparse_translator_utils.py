"""Tests for argparse_translator/utils.py utility functions."""

import argparse

import pytest

from openbb_cli.argparse_translator.utils import (
    get_argument_choices,
    get_argument_optional_choices,
    in_group,
    remove_argument,
    set_optional_choices,
)


def _make_parser_with_groups():
    """Build a parser with a custom group for testing."""
    parser = argparse.ArgumentParser()
    group = parser.add_argument_group("provider")
    group.add_argument("--alpha", type=str, default="a")
    group.add_argument("--beta", type=int, default=0)
    parser.add_argument("--gamma", type=float, default=1.0)
    return parser


class TestInGroup:
    def test_argument_in_group(self):
        parser = _make_parser_with_groups()
        assert in_group(parser, "--alpha", "provider") is True

    def test_argument_not_in_group(self):
        parser = _make_parser_with_groups()
        assert in_group(parser, "--gamma", "provider") is False

    def test_nonexistent_group(self):
        parser = _make_parser_with_groups()
        assert in_group(parser, "--alpha", "nonexistent") is False

    def test_dest_based_match(self):
        parser = _make_parser_with_groups()
        assert in_group(parser, "alpha", "provider") is True


class TestRemoveArgument:
    def test_remove_existing_argument(self):
        parser = _make_parser_with_groups()
        groups = remove_argument(parser, "--alpha")
        assert "provider" in groups
        opts = [opt for a in parser._actions for opt in a.option_strings]
        assert "--alpha" not in opts

    def test_remove_by_dest(self):
        parser = _make_parser_with_groups()
        groups = remove_argument(parser, "beta")
        assert "provider" in groups

    def test_remove_nonexistent_argument(self):
        parser = _make_parser_with_groups()
        groups = remove_argument(parser, "--nonexistent")
        assert groups == []


class TestGetArgumentChoices:
    def test_returns_choices(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--color", choices=["red", "green", "blue"])
        assert get_argument_choices(parser, "--color") == ("red", "green", "blue")

    def test_returns_empty_tuple_when_no_choices(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--name", type=str)
        assert get_argument_choices(parser, "--name") == ()

    def test_returns_empty_tuple_for_missing_argument(self):
        parser = argparse.ArgumentParser()
        assert get_argument_choices(parser, "--missing") == ()


class TestOptionalChoices:
    def test_set_and_get_optional_choices(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--provider", type=str)
        action = parser._actions[-1]
        set_optional_choices(action, True)
        assert get_argument_optional_choices(parser, "--provider") is True

    def test_get_optional_choices_default_raises(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--provider", type=str)
        with pytest.raises(AttributeError):
            get_argument_optional_choices(parser, "--provider")

    def test_set_optional_choices_false_noop(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--test", type=str)
        action = parser._actions[-1]
        set_optional_choices(action, False)
        assert not hasattr(action, "optional_choices")

    def test_get_optional_choices_unknown_argument_returns_false(self):
        """Unknown argument name walks the actions list and returns False."""
        parser = argparse.ArgumentParser()
        parser.add_argument("--known", type=str)
        assert get_argument_optional_choices(parser, "--never-set") is False
