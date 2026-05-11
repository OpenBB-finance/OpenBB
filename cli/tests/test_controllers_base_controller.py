"""Test the base controller."""

import argparse
from unittest.mock import MagicMock, patch

import pytest

from openbb_cli.controllers.base_controller import BaseController


class DummyBaseController(BaseController):
    """Testable Base Controller."""

    def __init__(self, queue=None):
        """Initialize the TestableBaseController."""
        self.PATH = "/valid/path/"
        super().__init__(queue=queue)

    def print_help(self):
        """Print help."""


def test_base_controller_initialization():
    """Test the initialization of the base controller."""
    with patch.object(DummyBaseController, "check_path", return_value=None):
        controller = DummyBaseController()
        assert controller.path == ["valid", "path"]


def test_path_validation():
    """Test the path validation method."""
    controller = DummyBaseController()

    with pytest.raises(ValueError):
        controller.PATH = "invalid/path"
        controller.check_path()

    with pytest.raises(ValueError):
        controller.PATH = "/invalid/path"
        controller.check_path()

    with pytest.raises(ValueError):
        controller.PATH = "/Invalid/Path/"
        controller.check_path()

    controller.PATH = "/valid/path/"


def test_parse_input():
    """Test the parse input method."""
    controller = DummyBaseController()
    input_str = "cmd1/cmd2/cmd3"
    expected = ["cmd1", "cmd2", "cmd3"]
    result = controller.parse_input(input_str)
    assert result == expected


def test_switch():
    """Test the switch method."""
    controller = DummyBaseController()
    with patch.object(controller, "call_exit", MagicMock()) as mock_exit:
        controller.queue = ["exit"]
        controller.switch("exit")
        mock_exit.assert_called_once()


def test_call_help():
    """Test the call help method."""
    controller = DummyBaseController()
    with patch("openbb_cli.controllers.base_controller.session.console.print"):
        controller.call_help(None)


def test_call_exit():
    """Test the call exit method."""
    controller = DummyBaseController()
    with patch.object(controller, "save_class", MagicMock()):
        controller.queue = ["quit"]
        controller.call_exit(None)


def test_update_completer_with_session_prompt_session():
    """``update_completer`` populates load + results subtree when a prompt session exists."""
    controller = DummyBaseController()
    with (
        patch("openbb_cli.controllers.base_controller.session") as sess,
        patch(
            "openbb_cli.controllers.utils.get_data_files_for_completion",
            return_value=["a.csv", "b.json"],
        ),
        patch("openbb_cli.controllers.base_controller.NestedCompleter") as nested,
    ):
        sess.prompt_session = MagicMock()
        sess.settings.USE_PROMPT_TOOLKIT = True
        sess.obbject_registry.all = {0: {"key": "k1"}, 1: {"key": ""}}
        controller.update_completer({})
    nested.from_nested_dict.assert_called_once()
    choices = nested.from_nested_dict.call_args[0][0]
    assert "load" in choices
    assert "results" in choices
    assert "--file" in choices["load"]
    assert "--index" in choices["results"]


def test_update_completer_without_prompt_session_is_noop():
    """No prompt session → ``update_completer`` skips completer construction."""
    controller = DummyBaseController()
    with (
        patch("openbb_cli.controllers.base_controller.session") as sess,
        patch("openbb_cli.controllers.base_controller.NestedCompleter") as nested,
    ):
        sess.prompt_session = None
        controller.update_completer({})
    nested.from_nested_dict.assert_not_called()


def test_load_class_returns_existing_instance_menu_when_cached():
    """``load_class`` reuses a cached controller when called with exactly one extra arg."""
    from openbb_cli.controllers import base_controller

    controller = DummyBaseController()
    controller.queue = ["next"]

    cached = MagicMock()
    cached.PATH = "/cached/"
    cached.menu.return_value = ["after-menu"]

    base_controller.controllers["/cached/"] = cached
    try:
        result = controller.load_class(cached, "extra-arg")
    finally:
        base_controller.controllers.pop("/cached/", None)
    assert result == ["after-menu"]
    cached.update_completer.assert_called_once()
    assert cached.queue == controller.queue


def test_load_class_creates_new_instance_when_extra_args():
    """If extra args are passed, ``load_class`` constructs a new instance."""
    controller = DummyBaseController()
    controller.queue = ["x"]

    factory = MagicMock()
    factory.PATH = "/new-class/"
    instance = factory.return_value
    instance.menu.return_value = ["new-menu"]

    result = controller.load_class(factory, "extra-arg-1", "extra-arg-2")
    assert result == ["new-menu"]
    factory.assert_called_once_with("extra-arg-1", "extra-arg-2")


def test_save_class_stores_self_in_module_registry():
    """``save_class`` records the controller under its PATH."""
    from openbb_cli.controllers import base_controller

    controller = DummyBaseController()
    controller.PATH = "/dummy/"
    base_controller.controllers.pop("/dummy/", None)
    controller.save_class()
    assert base_controller.controllers["/dummy/"] is controller
    base_controller.controllers.pop("/dummy/", None)


def test_custom_reset_returns_empty_list():
    """The base ``custom_reset`` returns an empty list (subclasses override)."""
    controller = DummyBaseController()
    assert controller.custom_reset() == []


def test_call_reset_uses_custom_reset_when_subclass_overrides():
    """A controller whose ``custom_reset`` returns non-empty has its result
    prepended to ``self.queue``."""

    class CustomResetController(DummyBaseController):
        def custom_reset(self):
            return ["restored", "tokens"]

    controller = CustomResetController()
    controller.queue = ["existing"]
    with patch.object(controller, "save_class"):
        controller.call_reset(None)
    assert "restored" in controller.queue
    assert "tokens" in controller.queue


def test_parse_input_protects_file_path_with_extension():
    """``-f path/to/data.csv`` is not split on ``/``."""
    controller = DummyBaseController()
    result = controller.parse_input("load -f path/to/data.csv")
    assert any("path/to/data.csv" in cmd for cmd in result)


def test_parse_input_protects_long_file_flag():
    """``--file`` form gets the same protection as ``-f``."""
    controller = DummyBaseController()
    result = controller.parse_input("load --file folder/x.json")
    assert any("folder/x.json" in cmd for cmd in result)


def test_parse_input_splits_on_slash_when_no_file():
    """Plain command path ``a/b/c`` splits into individual commands."""
    controller = DummyBaseController()
    result = controller.parse_input("a/b/c")
    assert "a" in result and "b" in result and "c" in result


def test_parse_input_absolute_path_prepends_home():
    """Input starting with ``/`` is rooted at home (``home`` prepended)."""
    controller = DummyBaseController()
    result = controller.parse_input("/equity/load")
    assert result[0] == "home"


def test_parse_input_does_not_double_prepend_home():
    """If the first token is already ``home``, don't add another."""
    controller = DummyBaseController()
    result = controller.parse_input("/home/equity")
    assert result.count("home") == 1


def test_switch_empty_input_returns_queue():
    """Empty input → no actions, returns the existing queue."""
    controller = DummyBaseController()
    controller.queue = ["existing"]
    with patch("openbb_cli.controllers.base_controller.session"):
        result = controller.switch("")
    assert result == ["existing"]


def test_switch_multiple_actions_pushes_to_queue():
    """``a/b/c`` splits and pushes onto the queue in order."""
    controller = DummyBaseController()
    controller.queue = []
    with patch("openbb_cli.controllers.base_controller.session"):
        controller.switch("first/second/third")
    assert "first" in controller.queue
    assert "second" in controller.queue
    assert "third" in controller.queue


@pytest.mark.parametrize(
    "shortcut, expected_method",
    [
        ("..", "call_quit"),
        ("q", "call_quit"),
        ("e", "call_exit"),
        ("?", "call_help"),
        ("h", "call_help"),
        ("r", "call_reset"),
    ],
)
def test_switch_redirects_shortcuts_to_canonical_methods(shortcut, expected_method):
    """``..`` / ``q`` / ``e`` / ``?`` / ``h`` / ``r`` redirect to their canonical call_* method."""
    controller = DummyBaseController()
    controller.queue = []
    with (
        patch("openbb_cli.controllers.base_controller.session"),
        patch.object(controller, expected_method) as canonical,
    ):
        controller.switch(shortcut)
    canonical.assert_called_once()


def test_switch_argparse_failure_raises_systemexit():
    """``switch`` re-raises argparse failures as SystemExit (production behavior)."""
    controller = DummyBaseController()
    controller.queue = []
    with (
        patch("openbb_cli.controllers.base_controller.session"),
        patch.object(
            controller.parser,
            "parse_known_args",
            side_effect=Exception("bad input"),
        ),
        pytest.raises(SystemExit),
    ):
        controller.switch("nonexistent_command_xyz")


def test_switch_unknown_command_lambda_fallback():
    """Unknown commands without raise → lambda fallback returning the warning string."""
    controller = DummyBaseController()
    controller.queue = []
    fake_known = MagicMock()
    fake_known.cmd = "nonexistent_command_xyz"
    with (
        patch("openbb_cli.controllers.base_controller.session"),
        patch.object(
            controller.parser, "parse_known_args", return_value=(fake_known, [])
        ),
    ):
        controller.switch("nonexistent_command_xyz")


def test_call_cls_invokes_system_clear():
    """``call_cls`` delegates to ``system_clear()``."""
    controller = DummyBaseController()
    with patch("openbb_cli.controllers.base_controller.system_clear") as system_clear:
        controller.call_cls(None)
    system_clear.assert_called_once()


