"""Test the choices controller."""

from argparse import ArgumentParser
from unittest.mock import patch

import pytest

from openbb_cli.controllers.choices import (
    build_controller_choice_map,
)


class MockController:
    """Mock controller class for testing."""

    CHOICES_COMMANDS = ["test_command"]
    controller_choices = ["test_command", "help"]

    def call_test_command(self, args):
        """Mock function for test_command."""
        parser = ArgumentParser()
        parser.add_argument(
            "--example", choices=["option1", "option2"], help="Example argument."
        )
        return parser.parse_args(args)


@pytest.fixture
def mock_controller():
    """Mock controller fixture."""
    return MockController()


def test_build_command_choice_map(mock_controller):
    """Test the building of a command choice map."""
    with patch(
        "openbb_cli.controllers.choices._get_argument_parser"
    ) as mock_get_parser:
        parser = ArgumentParser()
        parser.add_argument(
            "--option", choices=["opt1", "opt2"], help="A choice option."
        )
        mock_get_parser.return_value = parser

        choice_map = build_controller_choice_map(controller=mock_controller)

        assert "test_command" in choice_map
        assert "--option" in choice_map["test_command"]
        assert "opt1" in choice_map["test_command"]["--option"]
        assert "opt2" in choice_map["test_command"]["--option"]


def test_get_command_func_unknown_command_raises():
    """``__get_command_func`` raises AttributeError when the command isn't registered."""
    from openbb_cli.controllers import choices as _choices

    fn = getattr(_choices, "_choices__get_command_func", None) or getattr(
        _choices, "__get_command_func"
    )

    class C:
        CHOICES_COMMANDS = ["allowed"]

    with pytest.raises(AttributeError, match="not inside `CHOICES_COMMANDS`"):
        fn(C(), "unknown")


def test_contains_functions_to_patch_detects_parse_calls():
    """Detect functions whose body references ``parse_simple_args`` / ``parse_known_args_and_warn``."""
    from openbb_cli.controllers.choices import contains_functions_to_patch

    def with_parse(self):
        self.parse_known_args_and_warn(None, [])

    def without_parse(self):
        return None

    assert contains_functions_to_patch(with_parse) is True
    assert contains_functions_to_patch(without_parse) is False


def test_get_argument_parser_rejects_function_without_parsers():
    """``_get_argument_parser`` raises if the call_* function never calls a parser helper."""
    from openbb_cli.controllers.choices import _get_argument_parser

    class C:
        CHOICES_COMMANDS = ["foo"]

        def call_foo(self, _):
            return None

    with pytest.raises(AssertionError, match="parse_simple_args"):
        _get_argument_parser(C(), "foo")


def test_build_command_choice_map_skips_suppressed_actions():
    """Actions with ``help=SUPPRESS`` are excluded from the choice map."""
    from argparse import SUPPRESS

    from openbb_cli.controllers.choices import _build_command_choice_map

    parser = ArgumentParser()
    parser.add_argument("--visible", choices=["a", "b"])
    parser.add_argument("--hidden", help=SUPPRESS)
    cmap = _build_command_choice_map(parser)
    assert "--visible" in cmap
    assert "--hidden" not in cmap


def test_build_command_choice_map_short_long_name_aliases():
    """Two option strings → short maps to long; choices live on the long form."""
    from openbb_cli.controllers.choices import _build_command_choice_map

    parser = ArgumentParser()
    parser.add_argument("-l", "--limit", choices=["10", "20"])
    cmap = _build_command_choice_map(parser)
    assert cmap["-l"] == "--limit"
    assert "10" in cmap["--limit"]


def test_build_command_choice_map_rejects_invalid_action():
    """An action with three option strings is rejected."""
    from openbb_cli.controllers.choices import _build_command_choice_map

    parser = ArgumentParser()
    action = parser.add_argument("--a")
    action.option_strings = ["-a", "--alpha", "--alias"]
    with pytest.raises(AttributeError, match="Invalid argument_parser"):
        _build_command_choice_map(parser)


def test_build_controller_choice_map_reraises_in_debug_mode(mock_controller):
    """In ``DEBUG_MODE`` failures are re-raised as a contextualized exception."""
    with (
        patch("openbb_cli.controllers.choices._get_argument_parser") as get_parser,
        patch("openbb_cli.controllers.choices.session") as sess,
    ):
        get_parser.side_effect = RuntimeError("boom")
        sess.settings.DEBUG_MODE = True
        with pytest.raises(Exception, match="On command : `test_command`"):
            build_controller_choice_map(mock_controller)


