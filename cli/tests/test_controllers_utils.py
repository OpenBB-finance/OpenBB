"""Test the Controller utils."""

import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from openbb_cli.controllers.utils import (
    check_file_type_saved,
    check_non_negative,
    check_positive,
    get_flair_and_username,
    get_user_agent,
    parse_and_split_input,
    parse_unknown_args_to_dict,
    print_goodbye,
    remove_file,
    return_colored_value,
    suppress_stdout,
    validate_register_key,
    welcome_message,
)


@pytest.fixture
def mock_session():
    """Mock the session and its dependencies."""
    with patch("openbb_cli.controllers.utils.session") as mock_session:
        mock_session.console.print = MagicMock()
        mock_session.settings.VERSION = "1.0"
        mock_session.settings.FLAIR = "rocket"
        yield mock_session


def test_remove_file_existing_file():
    """Test removing an existing file."""
    with patch("os.path.isfile", return_value=True), patch("os.remove") as mock_remove:
        assert remove_file(Path("/path/to/file"))
        mock_remove.assert_called_once()


def test_remove_file_directory():
    """Test removing a directory."""
    with (
        patch("os.path.isfile", return_value=False),
        patch("os.path.isdir", return_value=True),
        patch("shutil.rmtree") as mock_rmtree,
    ):
        assert remove_file(Path("/path/to/directory"))
        mock_rmtree.assert_called_once()


def test_remove_file_failure(mock_session):
    """Test removing a file that fails."""
    with (
        patch("os.path.isfile", return_value=True),
        patch("os.remove", side_effect=Exception("Error")),
    ):
        assert not remove_file(Path("/path/to/file"))
        mock_session.console.print.assert_called()


def test_print_goodbye(mock_session):
    """Test printing the goodbye message."""
    print_goodbye()
    mock_session.console.print.assert_called()


def test_parse_and_split_input():
    """Test parsing and splitting user input."""
    user_input = "ls -f /home/user/docs/document.xlsx"
    result = parse_and_split_input(user_input, [])
    assert "ls" in result[0]


@pytest.mark.parametrize(
    "input_command, expected_output",
    [
        ("/", ["home"]),
        ("ls -f /path/to/file.txt", ["ls -f ", "path", "to", "file.txt"]),
        ("rm -f /home/user/docs", ["rm -f ", "home", "user", "docs"]),
    ],
)
def test_parse_and_split_input_special_cases(input_command, expected_output):
    """Test parsing and splitting user input with special cases."""
    result = parse_and_split_input(input_command, [])
    assert result == expected_output


def test_welcome_message(mock_session):
    """Test printing the welcome message."""
    welcome_message()
    mock_session.console.print.assert_called_with(
        "\nWelcome to OpenBB Platform CLI v1.0"
    )


def test_get_flair_and_username(mock_session):
    """Test getting the flair and username."""
    result = get_flair_and_username()
    assert "rocket" in result


@pytest.mark.parametrize(
    "value, expected",
    [
        ("10", 10),
        ("0", 0),
        ("-1", pytest.raises(argparse.ArgumentTypeError)),
        ("text", pytest.raises(ValueError)),
    ],
)
def test_check_non_negative(value, expected):
    """Test checking for a non-negative value."""
    if isinstance(expected, int):
        assert check_non_negative(value) == expected
    else:
        with expected:
            check_non_negative(value)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("1", 1),
        ("0", pytest.raises(argparse.ArgumentTypeError)),
        ("-1", pytest.raises(argparse.ArgumentTypeError)),
        ("text", pytest.raises(ValueError)),
    ],
)
def test_check_positive(value, expected):
    """Test checking for a positive value."""
    if isinstance(expected, int):
        assert check_positive(value) == expected
    else:
        with expected:
            check_positive(value)


def test_get_user_agent():
    """Test getting the user agent."""
    result = get_user_agent()
    assert result.startswith("Mozilla/5.0")


@pytest.mark.parametrize(
    "value, expected_color",
    [
        ("10.5", "green"),
        ("-3.2", "red"),
        ("0", "yellow"),
        ("0.0", "yellow"),
        ("no numbers here", ""),
        ("abc 1 def 2", ""),
    ],
)
def test_return_colored_value(value, expected_color):
    """Test return_colored_value applies correct color."""
    result = return_colored_value(value)
    if expected_color:
        assert f"[{expected_color}]" in result
    else:
        assert "[green]" not in result
        assert "[red]" not in result


import sys


def test_suppress_stdout():
    """Test that suppress_stdout redirects stdout and stderr."""
    original_out = sys.stdout
    original_err = sys.stderr
    with suppress_stdout():
        assert sys.stdout is not original_out
        assert sys.stderr is not original_err
    assert sys.stdout is original_out
    assert sys.stderr is original_err


from openbb_cli.controllers.utils import bootup


def test_bootup_runs_without_error(mock_session):
    """Test that bootup completes without raising."""
    bootup()


from openbb_cli.controllers.utils import first_time_user


def test_first_time_user_empty_env(mock_session, tmp_path):
    """Test first_time_user returns True for empty env file."""
    env_file = tmp_path / ".env"
    env_file.write_text("")
    with patch("openbb_cli.controllers.utils.ENV_FILE_SETTINGS", env_file):
        result = first_time_user()
    assert result is True
    mock_session.settings.set_item.assert_called_once_with("PREVIOUS_USE", True)


def test_first_time_user_non_empty_env(mock_session, tmp_path):
    """Test first_time_user returns False for non-empty env file."""
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=VALUE\n")
    with patch("openbb_cli.controllers.utils.ENV_FILE_SETTINGS", env_file):
        result = first_time_user()
    assert result is False


@pytest.mark.parametrize(
    "args, expected",
    [
        (["--key", "value"], {"key": "value"}),
        (["--a", "1", "--b", "hello"], {"a": 1, "b": "hello"}),
        (["--flag"], {}),
        (None, {}),
        ([], {}),
    ],
)
def test_parse_unknown_args_to_dict_basic(args, expected, mock_session):
    """Test basic key-value parsing and edge cases."""
    result = parse_unknown_args_to_dict(args)
    assert result == expected


@pytest.mark.parametrize(
    "args, expected",
    [
        (["--num", "42"], {"num": 42}),
        (["--pi", "3.14"], {"pi": 3.14}),
        (["--items", "[1, 2, 3]"], {"items": [1, 2, 3]}),
        (["--mapping", "{'a': 1}"], {"mapping": {"a": 1}}),
        (["--bool", "True"], {"bool": True}),
        (["--plain", "not-a-literal"], {"plain": "not-a-literal"}),
    ],
)
def test_parse_unknown_args_to_dict_literal_eval(args, expected, mock_session):
    """Test that ast.literal_eval correctly parses typed values."""
    result = parse_unknown_args_to_dict(args)
    assert result == expected


def test_parse_unknown_args_to_dict_missing_value(mock_session):
    """Test that a trailing --flag with no value prints a warning."""
    result = parse_unknown_args_to_dict(["--orphan"])
    assert result == {}
    mock_session.console.print.assert_called_once()