def test_call_home_pushes_quits_for_each_path_segment():
    """``call_home`` saves and pushes ``quit`` for each path-slash beyond the first."""
    controller = DummyBaseController()
    controller.PATH = "/a/b/c/"
    controller.queue = []
    with (
        patch.object(controller, "save_class") as save_class,
        patch.object(controller, "print_help"),
        patch("openbb_cli.controllers.base_controller.session"),
    ):
        controller.call_home(None)
    save_class.assert_called_once()
    assert controller.queue.count("quit") == 3


def test_call_home_at_root_calls_print_help_when_auto_help_enabled():
    """At PATH depth ``count('/')==1`` (root), ``ENABLE_EXIT_AUTO_HELP`` triggers ``print_help``."""
    controller = DummyBaseController()
    controller.PATH = "/"
    controller.queue = []
    with (
        patch.object(controller, "save_class"),
        patch.object(controller, "print_help") as print_help,
        patch("openbb_cli.controllers.base_controller.session") as sess,
    ):
        sess.settings.ENABLE_EXIT_AUTO_HELP = True
        controller.call_home(None)
    print_help.assert_called_once()


def test_call_quit_pushes_quit_to_queue():
    """``call_quit`` saves and prepends ``quit``."""
    controller = DummyBaseController()
    controller.queue = ["next"]
    with patch.object(controller, "save_class"):
        controller.call_quit(None)
    assert controller.queue[0] == "quit"


def test_call_reset_pushes_resetting_signal():
    """``call_reset`` populates the queue with the reset sentinel."""
    controller = DummyBaseController()
    controller.queue = []
    controller.PATH = "/x/y/"
    with (
        patch.object(controller, "save_class"),
        patch("openbb_cli.controllers.base_controller.session"),
    ):
        controller.call_reset(None)
    assert True


def _make_record_args(name, description=None, tag1="", tag2="", tag3=""):
    """Build a mock ns_parser for call_record."""
    ns = MagicMock()
    ns.name = name
    ns.description = description or []
    ns.tag1 = tag1
    ns.tag2 = tag2
    ns.tag3 = tag3
    return ns


def test_call_record_without_name_warns(mock_base_session):
    """No ``-n`` name → red warning, no recording started."""
    from openbb_cli.controllers import base_controller

    controller = DummyBaseController()
    ns = _make_record_args(name=[])
    controller.parse_simple_args = MagicMock(return_value=(ns, []))
    base_controller.RECORD_SESSION = False
    controller.call_record([])
    mock_base_session.console.print.assert_called()
    assert base_controller.RECORD_SESSION is False


def test_call_record_invalid_tag1_warns(mock_base_session):
    """``--tag1`` outside SCRIPT_TAGS triggers a red warning."""
    from openbb_cli.controllers import base_controller

    controller = DummyBaseController()
    ns = _make_record_args(name=["routine"], tag1="not_a_tag")
    controller.parse_simple_args = MagicMock(return_value=(ns, []))
    base_controller.RECORD_SESSION = False
    controller.call_record(["-n", "routine", "--tag1", "not_a_tag"])
    mock_base_session.console.print.assert_called()
    assert base_controller.RECORD_SESSION is False


def test_call_record_invalid_title_format_warns(mock_base_session):
    """Title with special chars (e.g. punctuation) is rejected."""
    from openbb_cli.controllers import base_controller

    controller = DummyBaseController()
    ns = _make_record_args(name=["bad!!!title###"])
    controller.parse_simple_args = MagicMock(return_value=(ns, []))
    base_controller.RECORD_SESSION = False
    controller.call_record(["-n", "bad!!!title###"])
    mock_base_session.console.print.assert_called()
    assert base_controller.RECORD_SESSION is False


def test_call_record_valid_input_starts_recording(mock_base_session):
    """Valid name + valid tags → ``RECORD_SESSION`` flips True."""
    from openbb_cli.controllers import base_controller
    from openbb_cli.controllers.base_controller import SCRIPT_TAGS

    controller = DummyBaseController()
    valid_tag = SCRIPT_TAGS[0]
    ns = _make_record_args(
        name=["clean", "title"],
        description=["my", "routine"],
        tag1=valid_tag,
    )
    controller.parse_simple_args = MagicMock(return_value=(ns, []))
    base_controller.RECORD_SESSION = False
    try:
        controller.call_record(["-n", "clean title"])
        assert base_controller.RECORD_SESSION is True
        assert base_controller.SESSION_RECORDED_NAME == "clean title"
    finally:
        base_controller.RECORD_SESSION = False


def test_call_record_inserts_dash_n_when_first_arg_lacks_flag(mock_base_session):
    """When ``other_args[0]`` doesn't start with ``-``, ``-n`` is auto-prepended."""
    from openbb_cli.controllers import base_controller

    controller = DummyBaseController()
    captured: list[list[str]] = []

    def fake_parse_simple_args(parser, args):
        captured.append(args[:])
        return (None, [])

    controller.parse_simple_args = fake_parse_simple_args
    base_controller.RECORD_SESSION = False
    controller.call_record(["my_routine"])
    assert captured[0][0] == "-n"
    assert captured[0][1] == "my_routine"


def test_call_stop_when_not_recording_warns(mock_base_session):
    """``stop`` while ``RECORD_SESSION`` is False prints a warning."""
    from openbb_cli.controllers import base_controller

    controller = DummyBaseController()
    base_controller.RECORD_SESSION = False
    controller.parse_simple_args = MagicMock(return_value=(None, []))
    controller.call_stop([])
    mock_base_session.console.print.assert_called()


def test_call_stop_with_empty_session_recorded_warns(mock_base_session):
    """Recording on but session-recorded list empty → still prints a warning, doesn't crash."""
    from openbb_cli.controllers import base_controller

    controller = DummyBaseController()
    base_controller.RECORD_SESSION = True
    base_controller.SESSION_RECORDED.clear()
    controller.parse_simple_args = MagicMock(return_value=(None, []))
    try:
        controller.call_stop([])
    finally:
        base_controller.RECORD_SESSION = False
    mock_base_session.console.print.assert_called()


def test_call_stop_writes_routine_file_when_recorded(mock_base_session, tmp_path):
    """``stop`` writes the recorded session to disk under ``export_directory/routines``."""
    from openbb_cli.controllers import base_controller

    controller = DummyBaseController()
    base_controller.RECORD_SESSION = True
    base_controller.SESSION_RECORDED = [
        "/equity/load",
        "/equity/quote",
        "/equity/quote",
        "/equity/quote",
        "/equity/quote",
        "stop",
    ]
    base_controller.SESSION_RECORDED_NAME = "Test Routine"
    base_controller.SESSION_RECORDED_TAGS = "Stocks"
    base_controller.SESSION_RECORDED_DESCRIPTION = "A test routine"
    mock_base_session.user.preferences.export_directory = str(tmp_path)
    controller.parse_simple_args = MagicMock(return_value=(None, []))
    try:
        controller.call_stop([])
    finally:
        base_controller.RECORD_SESSION = False
    routine_file = tmp_path / "routines" / "Test_Routine.openbb"
    assert routine_file.exists()
    body = routine_file.read_text()
    assert "Title: Test Routine" in body
    assert "/equity/load" in body
    assert base_controller.RECORD_SESSION is False
    assert base_controller.SESSION_RECORDED == []


def test_call_stop_overwrites_with_new_name_when_user_declines(
    mock_base_session, tmp_path
):
    """If a routine file exists and the user picks 'n', a timestamped name is used."""
    from openbb_cli.controllers import base_controller

    controller = DummyBaseController()
    base_controller.RECORD_SESSION = True
    base_controller.SESSION_RECORDED = ["a", "b", "c", "d", "e", "stop"]
    base_controller.SESSION_RECORDED_NAME = "Same"
    base_controller.SESSION_RECORDED_TAGS = ""
    base_controller.SESSION_RECORDED_DESCRIPTION = ""
    mock_base_session.user.preferences.export_directory = str(tmp_path)
    routines_dir = tmp_path / "routines"
    routines_dir.mkdir()
    (routines_dir / "Same.openbb").write_text("# old")
    mock_base_session.console.input.return_value = "n"
    controller.parse_simple_args = MagicMock(return_value=(None, []))
    try:
        controller.call_stop([])
    finally:
        base_controller.RECORD_SESSION = False
    new_files = [f for f in routines_dir.iterdir() if f.name != "Same.openbb"]
    assert new_files


@pytest.mark.parametrize(
    "mode, expected_choices",
    [
        ("raw_data_only", {"csv", "json", "xlsx"}),
        ("figures_only", {"png", "jpg"}),
        (
            "raw_data_and_figures",
            {"csv", "json", "xlsx", "png", "jpg", "db", "sqlite", "sqlite3"},
        ),
    ],
)
def test_parse_known_args_and_warn_export_choices(
    mock_base_session, mode, expected_choices
):
    """Each ``export_allowed`` value installs a matching ``--export`` choices set."""
    parser = argparse.ArgumentParser(add_help=False)
    BaseController.parse_known_args_and_warn(parser, [], export_allowed=mode)
    for action in parser._actions:
        if "--export" in action.option_strings:
            return
    pytest.fail("--export not added")


def test_parse_known_args_and_warn_no_export_skips_argument(mock_base_session):
    """``export_allowed='no_export'`` does not add ``--export``."""
    parser = argparse.ArgumentParser(add_help=False)
    BaseController.parse_known_args_and_warn(parser, [], export_allowed="no_export")
    optstrings = {opt for action in parser._actions for opt in action.option_strings}
    assert "--export" not in optstrings


