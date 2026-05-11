"""Test the Session class."""

from unittest.mock import MagicMock, patch

import pytest

from openbb_cli.models.settings import Settings
from openbb_cli.session import _UNSET, Session


def _fresh_session() -> Session:
    """Return a Session that's not the cached singleton from a prior test.

    Settings load from the user's ``~/.openbb_platform/.cli.env`` env file,
    which can leave ``OPENBB_OUTPUT_MODE`` set from prior interactive runs.
    Explicitly reset to the documented baseline so tests are deterministic.
    """
    Session._instances.pop(Session, None)
    s = Session()
    s.settings.OUTPUT_MODE = "tsv"
    s.settings.USE_INTERACTIVE_DF = False
    s._output_adapter = _UNSET
    return s


@pytest.fixture
def session():
    """Provide a fresh Session per-test."""
    return _fresh_session()


def test_session_initialization(session):
    """Heavy attrs are not materialized on construction."""
    assert session.settings is not None
    assert session.style is not None
    assert session.console is not None
    assert session.obbject_registry is not None
    assert isinstance(session.settings, Settings)
    assert session._prompt_session is _UNSET
    assert session._backend is _UNSET
    assert session._output_adapter is _UNSET


@patch("openbb_cli.session.sys.stdin.isatty", return_value=True)
def test_prompt_session_when_tty(mock_isatty, session):
    """Returns a PromptSession instance when stdin is a TTY."""
    with patch("prompt_toolkit.PromptSession") as mock_ps:
        mock_ps.return_value = MagicMock(name="PromptSession")
        prompt = session.prompt_session
    assert prompt is not None


@patch("openbb_cli.session.sys.stdin.isatty", return_value=False)
def test_prompt_session_when_not_tty(mock_isatty, session):
    """Returns None when stdin is not a TTY (CI / agent / pipe)."""
    assert session.prompt_session is None


@patch(
    "openbb_cli.session.sys.stdin.isatty",
    side_effect=ValueError("detached"),
)
def test_prompt_session_swallows_isatty_failure(mock_isatty, session):
    """Detached stdin (ValueError on isatty) is treated as non-interactive."""
    assert session.is_interactive is False
    assert session.prompt_session is None


def test_prompt_session_cached(session):
    """Subsequent accesses return the cached value."""
    with patch.object(session, "_build_prompt_session", return_value="X") as build:
        first = session.prompt_session
        second = session.prompt_session
    assert first == second == "X"
    build.assert_called_once()


@pytest.mark.parametrize(
    "mode, expected_module",
    [
        ("tsv", "openbb_cli.outputs.tsv"),
        ("rich", "openbb_cli.outputs.rich"),
        ("json", "openbb_cli.outputs.json"),
        ("html", "openbb_cli.outputs.html"),
    ],
)
def test_output_adapter_modes(mode, expected_module):
    """OUTPUT_MODE setting selects the matching adapter."""
    s = _fresh_session()
    s.settings.OUTPUT_MODE = mode
    s._output_adapter = _UNSET
    adapter = s.output_adapter
    assert adapter.__class__.__module__ == expected_module


def test_output_adapter_default_is_tsv(session):
    """Default OUTPUT_MODE is 'tsv' — adapter is TsvOutput."""
    from openbb_cli.outputs.tsv import TsvOutput

    assert isinstance(session.output_adapter, TsvOutput)


def test_output_adapter_cached_when_mode_unchanged(session):
    """Subsequent accesses return the same instance when ``OUTPUT_MODE`` is stable."""
    a1 = session.output_adapter
    a2 = session.output_adapter
    assert a1 is a2


def test_output_adapter_rebuilds_on_mode_change(session):
    """Changing ``OUTPUT_MODE`` via ``/settings/`` swaps the adapter — must
    not stay frozen at first-access mode."""
    from openbb_cli.outputs.json import JsonOutput
    from openbb_cli.outputs.tsv import TsvOutput

    session.settings.OUTPUT_MODE = "tsv"
    assert isinstance(session.output_adapter, TsvOutput)
    session.settings.OUTPUT_MODE = "json"
    assert isinstance(session.output_adapter, JsonOutput)


def test_backend_cached(session):
    """Backend property caches the first-built value."""
    sentinel = object()
    with patch.object(session, "_build_backend", return_value=sentinel) as build:
        first = session.backend
        second = session.backend
    assert first is second is sentinel
    build.assert_called_once()


def test_build_backend_swallows_import_failure(session):
    """``_build_backend`` returns None when openbb_charting import fails.

    Patches ``sys.modules`` to inject a None entry that triggers ImportError on
    the dynamic import, exercising the except-Exception branch of the real
    builder rather than the mocked-out version.
    """
    import sys

    with patch.dict(sys.modules, {"openbb_charting.core.backend": None}):
        assert session._build_backend() is None


def test_build_backend_returns_real_backend_on_success(session):
    """Happy path: openbb_charting and ChartingSettings both import → Backend instance."""
    sentinel = MagicMock(name="Backend instance")
    fake_backend_module = MagicMock()
    fake_backend_module.Backend.return_value = sentinel
    fake_settings_module = MagicMock()
    fake_settings_module.ChartingSettings.return_value = MagicMock(name="settings")

    import sys

    with patch.dict(
        sys.modules,
        {
            "openbb_charting.core.backend": fake_backend_module,
            "openbb_core.app.model.charts.charting_settings": fake_settings_module,
        },
    ):
        assert session._build_backend() is sentinel


def test_build_prompt_session_swallows_failure(session):
    """Constructing PromptSession may fail (e.g. terminal init); session degrades to None."""
    import sys

    with (
        patch("openbb_cli.session.sys.stdin.isatty", return_value=True),
        patch.dict(sys.modules, {"prompt_toolkit": None}),
    ):
        assert session._build_prompt_session() is None


def test_max_obbjects_not_exceeded(session):
    """Returns False under the registry size limit."""
    session.settings.N_TO_KEEP_OBBJECT_REGISTRY = 10
    assert session.max_obbjects_exceeded() is False


def test_max_obbjects_exceeded_at_limit():
    """At the limit (0), the empty registry counts as exceeded."""
    s = _fresh_session()
    s.settings.N_TO_KEEP_OBBJECT_REGISTRY = 0
    assert s.max_obbjects_exceeded() is True


def test_obb_swallows_user_styles_directory_failure():
    """If reading ``obb.user.preferences.user_styles_directory`` raises, the
    session still returns the fake obb (the styling apply is best-effort)."""
    import sys
    import types

    fake = types.SimpleNamespace()
    fake.user = MagicMock()
    type(fake.user).preferences = property(
        lambda self: (_ for _ in ()).throw(RuntimeError("preferences blew up"))
    )
    fake_mod = types.ModuleType("openbb")
    fake_mod.obb = fake
    s = _fresh_session()
    with patch.dict(sys.modules, {"openbb": fake_mod}):
        assert s._obb is fake
    with patch.dict(sys.modules, {"openbb": None}):
        assert s._obb is fake