@pytest.mark.parametrize(
    "key, should_raise",
    [
        ("my_api_key", False),
        ("secret_123", False),
        ("OBB_KEY", True),
        ("my_OBB_key", True),
        ("OBB", True),
    ],
)
def test_validate_register_key(key, should_raise):
    """Test that keys containing 'OBB' are rejected."""
    if should_raise:
        with pytest.raises(argparse.ArgumentTypeError, match="OBB"):
            validate_register_key(key)
    else:
        assert validate_register_key(key) == key


def test_check_file_type_saved_valid(mock_session):
    """Test valid filenames are accepted."""
    checker = check_file_type_saved(valid_types=[".csv", ".json"])
    assert checker("report.csv") == "report.csv"
    assert checker("data.json") == "data.json"
    assert checker("a.csv,b.json") == "a.csv,b.json"


def test_check_file_type_saved_invalid(mock_session):
    """Test invalid filenames are rejected with a warning."""
    checker = check_file_type_saved(valid_types=[".csv"])
    result = checker("report.xlsx")
    assert result == ""
    mock_session.console.print.assert_called()


def test_check_file_type_saved_empty(mock_session):
    """Test empty input returns empty string."""
    checker = check_file_type_saved(valid_types=[".csv"])
    assert checker("") == ""
    assert checker() == ""


def test_check_file_type_saved_no_valid_types(mock_session):
    """Test that None valid_types returns empty string."""
    checker = check_file_type_saved(valid_types=None)
    assert checker("anything.csv") == ""


def test_compose_export_path_with_normal_directory(mock_session, tmp_path):
    """Builds ``<export_dir>/<timestamp>_<dir-segments>_<func>``."""
    from openbb_cli.controllers.utils import compose_export_path

    mock_session.user.preferences.export_directory = str(tmp_path)
    parent = tmp_path / "stocks"
    sub = parent / "fundamentals"
    sub.mkdir(parents=True)
    result = compose_export_path("balance", str(sub))
    assert result.parent == tmp_path
    assert "stocks_fundamentals_balance" in result.name


def test_compose_export_path_collapses_openbb_cli_directory(mock_session, tmp_path):
    """When the parent dir is ``openbb_cli``, only the last path segment is used."""
    from openbb_cli.controllers.utils import compose_export_path

    mock_session.user.preferences.export_directory = str(tmp_path)
    fake_root = tmp_path / "openbb_cli" / "controllers"
    fake_root.mkdir(parents=True)
    result = compose_export_path("foo", str(fake_root))
    assert "controllers_foo" in result.name
    assert "openbb_cli" not in result.name


def test_ask_file_overwrite_when_overwrite_setting_enabled(mock_session, tmp_path):
    """``settings.FILE_OVERWRITE=True`` → no prompt, return (False, True)."""
    from openbb_cli.controllers.utils import ask_file_overwrite

    mock_session.settings.FILE_OVERWRITE = True
    f = tmp_path / "a.txt"
    f.write_text("x")
    assert ask_file_overwrite(f) == (False, True)


def test_ask_file_overwrite_in_test_mode(mock_session, tmp_path):
    """``TEST_MODE=True`` short-circuits to (False, True)."""
    from openbb_cli.controllers.utils import ask_file_overwrite

    mock_session.settings.FILE_OVERWRITE = False
    mock_session.settings.TEST_MODE = True
    f = tmp_path / "a.txt"
    f.write_text("x")
    assert ask_file_overwrite(f) == (False, True)


def test_ask_file_overwrite_user_yes(mock_session, tmp_path):
    """User answers 'y' → file is unlinked and (True, True) is returned."""
    from openbb_cli.controllers.utils import ask_file_overwrite

    mock_session.settings.FILE_OVERWRITE = False
    mock_session.settings.TEST_MODE = False
    f = tmp_path / "a.txt"
    f.write_text("x")
    with patch("builtins.input", return_value="y"):
        result = ask_file_overwrite(f)
    assert result == (True, True)
    assert not f.exists()


def test_ask_file_overwrite_user_no(mock_session, tmp_path):
    """User answers 'n' → file untouched, (True, False) returned."""
    from openbb_cli.controllers.utils import ask_file_overwrite

    mock_session.settings.FILE_OVERWRITE = False
    mock_session.settings.TEST_MODE = False
    f = tmp_path / "a.txt"
    f.write_text("x")
    with patch("builtins.input", return_value="n"):
        result = ask_file_overwrite(f)
    assert result == (True, False)
    assert f.exists()


def test_ask_file_overwrite_missing_file(mock_session, tmp_path):
    """Missing file → no prompt, (False, True)."""
    from openbb_cli.controllers.utils import ask_file_overwrite

    mock_session.settings.FILE_OVERWRITE = False
    mock_session.settings.TEST_MODE = False
    f = tmp_path / "missing.txt"
    assert ask_file_overwrite(f) == (False, True)


def test_request_invalid_method_raises():
    """Unknown HTTP method raises ValueError."""
    from openbb_cli.controllers.utils import request

    with pytest.raises(ValueError, match="Invalid method"):
        request("https://example.com", method="bogus")


def test_request_adds_user_agent_when_missing(mock_session):
    """``request`` injects a User-Agent header when none is supplied."""
    from openbb_cli.controllers.utils import request

    mock_session.user.preferences.request_timeout = 5
    with patch("openbb_cli.controllers.utils.requests") as req_mod:
        req_mod.get.return_value = MagicMock(status_code=200)
        request("https://example.com")
    headers = req_mod.get.call_args[1]["headers"]
    assert "User-Agent" in headers


def test_request_preserves_user_supplied_user_agent(mock_session):
    """Caller-provided User-Agent is not overwritten."""
    from openbb_cli.controllers.utils import request

    mock_session.user.preferences.request_timeout = 5
    with patch("openbb_cli.controllers.utils.requests") as req_mod:
        req_mod.post.return_value = MagicMock(status_code=200)
        request(
            "https://example.com",
            method="post",
            headers={"User-Agent": "custom"},
        )
    headers = req_mod.post.call_args[1]["headers"]
    assert headers["User-Agent"] == "custom"


def test_system_clear_invokes_os_system():
    """``system_clear`` calls ``os.system`` with the cls/clear command."""
    from openbb_cli.controllers.utils import system_clear

    with patch("openbb_cli.controllers.utils.os.system") as os_system:
        system_clear()
    os_system.assert_called_once_with("cls||clear")


def test_save_to_excel_creates_new_file(mock_session, tmp_path):
    """When the path doesn't exist yet, ``save_to_excel`` creates the workbook."""
    import pandas as pd

    from openbb_cli.controllers.utils import save_to_excel

    df = pd.DataFrame({"a": [1, 2]})
    saved = tmp_path / "out.xlsx"
    save_to_excel(df, saved, sheet_name="Sheet1")
    assert saved.exists()