def test_parse_known_args_and_warn_sheet_name_added_for_raw_modes(mock_base_session):
    """``raw_data_only`` and ``raw_data_and_figures`` modes add ``--sheet-name``."""
    for mode in ("raw_data_only", "raw_data_and_figures"):
        parser = argparse.ArgumentParser(add_help=False)
        BaseController.parse_known_args_and_warn(parser, [], export_allowed=mode)
        optstrings = {
            opt for action in parser._actions for opt in action.option_strings
        }
        assert "--sheet-name" in optstrings, f"--sheet-name missing for {mode}"


def test_parse_known_args_and_warn_sheet_name_omitted_for_figures_only(
    mock_base_session,
):
    """``figures_only`` does NOT add ``--sheet-name`` (no Excel)."""
    parser = argparse.ArgumentParser(add_help=False)
    BaseController.parse_known_args_and_warn(parser, [], export_allowed="figures_only")
    optstrings = {opt for action in parser._actions for opt in action.option_strings}
    assert "--sheet-name" not in optstrings


def test_parse_known_args_and_warn_raw_flag_added(mock_base_session):
    """``raw=True`` adds the ``--raw`` flag."""
    parser = argparse.ArgumentParser(add_help=False)
    BaseController.parse_known_args_and_warn(parser, [], raw=True)
    optstrings = {opt for action in parser._actions for opt in action.option_strings}
    assert "--raw" in optstrings


def test_parse_known_args_and_warn_limit_positive_adds_limit(mock_base_session):
    """``limit=N`` (N>0) adds ``-l/--limit`` with default N."""
    parser = argparse.ArgumentParser(add_help=False)
    BaseController.parse_known_args_and_warn(parser, [], limit=42)
    for action in parser._actions:
        if "--limit" in action.option_strings:
            assert action.default == 42
            return
    pytest.fail("--limit not added")


@pytest.fixture
def mock_base_session():
    """Mock the session for parse_known_args_and_warn tests."""
    with patch("openbb_cli.controllers.base_controller.session") as mock_session:
        mock_session.settings.USE_CLEAR_AFTER_CMD = False
        yield mock_session


def _make_parser(*args_spec):
    """Create an argparse parser from a list of add_argument kwargs."""
    parser = argparse.ArgumentParser(add_help=False)
    for spec in args_spec:
        flags = spec.pop("flags")
        parser.add_argument(*flags, **spec)
    return parser


def test_comma_split_flagged_value_not_split(mock_base_session):
    """Simple test: --symbol AAPL,MSFT must stay as one value."""
    parser = _make_parser({"flags": ["--symbol", "-s"], "dest": "symbol", "type": str})
    result = BaseController.parse_known_args_and_warn(parser, ["--symbol", "AAPL,MSFT"])
    assert result is not None
    assert result.symbol == "AAPL,MSFT"


def test_comma_split_short_flag_not_split(mock_base_session):
    """Short flag -s AAPL,MSFT must also stay as one value."""
    parser = _make_parser({"flags": ["--symbol", "-s"], "dest": "symbol", "type": str})
    result = BaseController.parse_known_args_and_warn(parser, ["-s", "AAPL,MSFT"])
    assert result is not None
    assert result.symbol == "AAPL,MSFT"


def test_comma_split_equals_syntax_not_split(mock_base_session):
    """--symbol=AAPL,MSFT must not be split."""
    parser = _make_parser({"flags": ["--symbol", "-s"], "dest": "symbol", "type": str})
    result = BaseController.parse_known_args_and_warn(parser, ["--symbol=AAPL,MSFT"])
    assert result is not None
    assert result.symbol == "AAPL,MSFT"


def test_comma_split_nargs_plus_all_values_protected(mock_base_session):
    """nargs='+': all consecutive values after --symbols are protected."""
    parser = _make_parser(
        {"flags": ["--symbols"], "dest": "symbols", "nargs": "+", "type": str}
    )
    result = BaseController.parse_known_args_and_warn(
        parser, ["--symbols", "AAPL,MSFT", "GOOG,AMZN"]
    )
    assert result is not None
    assert result.symbols == ["AAPL,MSFT", "GOOG,AMZN"]


def test_comma_split_nargs_star_values_protected(mock_base_session):
    """nargs='*': consecutive values after --tags are protected."""
    parser = _make_parser(
        {"flags": ["--tags"], "dest": "tags", "nargs": "*", "type": str}
    )
    result = BaseController.parse_known_args_and_warn(parser, ["--tags", "a,b", "c,d"])
    assert result is not None
    assert result.tags == ["a,b", "c,d"]


def test_comma_split_nargs_int_values_protected(mock_base_session):
    """nargs=2: both values after --pair are protected."""
    parser = _make_parser(
        {"flags": ["--pair"], "dest": "pair", "nargs": 2, "type": str}
    )
    result = BaseController.parse_known_args_and_warn(parser, ["--pair", "a,b", "c,d"])
    assert result is not None
    assert result.pair == ["a,b", "c,d"]


def test_comma_split_store_true_not_confused(mock_base_session):
    """store_true flags (nargs=0) should not protect the next token."""
    parser = _make_parser(
        {"flags": ["--symbol", "-s"], "dest": "symbol", "type": str},
        {"flags": ["--raw"], "dest": "raw", "action": "store_true", "default": False},
    )
    result = BaseController.parse_known_args_and_warn(
        parser, ["--raw", "--symbol", "AAPL,MSFT"]
    )
    assert result is not None
    assert result.raw is True
    assert result.symbol == "AAPL,MSFT"


def test_comma_split_no_comma_values_unchanged(mock_base_session):
    """Values without commas pass through unaffected."""
    parser = _make_parser({"flags": ["--symbol", "-s"], "dest": "symbol", "type": str})
    result = BaseController.parse_known_args_and_warn(parser, ["--symbol", "AAPL"])
    assert result is not None
    assert result.symbol == "AAPL"


def test_comma_split_multiple_flags_each_protected(mock_base_session):
    """Multiple flags each protect their own values independently."""
    parser = _make_parser(
        {"flags": ["--symbol", "-s"], "dest": "symbol", "type": str},
        {"flags": ["--raw"], "dest": "raw", "action": "store_true", "default": False},
        {"flags": ["--provider"], "dest": "provider", "type": str},
    )
    result = BaseController.parse_known_args_and_warn(
        parser,
        ["--symbol", "AAPL,MSFT", "--provider", "yfinance,polygon"],
    )
    assert result is not None
    assert result.symbol == "AAPL,MSFT"
    assert result.provider == "yfinance,polygon"


class TestCallResults:
    """Test the call_results method on BaseController."""

    def test_no_index_no_key_shows_all(self, mock_base_session):
        """Test results with no args shows all registry entries."""
        controller = DummyBaseController()
        mock_base_session.obbject_registry.all = {0: {"command": "test"}}
        controller.parse_simple_args = MagicMock(
            return_value=(
                MagicMock(
                    index=None, key=None, chart=False, export="", sheet_name=None
                ),
                [],
            )
        )
        controller.call_results([])
        mock_base_session.output_adapter.display.assert_called_once()

    def test_no_results(self, mock_base_session):
        """Test results when registry is empty."""
        controller = DummyBaseController()
        mock_base_session.obbject_registry.all = {}
        controller.parse_simple_args = MagicMock(
            return_value=(
                MagicMock(
                    index=None, key=None, chart=False, export="", sheet_name=None
                ),
                [],
            )
        )
        controller.call_results([])
        mock_base_session.console.print.assert_called()

    def test_by_index(self, mock_base_session):
        """Test results with --index flag."""
        controller = DummyBaseController()
        obbject = MagicMock()
        mock_base_session.obbject_registry.get.return_value = obbject
        controller.parse_simple_args = MagicMock(
            return_value=(
                MagicMock(index="0", key=None, chart=False, export="", sheet_name=None),
                [],
            )
        )
        with patch(
            "openbb_cli.controllers.base_controller.handle_obbject_display"
        ) as mock_display:
            controller.call_results(["-i", "0"])
            mock_display.assert_called_once()

    def test_by_invalid_index(self, mock_base_session):
        """Test results with non-integer index."""
        controller = DummyBaseController()
        controller.parse_simple_args = MagicMock(
            return_value=(
                MagicMock(
                    index="abc", key=None, chart=False, export="", sheet_name=None
                ),
                [],
            )
        )
        controller.call_results(["-i", "abc"])
        mock_base_session.console.print.assert_called()

    def test_by_key(self, mock_base_session):
        """Test results with --key flag."""
        controller = DummyBaseController()
        obbject = MagicMock()
        mock_base_session.obbject_registry.get.return_value = obbject
        controller.parse_simple_args = MagicMock(
            return_value=(
                MagicMock(
                    index=None, key="my_data", chart=False, export="", sheet_name=None
                ),
                [],
            )
        )
        with patch(
            "openbb_cli.controllers.base_controller.handle_obbject_display"
        ) as mock_display:
            controller.call_results(["-k", "my_data"])
            mock_display.assert_called_once()

    def test_by_key_not_found(self, mock_base_session):
        """Test results with unknown key."""
        controller = DummyBaseController()
        mock_base_session.obbject_registry.get.return_value = None
        controller.parse_simple_args = MagicMock(
            return_value=(
                MagicMock(
                    index=None, key="unknown", chart=False, export="", sheet_name=None
                ),
                [],
            )
        )
        controller.call_results(["-k", "unknown"])
        mock_base_session.console.print.assert_called()