def _mock_parse():
    """Resolve the module-private ``__mock_parse_known_args_and_warn``."""
    from openbb_cli.controllers import choices as _choices

    return getattr(
        _choices, "_choices__mock_parse_known_args_and_warn", None
    ) or getattr(_choices, "__mock_parse_known_args_and_warn")


def test_mock_parse_no_export_skips_export_argument():
    """``export_allowed='no_export'`` does not add an ``--export`` argument."""
    from argparse import ArgumentParser

    parser = ArgumentParser(add_help=False)
    fn = _mock_parse()
    fn(controller=None, parser=parser, other_args=[], export_allowed="no_export")
    optstrings = {opt for action in parser._actions for opt in action.option_strings}
    assert "--export" not in optstrings


@pytest.mark.parametrize(
    "mode, choices",
    [
        ("raw_data_only", {"csv", "json", "xlsx"}),
        ("figures_only", {"png", "jpg"}),
        ("raw_data_and_figures", {"csv", "json", "xlsx", "png", "jpg"}),
    ],
)
def test_mock_parse_export_choices_match_mode(mode, choices):
    """Each ``export_allowed`` mode emits the matching choices on ``--export``."""
    from argparse import ArgumentParser

    parser = ArgumentParser(add_help=False)
    fn = _mock_parse()
    fn(controller=None, parser=parser, other_args=[], export_allowed=mode)
    for action in parser._actions:
        if "--export" in action.option_strings:
            assert set(action.choices) == choices
            return
    pytest.fail("--export action not added")


def test_mock_parse_raw_flag_adds_raw_argument():
    """``raw=True`` adds the ``--raw`` flag."""
    from argparse import ArgumentParser

    parser = ArgumentParser(add_help=False)
    fn = _mock_parse()
    fn(controller=None, parser=parser, other_args=[], raw=True)
    optstrings = {opt for action in parser._actions for opt in action.option_strings}
    assert "--raw" in optstrings


def test_mock_parse_limit_positive_adds_limit_argument():
    """``limit=N`` (N>0) adds ``-l/--limit`` with default N."""
    from argparse import ArgumentParser

    parser = ArgumentParser(add_help=False)
    fn = _mock_parse()
    fn(controller=None, parser=parser, other_args=[], limit=42)
    for action in parser._actions:
        if "--limit" in action.option_strings:
            assert action.default == 42
            return
    pytest.fail("--limit not added")


def test_mock_parse_register_obbject_and_register_key_always_added():
    """``--register_obbject`` and ``--register_key`` are always added."""
    from argparse import ArgumentParser

    parser = ArgumentParser(add_help=False)
    fn = _mock_parse()
    fn(controller=None, parser=parser, other_args=[], export_allowed="no_export")
    optstrings = {opt for action in parser._actions for opt in action.option_strings}
    assert "--register_obbject" in optstrings
    assert "--register_key" in optstrings


def test_get_argument_parser_call_count_zero_raises():
    """A ``call_*`` fn that contains a parse-helper name but never invokes it raises AssertionError."""
    from openbb_cli.controllers.choices import _get_argument_parser

    class C:
        CHOICES_COMMANDS = ["foo"]

        def call_foo(self, _other_args):
            _ = "parse_simple_args"  # noqa: F841

    with pytest.raises(AssertionError, match="parse_simple_args"):
        _get_argument_parser(C(), "foo")


def test_get_argument_parser_call_count_two_raises():
    """A ``call_*`` fn that invokes BOTH parser helpers raises (call_count != 1)."""
    from openbb_cli.controllers.choices import _get_argument_parser

    class C:
        CHOICES_COMMANDS = ["foo"]

        def parse_simple_args(self, parser, other_args):
            return None, None

        def parse_known_args_and_warn(self, parser, other_args, **_):
            return None

        def call_foo(self, other_args):
            self.parse_simple_args(ArgumentParser(add_help=False), other_args)
            self.parse_known_args_and_warn(ArgumentParser(add_help=False), other_args)

    with pytest.raises(AssertionError, match="parse_simple_args"):
        _get_argument_parser(C(), "foo")