def test_handle_obbject_display_normal_path_uses_output_adapter(
    mock_session, sample_df_helper
):
    """Non-chart, non-interactive path goes through the session's output adapter."""

    from openbb_cli.controllers.utils import handle_obbject_display

    mock_session.settings.USE_INTERACTIVE_DF = False
    obbject = MagicMock()
    obbject.results = sample_df_helper
    obbject.extra = {"command": "/equity/quote"}
    obbject.chart = None
    obbject.to_dataframe.return_value = sample_df_helper

    with patch(
        "openbb_cli.controllers.utils.extract_dataframe", return_value=sample_df_helper
    ):
        handle_obbject_display(obbject)
    mock_session.output_adapter.display.assert_called_once()


def test_handle_obbject_display_chart_path(mock_session):
    """``chart=True`` calls ``obbject.show()`` when a chart is present."""
    from openbb_cli.controllers.utils import handle_obbject_display

    obbject = MagicMock()
    obbject.chart = MagicMock()
    obbject.results = MagicMock()
    obbject.extra = {}
    obbject.show = MagicMock()
    handle_obbject_display(obbject, chart=True)
    obbject.show.assert_called_once()


def test_handle_obbject_display_chart_failure_logs(mock_session):
    """Chart display failure prints a console error but doesn't propagate."""
    from openbb_cli.controllers.utils import handle_obbject_display

    obbject = MagicMock()
    obbject.chart = MagicMock()
    obbject.results = MagicMock()
    obbject.extra = {}
    obbject.show.side_effect = Exception("no chart")
    handle_obbject_display(obbject, chart=True)
    mock_session.console.print.assert_called()


def test_handle_obbject_display_sqlite_results_materialized(
    mock_session, sample_df_helper
):
    """SQLiteTable results are eagerly materialized to a DataFrame before downstream use."""
    from openbb_cli.controllers.utils import SQLiteTable, handle_obbject_display

    obbject = MagicMock()
    obbject.extra = {"command": "/foo"}
    obbject.chart = None
    sqlite_tbl = MagicMock(spec=SQLiteTable)
    sqlite_tbl.to_dataframe.return_value = sample_df_helper
    obbject.results = sqlite_tbl
    mock_session.settings.USE_INTERACTIVE_DF = False
    with patch(
        "openbb_cli.controllers.utils.extract_dataframe", return_value=sample_df_helper
    ):
        handle_obbject_display(obbject)
    sqlite_tbl.to_dataframe.assert_called_once()


def test_handle_obbject_display_chart_no_chart_calls_to_chart(mock_session):
    """When ``obbject.chart`` is None and chart=True, ``charting.to_chart`` is invoked."""
    from openbb_cli.controllers.utils import handle_obbject_display

    obbject = MagicMock()
    obbject.chart = None
    obbject.results = MagicMock()
    obbject.extra = {}
    handle_obbject_display(obbject, chart=True)
    obbject.charting.to_chart.assert_called_once()


def test_handle_obbject_display_export_with_data(
    mock_session, sample_df_helper, tmp_path
):
    """``export=...`` and a non-empty DataFrame call ``export_data`` with the assembled func_name."""
    from openbb_cli.controllers.utils import handle_obbject_display

    obbject = MagicMock()
    obbject.chart = None
    obbject.results = sample_df_helper
    obbject.extra = {"command": "/equity/quote --symbol AAPL"}
    mock_session.settings.USE_INTERACTIVE_DF = False
    with (
        patch(
            "openbb_cli.controllers.utils.extract_dataframe",
            return_value=sample_df_helper,
        ),
        patch("openbb_cli.controllers.utils.export_data") as export_data,
    ):
        handle_obbject_display(obbject, export="csv")
    export_data.assert_called_once()
    func_name = export_data.call_args[1]["func_name"]
    assert "equity" in func_name and "quote" in func_name
    assert "/" not in func_name
    assert " " not in func_name


def test_handle_obbject_display_export_with_empty_data_warns(mock_session):
    """``export=...`` with an empty DataFrame prints a 'No data to export' warning."""
    from openbb_cli.controllers.utils import handle_obbject_display

    obbject = MagicMock()
    obbject.chart = None
    obbject.results = None
    obbject.extra = {"command": "/x"}
    import pandas as pd

    mock_session.settings.USE_INTERACTIVE_DF = False
    with patch(
        "openbb_cli.controllers.utils.extract_dataframe",
        return_value=pd.DataFrame(),
    ):
        handle_obbject_display(obbject, export="csv")
    calls = [str(c) for c in mock_session.console.print.call_args_list]
    assert any("No data to export" in c for c in calls)


def test_handle_obbject_display_export_with_sheet_name_list(
    mock_session, sample_df_helper
):
    """``sheet_name`` passed as a list is unwrapped to its first element."""
    from openbb_cli.controllers.utils import handle_obbject_display

    obbject = MagicMock()
    obbject.chart = None
    obbject.results = sample_df_helper
    obbject.extra = {"command": "/foo"}
    mock_session.settings.USE_INTERACTIVE_DF = False
    with (
        patch(
            "openbb_cli.controllers.utils.extract_dataframe",
            return_value=sample_df_helper,
        ),
        patch("openbb_cli.controllers.utils.export_data") as export_data,
    ):
        handle_obbject_display(obbject, export="xlsx", sheet_name=["MySheet"])
    assert export_data.call_args[1]["sheet_name"] == "MySheet"


def test_handle_obbject_display_interactive_uses_charting_table(mock_session):
    """``USE_INTERACTIVE_DF=True`` and no chart → ``obbject.charting.table()``."""
    from openbb_cli.controllers.utils import handle_obbject_display

    obbject = MagicMock()
    obbject.chart = None
    obbject.results = MagicMock()
    obbject.extra = {}
    mock_session.settings.USE_INTERACTIVE_DF = True
    handle_obbject_display(obbject)
    obbject.charting.table.assert_called_once()


def test_handle_obbject_display_falls_back_to_dataframe_without_charting(mock_session):
    """When ``openbb-charting`` isn't installed, ``obbject.charting`` raises
    ``AttributeError`` from pydantic. The interactive path catches that and
    falls back to the plain DataFrame display so spec-mode REPL ``results
    -i N`` still surfaces rows instead of crashing on the missing accessor.

    Uses a real ``OBBject`` (MagicMock would auto-create ``charting`` and
    defeat the test). Isolates ``OBBject.accessors`` — it's a class-level
    set that other tests may have stamped ``"charting"`` into; we strip
    it for the duration of this test and restore on exit so the
    AttributeError actually fires.
    """
    from openbb_core.app.model.obbject import OBBject

    from openbb_cli.controllers.utils import handle_obbject_display

    had_charting = "charting" in OBBject.accessors
    OBBject.accessors.discard("charting")
    # Pydantic caches descriptor lookups on the class — purge any
    # ``charting`` descriptor a prior test might have installed so
    # attribute access really raises AttributeError.
    cached_descriptor = OBBject.__dict__.get("charting")
    if cached_descriptor is not None:
        delattr(OBBject, "charting")
    try:
        obbject = OBBject(results=[{"x": 1}], extra={"command": "/foo"})
        mock_session.settings.USE_INTERACTIVE_DF = True
        with patch(
            "openbb_cli.controllers.utils.extract_dataframe", return_value="DF"
        ) as ed:
            handle_obbject_display(obbject)
        ed.assert_called_once_with(obbject)
        mock_session.output_adapter.display.assert_called_once()
    finally:
        if had_charting:
            OBBject.accessors.add("charting")
        if cached_descriptor is not None:
            setattr(OBBject, "charting", cached_descriptor)