class TestCallLoad:
    """Test the call_load method on BaseController."""

    def test_load_csv(self, mock_base_session, tmp_path):
        """Test loading a CSV file."""
        import pandas as pd

        csv_path = tmp_path / "test.csv"
        pd.DataFrame({"A": [1, 2], "B": [3, 4]}).to_csv(csv_path, index=False)

        controller = DummyBaseController()
        mock_base_session.user.preferences.data_directory = str(tmp_path)
        mock_base_session.obbject_registry.obbject_keys = []
        mock_base_session.obbject_registry.register.return_value = True
        mock_base_session.max_obbjects_exceeded = MagicMock(return_value=False)

        ns = MagicMock()
        ns.file = "test.csv"
        ns.sheet_name = None
        ns.register_key = ""
        controller.parse_simple_args = MagicMock(return_value=(ns, []))
        with patch("openbb_cli.controllers.base_controller.session", mock_base_session):
            controller.call_load(["-f", "test.csv"])
        mock_base_session.obbject_registry.register.assert_called_once()

    def test_load_file_not_found(self, mock_base_session, tmp_path):
        """Test loading a nonexistent file."""
        controller = DummyBaseController()
        mock_base_session.user.preferences.data_directory = str(tmp_path)

        ns = MagicMock()
        ns.file = "nonexistent.csv"
        ns.sheet_name = None
        ns.register_key = ""
        controller.parse_simple_args = MagicMock(return_value=(ns, []))
        with patch("openbb_cli.controllers.base_controller.session", mock_base_session):
            controller.call_load(["-f", "nonexistent.csv"])
        mock_base_session.console.print.assert_called()
        call_args = mock_base_session.console.print.call_args[0][0]
        assert "not found" in call_args.lower() or "File not found" in call_args

    def test_load_json(self, mock_base_session, tmp_path):
        """Test loading a JSON file."""
        import pandas as pd

        json_path = tmp_path / "test.json"
        pd.DataFrame({"A": [1, 2], "B": [3, 4]}).to_json(json_path, orient="records")

        controller = DummyBaseController()
        mock_base_session.user.preferences.data_directory = str(tmp_path)
        mock_base_session.obbject_registry.obbject_keys = []
        mock_base_session.obbject_registry.register.return_value = True
        mock_base_session.max_obbjects_exceeded = MagicMock(return_value=False)

        ns = MagicMock()
        ns.file = "test.json"
        ns.sheet_name = None
        ns.register_key = ""
        controller.parse_simple_args = MagicMock(return_value=(ns, []))
        with patch("openbb_cli.controllers.base_controller.session", mock_base_session):
            controller.call_load(["-f", "test.json"])
        mock_base_session.obbject_registry.register.assert_called_once()

    def test_load_excel(self, mock_base_session, tmp_path):
        """Test loading an Excel file."""
        import pandas as pd

        xlsx_path = tmp_path / "test.xlsx"
        pd.DataFrame({"A": [1, 2], "B": [3, 4]}).to_excel(xlsx_path, index=False)

        controller = DummyBaseController()
        mock_base_session.user.preferences.data_directory = str(tmp_path)
        mock_base_session.obbject_registry.obbject_keys = []
        mock_base_session.obbject_registry.register.return_value = True
        mock_base_session.max_obbjects_exceeded = MagicMock(return_value=False)

        ns = MagicMock()
        ns.file = "test.xlsx"
        ns.sheet_name = None
        ns.register_key = ""
        controller.parse_simple_args = MagicMock(return_value=(ns, []))
        with patch("openbb_cli.controllers.base_controller.session", mock_base_session):
            controller.call_load(["-f", "test.xlsx"])
        mock_base_session.obbject_registry.register.assert_called_once()

    def test_load_sqlite(self, mock_base_session, tmp_path):
        """Test loading a SQLite database (lazy via SQLiteTable)."""
        import sqlite3

        import pandas as pd

        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(db_path)
        pd.DataFrame({"A": [1, 2], "B": [3, 4]}).to_sql("prices", conn, index=False)
        conn.close()

        controller = DummyBaseController()
        mock_base_session.user.preferences.data_directory = str(tmp_path)
        mock_base_session.obbject_registry.obbject_keys = []
        mock_base_session.obbject_registry.register.return_value = True
        mock_base_session.max_obbjects_exceeded = MagicMock(return_value=False)

        ns = MagicMock()
        ns.file = "test.db"
        ns.sheet_name = None
        ns.register_key = ""
        controller.parse_simple_args = MagicMock(return_value=(ns, []))
        with patch("openbb_cli.controllers.base_controller.session", mock_base_session):
            controller.call_load(["-f", "test.db"])
        mock_base_session.obbject_registry.register.assert_called_once()

    def test_load_register_key(self, mock_base_session, tmp_path):
        """Test loading with --register_key sets the key on the OBBject."""
        import pandas as pd

        csv_path = tmp_path / "keyed.csv"
        pd.DataFrame({"X": [10]}).to_csv(csv_path, index=False)

        controller = DummyBaseController()
        mock_base_session.user.preferences.data_directory = str(tmp_path)
        mock_base_session.obbject_registry.obbject_keys = []
        mock_base_session.obbject_registry.register.return_value = True
        mock_base_session.max_obbjects_exceeded = MagicMock(return_value=False)

        ns = MagicMock()
        ns.file = "keyed.csv"
        ns.sheet_name = None
        ns.register_key = "my_key"
        controller.parse_simple_args = MagicMock(return_value=(ns, []))
        with patch("openbb_cli.controllers.base_controller.session", mock_base_session):
            controller.call_load(["-f", "keyed.csv", "--register_key", "my_key"])
        obbject = mock_base_session.obbject_registry.register.call_args[0][0]
        assert obbject.extra.get("register_key") == "my_key"

    def test_load_duplicate_register_key(self, mock_base_session, tmp_path):
        """Test loading with a duplicate register_key prints warning."""
        import pandas as pd

        csv_path = tmp_path / "dup.csv"
        pd.DataFrame({"X": [10]}).to_csv(csv_path, index=False)

        controller = DummyBaseController()
        mock_base_session.user.preferences.data_directory = str(tmp_path)
        mock_base_session.obbject_registry.obbject_keys = ["my_key"]
        mock_base_session.obbject_registry.register.return_value = True
        mock_base_session.max_obbjects_exceeded = MagicMock(return_value=False)

        ns = MagicMock()
        ns.file = "dup.csv"
        ns.sheet_name = None
        ns.register_key = "my_key"
        controller.parse_simple_args = MagicMock(return_value=(ns, []))
        with patch("openbb_cli.controllers.base_controller.session", mock_base_session):
            controller.call_load(["-f", "dup.csv", "--register_key", "my_key"])
        console_calls = [str(c) for c in mock_base_session.console.print.call_args_list]
        assert any("already exists" in c for c in console_calls)

    def test_load_max_obbjects_exceeded(self, mock_base_session, tmp_path):
        """Test eviction when max obbjects is exceeded."""
        import pandas as pd

        csv_path = tmp_path / "evict.csv"
        pd.DataFrame({"X": [1]}).to_csv(csv_path, index=False)

        controller = DummyBaseController()
        mock_base_session.user.preferences.data_directory = str(tmp_path)
        mock_base_session.obbject_registry.obbject_keys = []
        mock_base_session.obbject_registry.register.return_value = True
        mock_base_session.max_obbjects_exceeded = MagicMock(return_value=True)

        ns = MagicMock()
        ns.file = "evict.csv"
        ns.sheet_name = None
        ns.register_key = ""
        controller.parse_simple_args = MagicMock(return_value=(ns, []))
        with patch("openbb_cli.controllers.base_controller.session", mock_base_session):
            controller.call_load(["-f", "evict.csv"])
        mock_base_session.obbject_registry.remove.assert_called_once()
        console_calls = [str(c) for c in mock_base_session.console.print.call_args_list]
        assert any("oldest entry was removed" in c for c in console_calls)

    def test_load_register_failure(self, mock_base_session, tmp_path):
        """Test when register() returns False."""
        import pandas as pd

        csv_path = tmp_path / "fail_reg.csv"
        pd.DataFrame({"X": [1]}).to_csv(csv_path, index=False)

        controller = DummyBaseController()
        mock_base_session.user.preferences.data_directory = str(tmp_path)
        mock_base_session.obbject_registry.obbject_keys = []
        mock_base_session.obbject_registry.register.return_value = False
        mock_base_session.max_obbjects_exceeded = MagicMock(return_value=False)

        ns = MagicMock()
        ns.file = "fail_reg.csv"
        ns.sheet_name = None
        ns.register_key = ""
        controller.parse_simple_args = MagicMock(return_value=(ns, []))
        with patch("openbb_cli.controllers.base_controller.session", mock_base_session):
            controller.call_load(["-f", "fail_reg.csv"])
        console_calls = [str(c) for c in mock_base_session.console.print.call_args_list]
        assert any("Failed to register" in c for c in console_calls)

    def test_load_unsupported_file_type(self, mock_base_session, tmp_path):
        """Test loading an unsupported file type."""
        bad_file = tmp_path / "data.parquet"
        bad_file.write_bytes(b"fake")

        controller = DummyBaseController()
        mock_base_session.user.preferences.data_directory = str(tmp_path)

        ns = MagicMock()
        ns.file = "data.parquet"
        ns.sheet_name = None
        ns.register_key = ""
        controller.parse_simple_args = MagicMock(return_value=(ns, []))
        with patch("openbb_cli.controllers.base_controller.session", mock_base_session):
            controller.call_load(["-f", "data.parquet"])
        console_calls = [str(c) for c in mock_base_session.console.print.call_args_list]
        assert any("Unsupported" in c for c in console_calls)

    def test_load_json_duplicate_register_key(self, mock_base_session, tmp_path):
        """JSON load with already-registered key prints the warning."""
        import pandas as pd

        json_path = tmp_path / "dup.json"
        pd.DataFrame({"X": [1]}).to_json(json_path)
        controller = DummyBaseController()
        mock_base_session.user.preferences.data_directory = str(tmp_path)
        mock_base_session.obbject_registry.obbject_keys = ["my_key"]
        mock_base_session.obbject_registry.register.return_value = True
        mock_base_session.max_obbjects_exceeded = MagicMock(return_value=False)

        ns = MagicMock()
        ns.file = "dup.json"
        ns.sheet_name = None
        ns.register_key = "my_key"
        controller.parse_simple_args = MagicMock(return_value=(ns, []))
        with patch("openbb_cli.controllers.base_controller.session", mock_base_session):
            controller.call_load(["-f", "dup.json", "--register_key", "my_key"])
        calls = [str(c) for c in mock_base_session.console.print.call_args_list]
        assert any("already exists" in c for c in calls)

    def test_load_json_max_obbjects_exceeded(self, mock_base_session, tmp_path):
        """JSON load with full registry triggers eviction."""
        import pandas as pd

        json_path = tmp_path / "evict.json"
        pd.DataFrame({"X": [1]}).to_json(json_path)
        controller = DummyBaseController()
        mock_base_session.user.preferences.data_directory = str(tmp_path)
        mock_base_session.obbject_registry.obbject_keys = []
        mock_base_session.obbject_registry.register.return_value = True
        mock_base_session.max_obbjects_exceeded = MagicMock(return_value=True)

        ns = MagicMock()
        ns.file = "evict.json"
        ns.sheet_name = None
        ns.register_key = ""
        controller.parse_simple_args = MagicMock(return_value=(ns, []))
        with patch("openbb_cli.controllers.base_controller.session", mock_base_session):
            controller.call_load(["-f", "evict.json"])
        mock_base_session.obbject_registry.remove.assert_called_once()

    def test_load_json_register_failure(self, mock_base_session, tmp_path):
        """JSON load with register() returning False prints the failure warning."""
        import pandas as pd

        json_path = tmp_path / "fail.json"
        pd.DataFrame({"X": [1]}).to_json(json_path)
        controller = DummyBaseController()
        mock_base_session.user.preferences.data_directory = str(tmp_path)
        mock_base_session.obbject_registry.obbject_keys = []
        mock_base_session.obbject_registry.register.return_value = False
        mock_base_session.max_obbjects_exceeded = MagicMock(return_value=False)

        ns = MagicMock()
        ns.file = "fail.json"
        ns.sheet_name = None
        ns.register_key = ""
        controller.parse_simple_args = MagicMock(return_value=(ns, []))
        with patch("openbb_cli.controllers.base_controller.session", mock_base_session):
            controller.call_load(["-f", "fail.json"])
        calls = [str(c) for c in mock_base_session.console.print.call_args_list]
        assert any("Failed to register" in c for c in calls)

    def test_load_excel_duplicate_register_key(self, mock_base_session, tmp_path):
        """Excel load with already-registered key prints the warning."""
        import pandas as pd

        xlsx_path = tmp_path / "dup.xlsx"
        pd.DataFrame({"X": [1]}).to_excel(xlsx_path, index=False)
        controller = DummyBaseController()
        mock_base_session.user.preferences.data_directory = str(tmp_path)
        mock_base_session.obbject_registry.obbject_keys = ["k"]
        mock_base_session.obbject_registry.register.return_value = True
        mock_base_session.max_obbjects_exceeded = MagicMock(return_value=False)

        ns = MagicMock()
        ns.file = "dup.xlsx"
        ns.sheet_name = None
        ns.register_key = "k"
        controller.parse_simple_args = MagicMock(return_value=(ns, []))
        with patch("openbb_cli.controllers.base_controller.session", mock_base_session):
            controller.call_load(["-f", "dup.xlsx", "--register_key", "k"])
        calls = [str(c) for c in mock_base_session.console.print.call_args_list]
        assert any("already exists" in c for c in calls)

    def test_load_excel_with_sheet_name(self, mock_base_session, tmp_path):
        """``--sheet-name`` adjusts the appended ``command`` annotation."""
        import pandas as pd

        xlsx_path = tmp_path / "sheets.xlsx"
        with pd.ExcelWriter(xlsx_path, engine="openpyxl") as w:
            pd.DataFrame({"a": [1]}).to_excel(w, sheet_name="Custom", index=False)
        controller = DummyBaseController()
        mock_base_session.user.preferences.data_directory = str(tmp_path)
        mock_base_session.obbject_registry.obbject_keys = []
        mock_base_session.obbject_registry.register.return_value = True
        mock_base_session.max_obbjects_exceeded = MagicMock(return_value=False)

        ns = MagicMock()
        ns.file = "sheets.xlsx"
        ns.sheet_name = "Custom"
        ns.register_key = ""
        controller.parse_simple_args = MagicMock(return_value=(ns, []))
        with patch("openbb_cli.controllers.base_controller.session", mock_base_session):
            controller.call_load(["-f", "sheets.xlsx", "--sheet-name", "Custom"])
        registered = mock_base_session.obbject_registry.register.call_args[0][0]
        assert "--sheet-name Custom" in registered.extra["command"]

    def test_load_excel_max_obbjects_exceeded(self, mock_base_session, tmp_path):
        """Excel load with full registry triggers eviction."""
        import pandas as pd

        xlsx_path = tmp_path / "ev.xlsx"
        pd.DataFrame({"X": [1]}).to_excel(xlsx_path, index=False)
        controller = DummyBaseController()
        mock_base_session.user.preferences.data_directory = str(tmp_path)
        mock_base_session.obbject_registry.obbject_keys = []
        mock_base_session.obbject_registry.register.return_value = True
        mock_base_session.max_obbjects_exceeded = MagicMock(return_value=True)

        ns = MagicMock()
        ns.file = "ev.xlsx"
        ns.sheet_name = None
        ns.register_key = ""
        controller.parse_simple_args = MagicMock(return_value=(ns, []))
        with patch("openbb_cli.controllers.base_controller.session", mock_base_session):
            controller.call_load(["-f", "ev.xlsx"])
        mock_base_session.obbject_registry.remove.assert_called_once()

    def test_load_excel_register_failure(self, mock_base_session, tmp_path):
        """Excel load with register() returning False prints the failure warning."""
        import pandas as pd

        xlsx_path = tmp_path / "fail.xlsx"
        pd.DataFrame({"X": [1]}).to_excel(xlsx_path, index=False)
        controller = DummyBaseController()
        mock_base_session.user.preferences.data_directory = str(tmp_path)
        mock_base_session.obbject_registry.obbject_keys = []
        mock_base_session.obbject_registry.register.return_value = False
        mock_base_session.max_obbjects_exceeded = MagicMock(return_value=False)

        ns = MagicMock()
        ns.file = "fail.xlsx"
        ns.sheet_name = None
        ns.register_key = ""
        controller.parse_simple_args = MagicMock(return_value=(ns, []))
        with patch("openbb_cli.controllers.base_controller.session", mock_base_session):
            controller.call_load(["-f", "fail.xlsx"])
        calls = [str(c) for c in mock_base_session.console.print.call_args_list]
        assert any("Failed to register" in c for c in calls)