@pytest.fixture
def sample_df_helper():
    """Reusable small DataFrame for utils tests."""
    import pandas as pd

    return pd.DataFrame({"x": [1, 2], "y": [3, 4]})


def test_get_user_data_directory_returns_path_from_preferences(mock_session, tmp_path):
    """``get_user_data_directory`` reads ``session.user.preferences.data_directory``."""
    from openbb_cli.controllers.utils import get_user_data_directory

    mock_session.user.preferences.data_directory = str(tmp_path)
    result = get_user_data_directory()
    assert result == Path(str(tmp_path))


def test_get_data_files_for_completion_lists_supported_extensions(
    mock_session, tmp_path
):
    """Walks the user data dir and returns supported file types as relative paths."""
    from openbb_cli.controllers.utils import get_data_files_for_completion

    mock_session.user.preferences.data_directory = str(tmp_path)
    (tmp_path / "a.csv").write_text("col\n1")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "b.json").write_text("{}")
    (tmp_path / "ignored.txt").write_text("ignored")
    files = get_data_files_for_completion()
    assert "a.csv" in files
    assert any("b.json" in f for f in files)
    assert all(not f.endswith(".txt") for f in files)


def test_get_data_files_for_completion_returns_empty_when_dir_missing(
    mock_session, tmp_path
):
    """Missing user data dir → empty list (no exception)."""
    from openbb_cli.controllers.utils import get_data_files_for_completion

    mock_session.user.preferences.data_directory = str(tmp_path / "does-not-exist")
    assert get_data_files_for_completion() == []


def test_get_data_files_for_completion_swallows_exceptions(mock_session):
    """If walking the path raises, the helper swallows and returns ``[]``."""
    from openbb_cli.controllers.utils import get_data_files_for_completion

    with patch(
        "openbb_cli.controllers.utils.get_user_data_directory",
        side_effect=Exception("boom"),
    ):
        assert get_data_files_for_completion() == []


def test_save_to_excel_appends_when_sheet_exists(mock_session, tmp_path):
    """When the target sheet already exists and the user picks ``a``, data is appended."""
    import pandas as pd

    from openbb_cli.controllers.utils import save_to_excel

    df = pd.DataFrame({"a": [1, 2]})
    target = tmp_path / "out.xlsx"
    save_to_excel(df, target, sheet_name="Sheet1")
    with patch("builtins.input", return_value="a"):
        save_to_excel(pd.DataFrame({"a": [3, 4]}), target, sheet_name="Sheet1")
    final = pd.read_excel(target, sheet_name="Sheet1")
    assert len(final) >= 2


def test_save_to_excel_overwrites_when_sheet_exists(mock_session, tmp_path):
    """``o`` (overwrite) branch replaces the existing sheet."""
    import pandas as pd

    from openbb_cli.controllers.utils import save_to_excel

    df = pd.DataFrame({"a": [1, 2]})
    target = tmp_path / "out.xlsx"
    save_to_excel(df, target, sheet_name="Sheet1")
    with patch("builtins.input", return_value="o"):
        save_to_excel(pd.DataFrame({"a": [10]}), target, sheet_name="Sheet1")
    final = pd.read_excel(target, sheet_name="Sheet1")
    assert final["a"].iloc[0] == 10


def test_remove_timezone_from_dataframe_strips_tz_aware_index(mock_session):
    """tz-aware datetime *index* is converted to date objects (no tzinfo).

    The function gates column conversion on the index being datetime-like, so
    a tz-aware index is the canonical setup for exercising the strip path.
    """
    import pandas as pd

    from openbb_cli.controllers.utils import remove_timezone_from_dataframe

    df = pd.DataFrame(
        {"value": [1, 2]},
        index=pd.to_datetime(["2024-01-01", "2024-01-02"], utc=True),
    )
    cleaned = remove_timezone_from_dataframe(df)
    assert getattr(cleaned.index[0], "tzinfo", None) is None


def test_reset_failure_falls_back_to_print_goodbye(mock_session):
    """If ``main`` raises during reset, ``print_goodbye`` is invoked as a graceful fallback.

    ``reset`` deletes ``openbb_cli.*`` from ``sys.modules`` as part of its
    contract, which would break every subsequent test that holds references
    to the original module classes. Snapshot/restore ``sys.modules`` (and
    re-pin the classes the test file imported at top level) so downstream
    tests see the same identity they started with.
    """
    import sys
    from types import ModuleType
    from unittest.mock import MagicMock, patch

    purged_keys = [k for k in sys.modules if k.startswith("openbb_cli")]
    snapshot = {k: sys.modules[k] for k in purged_keys}

    from openbb_cli.controllers.utils import reset

    stub = ModuleType("openbb_cli.controllers.cli_controller")
    stub.main = MagicMock(side_effect=RuntimeError("boom"))
    try:
        with patch("openbb_cli.controllers.utils.print_goodbye") as goodbye:
            sys.modules["openbb_cli.controllers.cli_controller"] = stub
            reset(queue=["x"])
        goodbye.assert_called_once()
        mock_session.console.print.assert_called()
    finally:
        for k, mod in snapshot.items():
            sys.modules[k] = mod


def test_extract_dataframe_from_obbject_with_list_results(mock_session):
    """OBBject with list results → DataFrame with one row per item."""
    from unittest.mock import MagicMock

    import pandas as pd

    from openbb_cli.controllers.utils import extract_dataframe

    obbj = MagicMock()
    obbj.model_dump.return_value = {"results": [{"a": 1}, {"a": 2}]}
    df = extract_dataframe(obbj)
    assert isinstance(df, pd.DataFrame)
    assert df["a"].tolist() == [1, 2]


def test_extract_dataframe_from_obbject_with_none_results_returns_empty(mock_session):
    from unittest.mock import MagicMock

    import pandas as pd

    from openbb_cli.controllers.utils import extract_dataframe

    obbj = MagicMock()
    obbj.model_dump.return_value = {"results": None}
    df = extract_dataframe(obbj)
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_extract_dataframe_with_dict_results(mock_session):
    from unittest.mock import MagicMock

    from openbb_cli.controllers.utils import extract_dataframe

    obbj = MagicMock()
    obbj.model_dump.return_value = {"results": {"x": 10, "y": 20}}
    df = extract_dataframe(obbj)
    assert df["x"].iloc[0] == 10


def test_extract_dataframe_with_scalar_results(mock_session):
    """Scalar results wrap into ``DataFrame({'value': [scalar]})``."""
    from unittest.mock import MagicMock

    from openbb_cli.controllers.utils import extract_dataframe

    obbj = MagicMock()
    obbj.model_dump.return_value = {"results": 42}
    df = extract_dataframe(obbj)
    assert df["value"].iloc[0] == 42


def test_extract_dataframe_with_existing_dataframe(mock_session):
    """OBBject with an already-built DataFrame is returned as-is."""
    from unittest.mock import MagicMock

    import pandas as pd

    from openbb_cli.controllers.utils import extract_dataframe

    sentinel = pd.DataFrame({"col": [1, 2]})
    obbj = MagicMock()
    obbj.model_dump.return_value = {"results": sentinel}
    df = extract_dataframe(obbj)
    assert df is sentinel


def test_extract_dataframe_passthrough_non_obbject_data(mock_session):
    """Non-OBBject data (no ``model_dump``) is treated as the results directly."""
    import pandas as pd

    from openbb_cli.controllers.utils import extract_dataframe

    df_in = pd.DataFrame({"col": [1]})
    result = extract_dataframe(df_in)
    assert result is df_in


def test_remove_timezone_from_dataframe_passthrough_for_naive(mock_session):
    """tz-naive columns survive the round-trip unchanged."""
    import pandas as pd

    from openbb_cli.controllers.utils import remove_timezone_from_dataframe

    df = pd.DataFrame({"ts": pd.to_datetime(["2024-01-01"])})
    cleaned = remove_timezone_from_dataframe(df)
    assert cleaned.equals(df) or cleaned["ts"].iloc[0] == df["ts"].iloc[0]


def test_export_data_writes_csv(mock_session, tmp_path):
    """``export_type='csv'`` writes a CSV file at the composed path."""
    import pandas as pd

    from openbb_cli.controllers.utils import export_data

    mock_session.user.preferences.export_directory = str(tmp_path)
    mock_session.settings.FILE_OVERWRITE = True
    mock_session.settings.TEST_MODE = False
    df = pd.DataFrame({"a": [1, 2]})
    export_data(
        export_type="csv",
        dir_path=str(tmp_path / "stocks" / "fundamentals"),
        func_name="balance",
        df=df,
    )
    csv_files = list(tmp_path.glob("*.csv"))
    assert csv_files, "expected at least one CSV in the export directory"


def test_export_data_writes_json(mock_session, tmp_path):
    """``export_type='json'`` writes a JSON file."""
    import pandas as pd

    from openbb_cli.controllers.utils import export_data

    mock_session.user.preferences.export_directory = str(tmp_path)
    mock_session.settings.FILE_OVERWRITE = True
    df = pd.DataFrame({"a": [1, 2]})
    export_data(
        export_type="json",
        dir_path=str(tmp_path / "stocks" / "fundamentals"),
        func_name="balance",
        df=df,
    )
    assert list(tmp_path.glob("*.json")), "expected JSON output"


def test_export_data_no_export_type_is_noop(mock_session, tmp_path):
    """Empty ``export_type`` short-circuits."""
    import pandas as pd

    from openbb_cli.controllers.utils import export_data

    mock_session.user.preferences.export_directory = str(tmp_path)
    df = pd.DataFrame({"a": [1]})
    export_data(
        export_type="",
        dir_path=str(tmp_path),
        func_name="cmd",
        df=df,
    )
    assert not list(tmp_path.iterdir())


def test_export_data_strips_rich_color_tags(mock_session, tmp_path):
    """Rich color tags inside DataFrame values are stripped before writing."""
    import pandas as pd

    from openbb_cli.controllers.utils import export_data

    mock_session.user.preferences.export_directory = str(tmp_path)
    mock_session.settings.FILE_OVERWRITE = True
    df = pd.DataFrame({"col": ["[green]ok[/green]", "[red]bad[/red]"]})
    export_data(
        export_type="csv",
        dir_path=str(tmp_path / "x" / "y"),
        func_name="cmd",
        df=df,
    )
    csv = next(tmp_path.glob("*.csv"))
    text = csv.read_text()
    assert "ok" in text and "bad" in text
    assert "[green]" not in text
    assert "[red]" not in text


def test_export_data_explicit_filename_with_extension(mock_session, tmp_path):
    """``export_type='out.csv'`` exports under exactly that filename."""
    import pandas as pd

    from openbb_cli.controllers.utils import export_data

    mock_session.user.preferences.export_directory = str(tmp_path)
    mock_session.settings.FILE_OVERWRITE = True
    df = pd.DataFrame({"a": [1]})
    export_data(
        export_type="out.csv",
        dir_path=str(tmp_path / "x"),
        func_name="cmd",
        df=df,
    )
    assert (tmp_path / "out.csv").exists()


def test_export_data_writes_xlsx(mock_session, tmp_path):
    """``export_type='xlsx'`` writes an Excel workbook (default sheet path)."""
    import pandas as pd

    from openbb_cli.controllers.utils import export_data

    mock_session.user.preferences.export_directory = str(tmp_path)
    mock_session.settings.FILE_OVERWRITE = True
    df = pd.DataFrame({"a": [1, 2]})
    export_data(
        export_type="xlsx",
        dir_path=str(tmp_path / "stocks"),
        func_name="balance",
        df=df,
    )
    assert list(tmp_path.glob("*.xlsx"))


def test_export_data_writes_xlsx_with_sheet_name(mock_session, tmp_path):
    """``sheet_name`` routes through ``save_to_excel`` (sheet-aware writer)."""
    import pandas as pd

    from openbb_cli.controllers.utils import export_data

    mock_session.user.preferences.export_directory = str(tmp_path)
    mock_session.settings.FILE_OVERWRITE = True
    df = pd.DataFrame({"a": [1]})
    with patch("openbb_cli.controllers.utils.save_to_excel") as save_to_excel:
        export_data(
            export_type="xlsx",
            dir_path=str(tmp_path / "x"),
            func_name="cmd",
            df=df,
            sheet_name="Custom",
        )
    save_to_excel.assert_called_once()


def test_export_data_image_without_figure_warns(mock_session, tmp_path):
    """``export_type='out.png'`` without a figure prints 'No plot to export.'"""
    import pandas as pd

    from openbb_cli.controllers.utils import export_data

    mock_session.user.preferences.export_directory = str(tmp_path)
    mock_session.settings.FILE_OVERWRITE = True
    df = pd.DataFrame({"a": [1]})
    export_data(
        export_type="out.png",
        dir_path=str(tmp_path / "x"),
        func_name="cmd",
        df=df,
        figure=None,
    )
    calls = [str(c) for c in mock_session.console.print.call_args_list]
    assert any("No plot to export" in c for c in calls)


def test_export_data_image_with_figure_calls_show(mock_session, tmp_path):
    """``export_type='out.jpg'`` with a figure calls ``figure.show(export_image=path)``."""
    import pandas as pd

    from openbb_cli.controllers.utils import export_data

    mock_session.user.preferences.export_directory = str(tmp_path)
    mock_session.settings.FILE_OVERWRITE = True
    df = pd.DataFrame({"a": [1]})
    fig = MagicMock()
    export_data(
        export_type="out.jpg",
        dir_path=str(tmp_path / "x"),
        func_name="cmd",
        df=df,
        figure=fig,
    )
    fig.show.assert_called_once()