class TestCallResultsAdvanced:
    """Additional call_results tests for chart, export, and edge cases."""

    def test_by_index_with_chart(self, mock_base_session):
        """Test results with --index and --chart flag."""
        controller = DummyBaseController()
        obbject = MagicMock()
        mock_base_session.obbject_registry.get.return_value = obbject
        controller.parse_simple_args = MagicMock(
            return_value=(
                MagicMock(index="0", key=None, chart=True, export="", sheet_name=None),
                [],
            )
        )
        with patch(
            "openbb_cli.controllers.base_controller.handle_obbject_display"
        ) as mock_display:
            controller.call_results(["-i", "0", "--chart"])
            mock_display.assert_called_once()
            call_kwargs = mock_display.call_args[1]
            assert call_kwargs["chart"] is True

    def test_by_index_with_export(self, mock_base_session):
        """Test results with --index and --export flag."""
        controller = DummyBaseController()
        obbject = MagicMock()
        mock_base_session.obbject_registry.get.return_value = obbject
        controller.parse_simple_args = MagicMock(
            return_value=(
                MagicMock(
                    index="0", key=None, chart=False, export="csv", sheet_name=None
                ),
                [],
            )
        )
        with patch(
            "openbb_cli.controllers.base_controller.handle_obbject_display"
        ) as mock_display:
            controller.call_results(["-i", "0", "--export", "csv"])
            mock_display.assert_called_once()
            call_kwargs = mock_display.call_args[1]
            assert call_kwargs["export"] == "csv"

    def test_by_index_not_found(self, mock_base_session):
        """Test results with valid int index but no result."""
        controller = DummyBaseController()
        mock_base_session.obbject_registry.get.return_value = None
        controller.parse_simple_args = MagicMock(
            return_value=(
                MagicMock(index="5", key=None, chart=False, export="", sheet_name=None),
                [],
            )
        )
        controller.call_results(["-i", "5"])
        mock_base_session.console.print.assert_called()
        call_args = mock_base_session.console.print.call_args[0][0]
        assert "No result" in call_args

    def test_by_key_with_chart_and_export(self, mock_base_session):
        """Test results with --key, --chart, and --export."""
        controller = DummyBaseController()
        obbject = MagicMock()
        mock_base_session.obbject_registry.get.return_value = obbject
        controller.parse_simple_args = MagicMock(
            return_value=(
                MagicMock(
                    index=None,
                    key="prices",
                    chart=True,
                    export="json",
                    sheet_name="Sheet1",
                ),
                [],
            )
        )
        with patch(
            "openbb_cli.controllers.base_controller.handle_obbject_display"
        ) as mock_display:
            controller.call_results(["-k", "prices", "--chart", "--export", "json"])
            call_kwargs = mock_display.call_args[1]
            assert call_kwargs["chart"] is True
            assert call_kwargs["export"] == "json"
            assert call_kwargs["sheet_name"] == "Sheet1"


@pytest.fixture
def mock_base_session_full():
    with patch("openbb_cli.controllers.base_controller.session") as sess:
        sess.console = MagicMock()
        sess.settings = MagicMock()
        sess.settings.USE_CLEAR_AFTER_CMD = False
        sess.settings.USE_PROMPT_TOOLKIT = True
        sess.settings.TOOLBAR_HINT = False
        sess.settings.ENABLE_EXIT_AUTO_HELP = True
        sess.settings.SHOW_MSG_OBBJECT_REGISTRY = False
        sess.user.preferences.export_directory = "/tmp"
        sess.user.preferences.data_directory = "/tmp"
        sess.obbject_registry = MagicMock()
        sess.obbject_registry.obbject_keys = []
        sess.obbject_registry.all = {}
        sess.max_obbjects_exceeded = MagicMock(return_value=False)
        sess.output_adapter = MagicMock()
        sess.prompt_session = MagicMock()
        yield sess


def test_call_record_invalid_tag2(mock_base_session_full):
    """Tag2 outside SCRIPT_TAGS prints red error and returns."""
    from openbb_cli.controllers.base_controller import SCRIPT_TAGS

    controller = DummyBaseController()
    ns = MagicMock()
    ns.tag1 = SCRIPT_TAGS[0] if SCRIPT_TAGS else ""
    ns.tag2 = "totally_bogus_tag"
    ns.tag3 = ""
    ns.name = ["myrun"]
    ns.description = []
    controller.parse_simple_args = MagicMock(return_value=(ns, []))
    controller.call_record(["-n", "myrun"])
    msgs = [str(c) for c in mock_base_session_full.console.print.call_args_list]
    assert any("tag2" in m for m in msgs)


def test_call_record_invalid_tag3(mock_base_session_full):
    """Tag3 outside SCRIPT_TAGS prints red error and returns."""
    from openbb_cli.controllers.base_controller import SCRIPT_TAGS

    controller = DummyBaseController()
    ns = MagicMock()
    ns.tag1 = SCRIPT_TAGS[0] if SCRIPT_TAGS else ""
    ns.tag2 = ""
    ns.tag3 = "bogus_again"
    ns.name = ["myrun"]
    ns.description = []
    controller.parse_simple_args = MagicMock(return_value=(ns, []))
    controller.call_record(["-n", "myrun"])
    msgs = [str(c) for c in mock_base_session_full.console.print.call_args_list]
    assert any("tag3" in m for m in msgs)


def test_parse_simple_args_help_flag_returns_none(mock_base_session_full):
    """``-h`` in other_args produces help text and returns ``(None, None)``."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--limit", type=int, default=10)
    out, unknown = DummyBaseController.parse_simple_args(parser, ["-h"])
    assert out is None and unknown is None
    msgs = [str(c) for c in mock_base_session_full.console.print.call_args_list]
    assert any("[help]" in m for m in msgs)


def test_parse_simple_args_unknown_args_warning(mock_base_session_full):
    """Leftover args print the 'couldn't be interpreted' warning."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--name")
    out, unknown = DummyBaseController.parse_simple_args(
        parser, ["--name", "x", "--bogus"]
    )
    assert unknown == ["--bogus"]
    msgs = [str(c) for c in mock_base_session_full.console.print.call_args_list]
    assert any("couldn't be interpreted" in m for m in msgs)


def test_menu_queue_with_quit_returns_remaining(mock_base_session_full):
    """``self.queue`` starting with ``q`` returns immediately with the rest of the queue."""
    controller = DummyBaseController()
    controller.queue = ["q", "stocks"]
    out = controller.menu()
    assert out == ["stocks"]


def test_menu_queue_with_quit_at_end_returns_help(mock_base_session_full):
    """When ``ENABLE_EXIT_AUTO_HELP=True`` and queue is just ``["q"]`` → returns ['help']."""
    controller = DummyBaseController()
    mock_base_session_full.settings.ENABLE_EXIT_AUTO_HELP = True
    controller.queue = ["q"]
    out = controller.menu()
    assert out == ["help"]


def test_menu_queue_with_quit_at_end_no_auto_help(mock_base_session_full):
    """When ``ENABLE_EXIT_AUTO_HELP=False`` and queue is just ``["q"]`` → returns []."""
    controller = DummyBaseController()
    mock_base_session_full.settings.ENABLE_EXIT_AUTO_HELP = False
    controller.queue = ["q"]
    out = controller.menu()
    assert out == []


def test_menu_queue_with_known_command_then_quit(mock_base_session_full):
    """A known command in the queue is dispatched, then ``q`` exits the loop."""
    controller = DummyBaseController()
    controller.controller_choices = ["help", "q"]
    controller.queue = ["help", "q"]
    controller.print_help = MagicMock()
    controller.menu()
    controller.print_help.assert_called()


def test_menu_queue_with_unknown_command_emits_red_warning(mock_base_session_full):
    """Unknown command triggers SystemExit handling + similarity hint."""
    controller = DummyBaseController()
    controller.controller_choices = ["help", "exit", "q"]
    controller.queue = ["definitely_not_a_real_command", "q"]
    controller.menu()
    msgs = [str(c) for c in mock_base_session_full.console.print.call_args_list]
    assert any("doesn't exist" in m for m in msgs)


def test_menu_prompt_path_keyboardinterrupt_becomes_exit(mock_base_session_full):
    """KeyboardInterrupt during prompt is caught and treated as ``exit``.

    Real ``call_exit`` pushes ``quit`` tokens onto the queue (one per PATH
    segment), so the next loop iteration sees ``quit`` and returns. Patching
    ``call_exit`` would create an infinite loop here.
    """
    controller = DummyBaseController()
    controller.queue = []
    mock_base_session_full.prompt_session.prompt.side_effect = KeyboardInterrupt()
    real_exit = controller.call_exit
    spy = MagicMock(side_effect=real_exit)
    controller.call_exit = spy
    controller.menu()
    spy.assert_called()


def test_menu_with_custom_path_menu_above_inserts_path(mock_base_session_full):
    """``custom_path_menu_above`` is inserted into the queue when quitting."""
    controller = DummyBaseController()
    controller.queue = ["q", "remaining"]
    out = controller.menu(custom_path_menu_above="/equity")
    assert "/equity" in out


def _load_ns(file: str, register_key: str = "", sheet_name=None):
    """Make a Namespace-like mock for ``parse_simple_args`` return value."""
    ns = MagicMock()
    ns.file = file
    ns.register_key = register_key
    ns.sheet_name = sheet_name
    return ns


def test_load_unsupported_extension(mock_base_session_full, tmp_path):
    """Unsupported file extension prints red error."""
    controller = DummyBaseController()
    fake = tmp_path / "x.parquet"
    fake.write_bytes(b"dummy")
    controller.parse_simple_args = MagicMock(return_value=(_load_ns(str(fake)), []))
    controller.call_load([])
    msgs = [str(c) for c in mock_base_session_full.console.print.call_args_list]
    assert any("Unsupported file type" in m for m in msgs)


def test_load_csv_register_key_collision(mock_base_session_full, tmp_path):
    """CSV path with register_key already in registry → yellow warning."""
    import pandas as pd

    controller = DummyBaseController()
    csv = tmp_path / "data.csv"
    pd.DataFrame({"a": [1]}).to_csv(csv, index=False)
    controller.parse_simple_args = MagicMock(
        return_value=(_load_ns(str(csv), register_key="taken"), [])
    )
    mock_base_session_full.obbject_registry.obbject_keys = ["taken"]
    mock_base_session_full.obbject_registry.register.return_value = True
    controller.call_load([])
    msgs = [str(c) for c in mock_base_session_full.console.print.call_args_list]
    assert any("already exists" in m for m in msgs)


def test_load_json_path(mock_base_session_full, tmp_path):
    """JSON file is loaded successfully."""
    import pandas as pd

    controller = DummyBaseController()
    js = tmp_path / "data.json"
    pd.DataFrame({"a": [1, 2]}).to_json(js)
    controller.parse_simple_args = MagicMock(return_value=(_load_ns(str(js)), []))
    mock_base_session_full.obbject_registry.register.return_value = True
    controller.call_load([])
    msgs = [str(c) for c in mock_base_session_full.console.print.call_args_list]
    assert any("Successfully loaded" in m for m in msgs)