def test_export_data_sqlite_creates_new_table(mock_session, tmp_path):
    """SQLite export to a fresh DB writes the data table without prompting."""
    import pandas as pd

    from openbb_cli.controllers.utils import export_data

    mock_session.user.preferences.export_directory = str(tmp_path)
    mock_session.settings.FILE_OVERWRITE = True
    df = pd.DataFrame({"a": [1, 2]})
    export_data(
        export_type="out.db",
        dir_path=str(tmp_path / "x"),
        func_name="cmd",
        df=df,
    )
    db_files = list(tmp_path.glob("*.db"))
    assert db_files


def test_export_data_unknown_extension_warns(mock_session, tmp_path):
    """Unknown extension (``.parquet``) hits the catch-all 'Wrong export file specified.'"""
    import pandas as pd

    from openbb_cli.controllers.utils import export_data

    mock_session.user.preferences.export_directory = str(tmp_path)
    mock_session.settings.FILE_OVERWRITE = True
    df = pd.DataFrame({"a": [1]})
    export_data(
        export_type="out.parquet",
        dir_path=str(tmp_path / "x"),
        func_name="cmd",
        df=df,
    )
    calls = [str(c) for c in mock_session.console.print.call_args_list]
    assert any("Wrong export file" in c for c in calls)


def test_print_rich_table_returns_when_export_true(mock_session):
    """``export=True`` short-circuits without printing."""
    import pandas as pd

    from openbb_cli.controllers.utils import print_rich_table

    df = pd.DataFrame({"a": [1, 2]})
    print_rich_table(df, export=True)
    mock_session.console.print.assert_not_called()


def test_print_rich_table_basic_dataframe_renders(mock_session):
    """Basic non-interactive path prints the table via session.console."""
    import pandas as pd

    from openbb_cli.controllers.utils import print_rich_table

    mock_session.settings.USE_INTERACTIVE_DF = False
    mock_session.backend = None
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    print_rich_table(df, title="Test Table")
    mock_session.console.print.assert_called()


def test_print_rich_table_validates_header_length(mock_session):
    """Header list whose length mismatches DataFrame columns raises ValueError."""
    import pandas as pd

    from openbb_cli.controllers.utils import print_rich_table

    mock_session.settings.USE_INTERACTIVE_DF = True
    mock_session.backend = MagicMock()
    df = pd.DataFrame({"a": [1], "b": [2]})
    with pytest.raises(ValueError, match="Length of headers"):
        print_rich_table(df, headers=["only_one"])


def test_print_rich_table_interactive_send_table(mock_session):
    """Interactive mode + backend → ``backend.send_table`` is invoked."""
    import pandas as pd

    from openbb_cli.controllers.utils import print_rich_table

    mock_session.settings.USE_INTERACTIVE_DF = True
    mock_session.backend = MagicMock()
    mock_session.user.preferences.table_style = "dark"
    df = pd.DataFrame({"a": [1, 2]})
    print_rich_table(df, title="t", show_index=True, index_name="Idx")
    mock_session.backend.send_table.assert_called_once()


def test_print_rich_table_interactive_failure_falls_through(mock_session):
    """If ``backend.send_table`` raises, the rich-table path runs as fallback."""
    import pandas as pd

    from openbb_cli.controllers.utils import print_rich_table

    mock_session.settings.USE_INTERACTIVE_DF = True
    mock_session.backend = MagicMock()
    mock_session.backend.send_table.side_effect = Exception("backend down")
    mock_session.user.preferences.table_style = "dark"
    df = pd.DataFrame({"a": [1, 2]})
    print_rich_table(df)
    mock_session.console.print.assert_called()


def test_print_rich_table_floatfmt_list_length_mismatch(mock_session):
    """``floatfmt`` list of wrong length raises ValueError."""
    import pandas as pd

    from openbb_cli.controllers.utils import print_rich_table

    mock_session.settings.USE_INTERACTIVE_DF = False
    mock_session.backend = None
    df = pd.DataFrame({"a": [1.0], "b": [2.0]})
    with pytest.raises(ValueError, match="floatfmt"):
        print_rich_table(df, floatfmt=["only_one"])


def test_print_rich_table_use_tabulate_false_uses_to_string(mock_session):
    """``use_tabulate_df=False`` prints via ``df.to_string``."""
    import pandas as pd

    from openbb_cli.controllers.utils import print_rich_table

    mock_session.settings.USE_INTERACTIVE_DF = False
    mock_session.backend = None
    df = pd.DataFrame({"a": [1, 2]})
    print_rich_table(df, use_tabulate_df=False)
    mock_session.console.print.assert_called()


def test_print_rich_table_automatic_coloring_with_columns(mock_session):
    """``automatic_coloring`` + ``columns_to_auto_color`` colors only those columns."""
    import pandas as pd

    from openbb_cli.controllers.utils import print_rich_table

    mock_session.settings.USE_INTERACTIVE_DF = False
    mock_session.backend = None
    df = pd.DataFrame({"a": [1.0, -2.0], "b": [3.0, 4.0]})
    print_rich_table(df, automatic_coloring=True, columns_to_auto_color=["a"])
    mock_session.console.print.assert_called()


def test_print_rich_table_automatic_coloring_blanket_apply(mock_session):
    """``automatic_coloring`` without column/row filters maps the entire DataFrame."""
    import pandas as pd

    from openbb_cli.controllers.utils import print_rich_table

    mock_session.settings.USE_INTERACTIVE_DF = False
    mock_session.backend = None
    df = pd.DataFrame({"a": [1.0, -2.0], "b": [3.0, 4.0]})
    print_rich_table(df, automatic_coloring=True)
    mock_session.console.print.assert_called()


def test_parse_and_split_input_with_trailing_slash():
    """An input ending with ``/`` triggers the empty-trailing-segment branch."""
    out = parse_and_split_input("foo/", custom_filters=[])
    assert out == ["foo"]


def test_print_rich_table_columns_keep_types(mock_session):
    """``columns_keep_types`` skips coercion for listed columns."""
    import pandas as pd

    from openbb_cli.controllers.utils import print_rich_table

    mock_session.settings.USE_INTERACTIVE_DF = False
    mock_session.backend = None
    df = pd.DataFrame({"keep": ["mixed", "data"], "convert": ["1", "2"]})
    print_rich_table(df, columns_keep_types=["keep"])
    mock_session.console.print.assert_called()


def test_print_rich_table_headers_as_pandas_index(mock_session):
    """``headers`` passed as ``pd.Index`` exercises ``_get_headers`` index branch."""
    import pandas as pd

    from openbb_cli.controllers.utils import print_rich_table

    mock_session.settings.USE_INTERACTIVE_DF = True
    mock_session.backend = MagicMock()
    df = pd.DataFrame({"a": [1], "b": [2]})
    print_rich_table(df, headers=pd.Index(["one", "two"]))
    mock_session.backend.send_table.assert_called_once()