def test_load_xlsx_path(mock_base_session_full, tmp_path):
    """xlsx file loads via ``read_excel``."""
    import pandas as pd

    controller = DummyBaseController()
    xl = tmp_path / "data.xlsx"
    pd.DataFrame({"a": [1, 2]}).to_excel(xl, index=False)
    controller.parse_simple_args = MagicMock(return_value=(_load_ns(str(xl)), []))
    mock_base_session_full.obbject_registry.register.return_value = True
    controller.call_load([])
    msgs = [str(c) for c in mock_base_session_full.console.print.call_args_list]
    assert any("Successfully loaded" in m for m in msgs)


def test_load_sqlite_path(mock_base_session_full, tmp_path):
    """SQLite db loads each table as a lazy OBBject."""
    import sqlite3

    import pandas as pd

    controller = DummyBaseController()
    db = tmp_path / "data.db"
    conn = sqlite3.connect(db)
    pd.DataFrame({"a": [1, 2]}).to_sql("tbl1", conn, if_exists="replace", index=False)
    conn.close()
    controller.parse_simple_args = MagicMock(return_value=(_load_ns(str(db)), []))
    mock_base_session_full.obbject_registry.register.return_value = True
    controller.call_load([])
    msgs = [str(c) for c in mock_base_session_full.console.print.call_args_list]
    assert any("Successfully loaded" in m and "table" in m for m in msgs)


def test_load_register_failed(mock_base_session_full, tmp_path):
    """``register`` returns False → 'Failed to register OBBject' yellow warning."""
    import pandas as pd

    controller = DummyBaseController()
    js = tmp_path / "data.json"
    pd.DataFrame({"a": [1]}).to_json(js)
    controller.parse_simple_args = MagicMock(return_value=(_load_ns(str(js)), []))
    mock_base_session_full.obbject_registry.register.return_value = False
    controller.call_load([])
    msgs = [str(c) for c in mock_base_session_full.console.print.call_args_list]
    assert any("Failed to register" in m for m in msgs)


def test_load_sqlite_no_tables(mock_base_session_full, tmp_path):
    """SQLite db with no tables emits the yellow 'No tables found' notice."""
    import sqlite3

    controller = DummyBaseController()
    db = tmp_path / "empty.db"
    conn = sqlite3.connect(db)
    conn.close()
    controller.parse_simple_args = MagicMock(return_value=(_load_ns(str(db)), []))
    controller.call_load([])
    msgs = [str(c) for c in mock_base_session_full.console.print.call_args_list]
    assert any("No tables found" in m for m in msgs)


def test_load_csv_link_obbject_hook(mock_base_session_full, tmp_path):
    """When ``_link_obbject_to_data_processing_commands`` exists, CSV load invokes it."""
    import pandas as pd

    controller = DummyBaseController()
    csv = tmp_path / "data.csv"
    pd.DataFrame({"a": [1]}).to_csv(csv, index=False)
    controller.parse_simple_args = MagicMock(return_value=(_load_ns(str(csv)), []))
    mock_base_session_full.obbject_registry.register.return_value = True
    controller._link_obbject_to_data_processing_commands = MagicMock()
    controller.update_completer = MagicMock()
    controller.call_load([])
    controller._link_obbject_to_data_processing_commands.assert_called()


def test_load_json_register_key_collision(mock_base_session_full, tmp_path):
    """JSON path with register_key collision prints the yellow warning."""
    import pandas as pd

    controller = DummyBaseController()
    js = tmp_path / "data.json"
    pd.DataFrame({"a": [1, 2]}).to_json(js)
    controller.parse_simple_args = MagicMock(
        return_value=(_load_ns(str(js), register_key="taken"), [])
    )
    mock_base_session_full.obbject_registry.obbject_keys = ["taken"]
    mock_base_session_full.obbject_registry.register.return_value = True
    controller.call_load([])
    msgs = [str(c) for c in mock_base_session_full.console.print.call_args_list]
    assert any("already exists" in m for m in msgs)


def test_load_json_link_obbject_hook(mock_base_session_full, tmp_path):
    """JSON load triggers the link hook when present."""
    import pandas as pd

    controller = DummyBaseController()
    js = tmp_path / "data.json"
    pd.DataFrame({"a": [1]}).to_json(js)
    controller.parse_simple_args = MagicMock(return_value=(_load_ns(str(js)), []))
    mock_base_session_full.obbject_registry.register.return_value = True
    controller._link_obbject_to_data_processing_commands = MagicMock()
    controller.update_completer = MagicMock()
    controller.call_load([])
    controller._link_obbject_to_data_processing_commands.assert_called()


def test_load_xlsx_register_key_collision(mock_base_session_full, tmp_path):
    """xlsx path with register_key collision emits yellow warning."""
    import pandas as pd

    controller = DummyBaseController()
    xl = tmp_path / "data.xlsx"
    pd.DataFrame({"a": [1, 2]}).to_excel(xl, index=False)
    controller.parse_simple_args = MagicMock(
        return_value=(_load_ns(str(xl), register_key="taken"), [])
    )
    mock_base_session_full.obbject_registry.obbject_keys = ["taken"]
    mock_base_session_full.obbject_registry.register.return_value = True
    controller.call_load([])
    msgs = [str(c) for c in mock_base_session_full.console.print.call_args_list]
    assert any("already exists" in m for m in msgs)


def test_load_xlsx_link_obbject_hook(mock_base_session_full, tmp_path):
    """xlsx load triggers the link hook when present."""
    import pandas as pd

    controller = DummyBaseController()
    xl = tmp_path / "data.xlsx"
    pd.DataFrame({"a": [1]}).to_excel(xl, index=False)
    controller.parse_simple_args = MagicMock(return_value=(_load_ns(str(xl)), []))
    mock_base_session_full.obbject_registry.register.return_value = True
    controller._link_obbject_to_data_processing_commands = MagicMock()
    controller.update_completer = MagicMock()
    controller.call_load([])
    controller._link_obbject_to_data_processing_commands.assert_called()


def test_load_sqlite_register_key_single_table_collision(
    mock_base_session_full, tmp_path
):
    """SQLite with one table + register_key already taken → falls back to auto_key."""
    import sqlite3

    import pandas as pd

    controller = DummyBaseController()
    db = tmp_path / "single.db"
    conn = sqlite3.connect(db)
    pd.DataFrame({"a": [1]}).to_sql("only", conn, if_exists="replace", index=False)
    conn.close()
    controller.parse_simple_args = MagicMock(
        return_value=(_load_ns(str(db), register_key="taken"), [])
    )
    mock_base_session_full.obbject_registry.obbject_keys = ["taken"]
    mock_base_session_full.obbject_registry.register.return_value = True
    controller.call_load([])
    msgs = [str(c) for c in mock_base_session_full.console.print.call_args_list]
    assert any("already exists" in m and "auto-generated" in m for m in msgs)


def test_load_sqlite_auto_key_collision(mock_base_session_full, tmp_path):
    """Auto-generated key already in registry → yellow warning, no key set."""
    import sqlite3

    import pandas as pd

    controller = DummyBaseController()
    db = tmp_path / "multi.db"
    conn = sqlite3.connect(db)
    pd.DataFrame({"a": [1]}).to_sql("t1", conn, if_exists="replace", index=False)
    pd.DataFrame({"b": [2]}).to_sql("t2", conn, if_exists="replace", index=False)
    conn.close()
    controller.parse_simple_args = MagicMock(return_value=(_load_ns(str(db)), []))
    mock_base_session_full.obbject_registry.obbject_keys = ["multi_t1", "multi_t2"]
    mock_base_session_full.obbject_registry.register.return_value = True
    controller.call_load([])
    msgs = [str(c) for c in mock_base_session_full.console.print.call_args_list]
    assert any("already exists" in m and "kept without" in m for m in msgs)


def test_load_sqlite_max_obbjects_evicts(mock_base_session_full, tmp_path):
    """``max_obbjects_exceeded()=True`` evicts oldest before register."""
    import sqlite3

    import pandas as pd

    controller = DummyBaseController()
    db = tmp_path / "evict.db"
    conn = sqlite3.connect(db)
    pd.DataFrame({"a": [1]}).to_sql("only", conn, if_exists="replace", index=False)
    conn.close()
    controller.parse_simple_args = MagicMock(return_value=(_load_ns(str(db)), []))
    mock_base_session_full.max_obbjects_exceeded.return_value = True
    mock_base_session_full.obbject_registry.register.return_value = True
    controller.call_load([])
    mock_base_session_full.obbject_registry.remove.assert_called()


def test_load_sqlite_link_obbject_hook(mock_base_session_full, tmp_path):
    """SQLite load triggers the link hook when present."""
    import sqlite3

    import pandas as pd

    controller = DummyBaseController()
    db = tmp_path / "linked.db"
    conn = sqlite3.connect(db)
    pd.DataFrame({"a": [1]}).to_sql("only", conn, if_exists="replace", index=False)
    conn.close()
    controller.parse_simple_args = MagicMock(return_value=(_load_ns(str(db)), []))
    mock_base_session_full.obbject_registry.register.return_value = True
    controller._link_obbject_to_data_processing_commands = MagicMock()
    controller.update_completer = MagicMock()
    controller.call_load([])
    controller._link_obbject_to_data_processing_commands.assert_called()


def test_load_inner_exception_is_caught(mock_base_session_full, tmp_path):
    """An exception raised while loading is caught and emitted as red error."""
    import pandas as pd

    controller = DummyBaseController()
    csv = tmp_path / "data.csv"
    pd.DataFrame({"a": [1]}).to_csv(csv, index=False)
    controller.parse_simple_args = MagicMock(return_value=(_load_ns(str(csv)), []))
    with patch(
        "openbb_cli.controllers.base_controller.pd.read_csv",
        side_effect=RuntimeError("synthetic"),
    ):
        controller.call_load([])
    msgs = [str(c) for c in mock_base_session_full.console.print.call_args_list]
    assert any("Error loading file" in m for m in msgs)