def test_print_rich_table_interactive_with_show_index_and_named_index(mock_session):
    """Interactive path with ``show_index=True`` and named index."""
    import pandas as pd

    from openbb_cli.controllers.utils import print_rich_table

    mock_session.settings.USE_INTERACTIVE_DF = True
    mock_session.backend = MagicMock()
    df = pd.DataFrame({"a": [1, 2]}, index=pd.Index(["r1", "r2"]))
    print_rich_table(df, show_index=True, index_name="Idx")
    mock_session.backend.send_table.assert_called_once()


def test_print_rich_table_interactive_renames_blank_columns(mock_session):
    """Interactive path renames empty-string column names to ``"  "``."""
    import pandas as pd

    from openbb_cli.controllers.utils import print_rich_table

    mock_session.settings.USE_INTERACTIVE_DF = True
    mock_session.backend = MagicMock()
    df = pd.DataFrame({"a": [1], "": [2]})
    print_rich_table(df)
    sent = mock_session.backend.send_table.call_args[1]["df_table"]
    assert "  " in sent.columns


def test_print_rich_table_rows_to_auto_color(mock_session):
    """``rows_to_auto_color`` colors specified rows."""
    import pandas as pd

    from openbb_cli.controllers.utils import print_rich_table

    mock_session.settings.USE_INTERACTIVE_DF = False
    mock_session.backend = None
    df = pd.DataFrame(
        {"a": ["1.0", "-2.0"], "b": ["3.0", "4.0"]},
        index=["r1", "r2"],
        dtype=object,
    )
    print_rich_table(
        df,
        automatic_coloring=True,
        rows_to_auto_color=["r1"],
        columns_keep_types=["a", "b"],
    )
    mock_session.console.print.assert_called()


def test_print_rich_table_tabulate_with_show_index_and_headers(mock_session):
    """Tabulate path with ``show_index`` and custom ``headers``."""
    import pandas as pd

    from openbb_cli.controllers.utils import print_rich_table

    mock_session.settings.USE_INTERACTIVE_DF = False
    mock_session.backend = None
    df = pd.DataFrame({"a": [1], "b": [2]}, index=["r1"])
    print_rich_table(df, show_index=True, index_name="Idx", headers=["A", "B"])
    mock_session.console.print.assert_called()


def test_remove_timezone_from_dataframe_strips_tz_columns(mock_session):
    """A tz-aware datetime column is stripped to date-only."""
    import pandas as pd

    from openbb_cli.controllers.utils import remove_timezone_from_dataframe

    df = pd.DataFrame(
        {
            "dt": pd.to_datetime(["2024-01-01", "2024-01-02"]).tz_localize("UTC"),
        }
    )
    df.index = pd.to_datetime(["2024-01-01", "2024-01-02"]).tz_localize("UTC")
    out = remove_timezone_from_dataframe(df)
    assert out["dt"].iloc[0] == pd.Timestamp("2024-01-01").date()


def test_export_data_collapses_openbb_cli_filename_marker(
    mock_session, tmp_path, sample_df_helper
):
    """A filename containing ``.OpenBB_openbb_cli`` is rewritten to ``OpenBBCLI``."""
    from openbb_cli.controllers.utils import export_data

    mock_session.user.preferences.export_directory = str(tmp_path)
    mock_session.user.preferences.overwrite_export = True
    fake_dir = tmp_path / ".OpenBB" / "openbb_cli"
    fake_dir.mkdir(parents=True)
    export_data(
        export_type="csv",
        dir_path=str(fake_dir),
        func_name="myfunc",
        df=sample_df_helper,
    )
    files = list(tmp_path.glob("*.csv"))
    assert any("OpenBBCLI" in f.name for f in files)


def test_export_data_existing_file_collision_increments(
    mock_session, tmp_path, sample_df_helper
):
    """Existing file + user declines overwrite → bumps the filename suffix."""
    from openbb_cli.controllers.utils import export_data

    mock_session.user.preferences.export_directory = str(tmp_path)
    (tmp_path / "preexisting.csv").write_text("col\n1")
    with patch(
        "openbb_cli.controllers.utils.ask_file_overwrite",
        return_value=(True, False),
    ):
        export_data(
            export_type="csv",
            dir_path=str(tmp_path),
            func_name="myfunc",
            df=sample_df_helper,
        )
    csvs = list(tmp_path.glob("*.csv"))
    assert len(csvs) >= 2


def _seed_sqlite_table(target, df, name="data"):
    """Pre-populate a SQLite db with ``df`` rows under ``name`` using sqlite3 directly.

    Avoids pandas' SQLAlchemy URI requirement.
    """
    import sqlite3

    conn = sqlite3.connect(target)
    try:
        df.to_sql(name, conn, if_exists="replace", index=False)
    finally:
        conn.close()


def test_export_data_sqlite_existing_table_overwrite(
    mock_session, tmp_path, sample_df_helper
):
    """SQLite export with existing table + 'o' choice → ``if_exists='replace'``."""
    from openbb_cli.controllers.utils import export_data

    mock_session.user.preferences.export_directory = str(tmp_path)
    mock_session.user.preferences.overwrite_export = True
    target = tmp_path / "out.db"
    _seed_sqlite_table(target, sample_df_helper)
    with patch("builtins.input", return_value="o"):
        export_data(
            export_type="out.db",
            dir_path=str(tmp_path),
            func_name="myfunc",
            df=sample_df_helper,
        )
    import sqlite3

    conn = sqlite3.connect(target)
    rows = conn.execute("SELECT * FROM data").fetchall()
    conn.close()
    assert len(rows) == len(sample_df_helper)


def test_export_data_sqlite_existing_table_append(
    mock_session, tmp_path, sample_df_helper
):
    """SQLite with 'a' choice appends to existing table."""
    from openbb_cli.controllers.utils import export_data

    mock_session.user.preferences.export_directory = str(tmp_path)
    mock_session.user.preferences.overwrite_export = True
    target = tmp_path / "out.db"
    _seed_sqlite_table(target, sample_df_helper)
    with patch("builtins.input", return_value="a"):
        export_data(
            export_type="out.db",
            dir_path=str(tmp_path),
            func_name="myfunc",
            df=sample_df_helper,
        )
    import sqlite3

    conn = sqlite3.connect(target)
    count = conn.execute("SELECT COUNT(*) FROM data").fetchone()[0]
    conn.close()
    assert count == 2 * len(sample_df_helper)


def test_export_data_sqlite_existing_table_new_name(
    mock_session, tmp_path, sample_df_helper
):
    """SQLite with 'n' creates a new uniquely-named table."""
    from openbb_cli.controllers.utils import export_data

    mock_session.user.preferences.export_directory = str(tmp_path)
    mock_session.user.preferences.overwrite_export = True
    target = tmp_path / "out.db"
    _seed_sqlite_table(target, sample_df_helper)
    with patch("builtins.input", return_value="n"):
        export_data(
            export_type="out.db",
            dir_path=str(tmp_path),
            func_name="myfunc",
            df=sample_df_helper,
        )
    import sqlite3

    conn = sqlite3.connect(target)
    names = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    conn.close()
    assert "data_1" in names


def test_export_data_sqlite_invalid_choice_skips(
    mock_session, tmp_path, sample_df_helper
):
    """SQLite with any other input skips the export."""
    from openbb_cli.controllers.utils import export_data

    mock_session.user.preferences.export_directory = str(tmp_path)
    mock_session.user.preferences.overwrite_export = True
    target = tmp_path / "out.db"
    _seed_sqlite_table(target, sample_df_helper)
    with patch("builtins.input", return_value="garbage"):
        export_data(
            export_type="out.db",
            dir_path=str(tmp_path),
            func_name="myfunc",
            df=sample_df_helper,
        )
    msgs = [str(c) for c in mock_session.console.print.call_args_list]
    assert any("Invalid choice" in m for m in msgs)


def test_handle_obbject_display_chart_with_export_extracts_dataframe(mock_session):
    """``chart=True`` AND ``export=...`` triggers chart-fig + DataFrame extract."""
    from openbb_cli.controllers.utils import handle_obbject_display

    obbject = MagicMock()
    obbject.chart = MagicMock()
    obbject.results = MagicMock()
    obbject.extra = {"command": "/x"}
    mock_session.settings.USE_INTERACTIVE_DF = False
    with (
        patch(
            "openbb_cli.controllers.utils.extract_dataframe",
        ) as extract,
        patch("openbb_cli.controllers.utils.export_data") as export_data,
    ):
        import pandas as pd

        extract.return_value = pd.DataFrame({"x": [1]})
        handle_obbject_display(obbject, chart=True, export="png")
    obbject.show.assert_called_once()
    extract.assert_called()
    export_data.assert_called_once()


@pytest.fixture
def sqlite_db(tmp_path):
    """Pre-populated SQLite database with a small table."""
    import sqlite3

    import pandas as pd

    db = tmp_path / "store.db"
    conn = sqlite3.connect(db)
    pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]}).to_sql(
        "rows", conn, if_exists="replace", index=False
    )
    conn.close()
    return db


def test_sqlite_table_init_stores_args(sqlite_db):
    """``SQLiteTable.__init__`` stores the path/name/count and clears cache."""
    from openbb_cli.controllers.utils import SQLiteTable

    tbl = SQLiteTable(db_path=str(sqlite_db), table_name="rows", row_count=3)
    assert tbl.db_path == str(sqlite_db)
    assert tbl.table_name == "rows"
    assert tbl.row_count == 3
    assert tbl._cached_df is None


def test_sqlite_table_quoted_name_escapes_quotes(sqlite_db):
    """``_quoted_name`` doubles internal quotes and wraps in double-quotes."""
    from openbb_cli.controllers.utils import SQLiteTable

    tbl = SQLiteTable(db_path=str(sqlite_db), table_name='weird"name', row_count=0)
    assert tbl._quoted_name == '"weird""name"'


def test_sqlite_table_to_dataframe_caches(sqlite_db):
    """``to_dataframe`` loads from disk on first call and caches afterward."""
    from openbb_cli.controllers.utils import SQLiteTable

    tbl = SQLiteTable(db_path=str(sqlite_db), table_name="rows", row_count=3)
    first = tbl.to_dataframe()
    assert len(first) == 3
    assert tbl._cached_df is not None
    second = tbl.to_dataframe()
    assert second is tbl._cached_df


def test_sqlite_table_to_dataframe_no_cache(sqlite_db):
    """``use_cache=False`` skips caching entirely."""
    from openbb_cli.controllers.utils import SQLiteTable

    tbl = SQLiteTable(db_path=str(sqlite_db), table_name="rows", row_count=3)
    out = tbl.to_dataframe(use_cache=False)
    assert len(out) == 3
    assert tbl._cached_df is None


def test_sqlite_table_get_schema_returns_pragma_rows(sqlite_db):
    """``get_schema`` returns the PRAGMA table_info rows."""
    from openbb_cli.controllers.utils import SQLiteTable

    tbl = SQLiteTable(db_path=str(sqlite_db), table_name="rows", row_count=3)
    schema = tbl.get_schema()
    column_names = {row[1] for row in schema}
    assert column_names == {"a", "b"}


def test_sqlite_table_query_with_where_and_limit(sqlite_db):
    """``query`` builds SQL with optional WHERE + LIMIT clauses."""
    from openbb_cli.controllers.utils import SQLiteTable

    tbl = SQLiteTable(db_path=str(sqlite_db), table_name="rows", row_count=3)
    out = tbl.query(where="a > 1", limit=1)
    assert len(out) == 1
    assert int(out["a"].iloc[0]) > 1


def test_sqlite_table_query_no_filters(sqlite_db):
    """``query`` with no filters returns all rows."""
    from openbb_cli.controllers.utils import SQLiteTable

    tbl = SQLiteTable(db_path=str(sqlite_db), table_name="rows", row_count=3)
    assert len(tbl.query()) == 3


def test_extract_dataframe_with_sqlite_table_lazy_loads(sqlite_db):
    """``extract_dataframe`` materializes a ``SQLiteTable`` via ``to_dataframe``."""
    from openbb_cli.controllers.utils import SQLiteTable, extract_dataframe

    tbl = SQLiteTable(db_path=str(sqlite_db), table_name="rows", row_count=3)
    obbject = MagicMock()
    obbject.model_dump.return_value = {"results": tbl}
    out = extract_dataframe(obbject)
    assert len(out) == 3
    assert set(out.columns) == {"a", "b"}


def test_parse_and_split_input_with_custom_filter():
    """A non-None entry in ``custom_filters`` is appended to the regex."""
    out = parse_and_split_input(
        "load AAPL/help", custom_filters=[r"\bload\s+\w+", None]
    )
    assert any("load" in seg for seg in out)


def test_export_data_sqlite_new_name_collision_loops(
    mock_session, tmp_path, sample_df_helper
):
    """When 'n' is chosen and ``data_1`` already exists, the loop bumps to ``data_2``."""
    from openbb_cli.controllers.utils import export_data

    mock_session.user.preferences.export_directory = str(tmp_path)
    mock_session.user.preferences.overwrite_export = True
    target = tmp_path / "out.db"
    import sqlite3

    conn = sqlite3.connect(target)
    sample_df_helper.to_sql("data", conn, if_exists="replace", index=False)
    sample_df_helper.to_sql("data_1", conn, if_exists="replace", index=False)
    conn.close()
    with patch("builtins.input", return_value="n"):
        export_data(
            export_type="out.db",
            dir_path=str(tmp_path),
            func_name="myfunc",
            df=sample_df_helper,
        )
    conn = sqlite3.connect(target)
    names = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    conn.close()
    assert "data_2" in names