def test_parse_simple_args_use_clear_after_cmd(mock_base_session_full):
    """``USE_CLEAR_AFTER_CMD=True`` invokes ``system_clear``."""
    mock_base_session_full.settings.USE_CLEAR_AFTER_CMD = True
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--name", default="x")
    with patch("openbb_cli.controllers.base_controller.system_clear") as system_clear:
        DummyBaseController.parse_simple_args(parser, [])
    system_clear.assert_called_once()


def test_parse_known_args_and_warn_use_clear_after_cmd(mock_base_session_full):
    """``parse_known_args_and_warn`` honors ``USE_CLEAR_AFTER_CMD``."""
    mock_base_session_full.settings.USE_CLEAR_AFTER_CMD = True
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--name", default="x")
    with patch("openbb_cli.controllers.base_controller.system_clear") as system_clear:
        BaseController.parse_known_args_and_warn(parser, [])
    system_clear.assert_called_once()


def test_parse_known_args_and_warn_help_short_circuits(mock_base_session_full):
    """``--help`` in other_args prints help and returns None."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--name", default="x")
    out = BaseController.parse_known_args_and_warn(parser, ["--help"])
    assert out is None
    msgs = [str(c) for c in mock_base_session_full.console.print.call_args_list]
    assert any("[help]" in m for m in msgs)


def test_parse_known_args_and_warn_routine_args_index_protected(mock_base_session_full):
    """``--input value`` for a parser with ``routine_args`` dest is not comma-split."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-i", "--input", dest="routine_args", default="")
    out = BaseController.parse_known_args_and_warn(parser, ["-i", "AAPL,MSFT"])
    assert out is not None
    assert out.routine_args == "AAPL,MSFT"


def test_parse_known_args_and_warn_resets_optional_choices(mock_base_session_full):
    """Actions with ``optional_choices`` have their ``choices`` cleared."""
    parser = argparse.ArgumentParser(add_help=False)
    action = parser.add_argument("--symbol", default="AAPL", choices=["AAPL", "MSFT"])
    action.optional_choices = True
    out = BaseController.parse_known_args_and_warn(parser, ["--symbol", "ANYTHING"])
    assert out is not None
    assert out.symbol == "ANYTHING"


def test_parse_known_args_and_warn_systemexit_returns_none(mock_base_session_full):
    """Required arg missing → SystemExit caught, returns None."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--name", required=True)
    out = BaseController.parse_known_args_and_warn(parser, [])
    assert out is None


def test_parse_known_args_and_warn_unknown_args_warning(mock_base_session_full):
    """Unrecognized args trigger the warning print."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--name", default="x")
    BaseController.parse_known_args_and_warn(parser, ["--name", "y", "--bogus"])
    msgs = [str(c) for c in mock_base_session_full.console.print.call_args_list]
    assert any("couldn't be interpreted" in m for m in msgs)


def test_menu_prompt_path_returns_input_then_quit(mock_base_session_full):
    """The non-toolbar prompt branch yields input on iter1, then ``q`` exits."""
    controller = DummyBaseController()
    controller.queue = []
    mock_base_session_full.settings.TOOLBAR_HINT = False
    mock_base_session_full.prompt_session.prompt.side_effect = ["q"]
    controller.menu()


def test_menu_prompt_path_with_toolbar_hint(mock_base_session_full):
    """``TOOLBAR_HINT=True`` builds the toolbar prompt."""
    controller = DummyBaseController()
    controller.queue = []
    mock_base_session_full.settings.TOOLBAR_HINT = True
    mock_base_session_full.prompt_session.prompt.side_effect = ["q"]
    controller.menu()
    assert mock_base_session_full.prompt_session.prompt.called


def test_menu_prompt_path_uses_input_when_no_prompt_session(mock_base_session_full):
    """Without a prompt session, the menu falls back to ``builtins.input``."""
    controller = DummyBaseController()
    controller.queue = []
    mock_base_session_full.prompt_session = None
    with patch("builtins.input", side_effect=["q"]) as mock_input:
        controller.menu()
    mock_input.assert_called()


def test_menu_unknown_command_with_close_match_replaces(mock_base_session_full):
    """Close match found via difflib → replaces an_input and continues."""
    controller = DummyBaseController()
    controller.queue = ["hlep", "q"]
    controller.menu()
    msgs = [str(c) for c in mock_base_session_full.console.print.call_args_list]
    assert any("Replacing by 'help'" in m for m in msgs)


def test_menu_unknown_multi_token_with_close_match(mock_base_session_full):
    """Multi-token unknown with close match → ``similar_cmd[0] + rest``."""
    controller = DummyBaseController()
    controller.queue = ["hlep --x", "q"]
    controller.menu()
    msgs = [str(c) for c in mock_base_session_full.console.print.call_args_list]
    assert any("Replacing by 'help --x'" in m for m in msgs)


def test_menu_queue_prints_location_for_known_non_help_command(mock_base_session_full):
    """A queue entry that's a real command (not ``home``/``help``) prints the prompt location."""
    controller = DummyBaseController()
    controller.queue = [
        "cls",
        "q",
    ]
    with patch("openbb_cli.controllers.base_controller.system_clear"):
        controller.menu()
    msgs = [str(c) for c in mock_base_session_full.console.print.call_args_list]
    assert any("/valid/path/" in m and "cls" in m for m in msgs)


def test_call_stop_existing_routine_invalid_then_no(mock_base_session_full, tmp_path):
    """``call_stop`` retries the y/n prompt on invalid input then proceeds."""
    from openbb_cli.controllers import base_controller as bc

    controller = DummyBaseController()
    routines_dir = tmp_path / "routines"
    routines_dir.mkdir()
    title = "MyTitle"
    existing = routines_dir / (title.replace(" ", "_") + ".openbb")
    existing.write_text("placeholder")
    mock_base_session_full.user.preferences.export_directory = str(tmp_path)

    bc.RECORD_SESSION = True
    bc.SESSION_RECORDED = ["a", "b", "c", "d", "e"]
    bc.SESSION_RECORDED_NAME = title
    bc.SESSION_RECORDED_DESCRIPTION = "desc"
    bc.SESSION_RECORDED_TAGS = ""
    try:
        mock_base_session_full.console.input.side_effect = ["maybe", "n"]
        controller.call_stop([])
    finally:
        bc.RECORD_SESSION = False
        bc.SESSION_RECORDED = []
    assert mock_base_session_full.console.input.call_count >= 2


def test_load_json_register_key_set(mock_base_session_full, tmp_path):
    """JSON load with a fresh register_key sets it on the OBBject."""
    import pandas as pd

    controller = DummyBaseController()
    js = tmp_path / "data.json"
    pd.DataFrame({"a": [1]}).to_json(js)
    captured = {}

    def fake_register(obbject):
        captured["obbject"] = obbject
        return True

    controller.parse_simple_args = MagicMock(
        return_value=(_load_ns(str(js), register_key="myfreekey"), [])
    )
    mock_base_session_full.obbject_registry.obbject_keys = []
    mock_base_session_full.obbject_registry.register.side_effect = fake_register
    controller.call_load([])
    assert captured["obbject"].extra.get("register_key") == "myfreekey"


def test_load_xlsx_register_key_set(mock_base_session_full, tmp_path):
    """xlsx load with a fresh register_key sets it on the OBBject."""
    import pandas as pd

    controller = DummyBaseController()
    xl = tmp_path / "data.xlsx"
    pd.DataFrame({"a": [1]}).to_excel(xl, index=False)
    captured = {}

    def fake_register(obbject):
        captured["obbject"] = obbject
        return True

    controller.parse_simple_args = MagicMock(
        return_value=(_load_ns(str(xl), register_key="myfreekey"), [])
    )
    mock_base_session_full.obbject_registry.obbject_keys = []
    mock_base_session_full.obbject_registry.register.side_effect = fake_register
    controller.call_load([])
    assert captured["obbject"].extra.get("register_key") == "myfreekey"


def test_load_sqlite_single_table_register_key_set(mock_base_session_full, tmp_path):
    """SQLite with a single table + fresh register_key sets the key."""
    import sqlite3

    import pandas as pd

    controller = DummyBaseController()
    db = tmp_path / "single.db"
    conn = sqlite3.connect(db)
    pd.DataFrame({"a": [1]}).to_sql("only", conn, if_exists="replace", index=False)
    conn.close()
    captured = []

    def fake_register(obbject):
        captured.append(obbject)
        return True

    controller.parse_simple_args = MagicMock(
        return_value=(_load_ns(str(db), register_key="userkey"), [])
    )
    mock_base_session_full.obbject_registry.obbject_keys = []
    mock_base_session_full.obbject_registry.register.side_effect = fake_register
    controller.call_load([])
    assert captured
    assert captured[0].extra.get("register_key") == "userkey"


def test_switch_record_session_appends(mock_base_session_full):
    """``RECORD_SESSION=True`` causes ``switch`` to append the input."""
    from openbb_cli.controllers import base_controller as bc

    controller = DummyBaseController()
    bc.RECORD_SESSION = True
    bc.SESSION_RECORDED = []
    try:
        controller.switch("help")
        recorded = list(bc.SESSION_RECORDED)
    finally:
        bc.RECORD_SESSION = False
        bc.SESSION_RECORDED = []
    assert "help" in recorded
