"""Tests for ``openbb_platform_api.service.widgets_service``.

Covers the editable-on-disk flow (build → diff → prompt → write) and
the ephemeral in-memory build path. Each test isolates the module's
mutable state (``FIRST_RUN`` / ``PATH_WIDGETS``) so test order doesn't
matter.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from openbb_platform_api.service import widgets_service


@pytest.fixture
def reset_widgets_service_state():
    """Snapshot + restore module-level state around each test."""
    original_first_run = widgets_service.FIRST_RUN
    original_path_widgets = widgets_service.PATH_WIDGETS.copy()
    yield
    widgets_service.FIRST_RUN = original_first_run
    widgets_service.PATH_WIDGETS = original_path_widgets


def test_get_widgets_json_ephemeral_build_non_router_path_widgets(
    reset_widgets_service_state, monkeypatch
):
    """Non-editable mode → ``build_json`` is the source of truth, no
    disk I/O. Router-attached widgets whose key *doesn't* end in ``/``
    are merged in (the trailing-``/`` keys auto-add a ``*`` exclude
    that then prevents their own merge — that's an intentional
    deduplication for trailing-slash router prefixes).
    """
    widgets_service.FIRST_RUN = False
    widgets_service.PATH_WIDGETS = {
        # Key without trailing ``/`` — survives the dedup logic and
        # merges into the final dict.
        "router_namespace": {"router_widget": {"name": "Router"}},
    }
    monkeypatch.setattr(
        "openbb_platform_api.utils.widgets.build_json",
        MagicMock(return_value={"auto_widget": {"name": "Auto"}}),
    )

    result = widgets_service.get_widgets_json(
        _build=False, _openapi={}, widget_exclude_filter=[]
    )
    # Both auto and router-attached widgets in the merged set.
    assert result["auto_widget"] == {"name": "Auto"}
    assert result["router_widget"] == {"name": "Router"}


def test_get_widgets_json_excludes_widget_id_from_path_widgets(
    reset_widgets_service_state, monkeypatch
):
    """A widget id explicitly in the exclude filter is dropped from
    the router-attached merge step — the inner ``if widget_id not in
    widget_exclude_filter`` guard.
    """
    widgets_service.FIRST_RUN = False
    widgets_service.PATH_WIDGETS = {
        "router": {
            "kept": {"name": "Kept"},
            "dropped_id": {"name": "Dropped"},
        },
    }
    monkeypatch.setattr(
        "openbb_platform_api.utils.widgets.build_json",
        MagicMock(return_value={}),
    )

    result = widgets_service.get_widgets_json(
        _build=False,
        _openapi={},
        widget_exclude_filter=["dropped_id"],
    )
    assert result == {"kept": {"name": "Kept"}}


def test_get_widgets_json_trailing_slash_path_widgets_self_dedup(
    reset_widgets_service_state, monkeypatch
):
    """Path-widget keys ending in ``/`` get auto-added to the exclude
    filter as ``*``-globs so the auto-builder skips them. The merge
    step then also skips them — net effect: trailing-slash router
    prefixes are EXPECTED to be defined entirely by the router (not
    auto-merged here). Lock this contract so a future refactor can't
    silently flip it.
    """
    widgets_service.FIRST_RUN = False
    widgets_service.PATH_WIDGETS = {
        "/router_prefix/": {"router_widget": {"name": "Router"}},
    }
    monkeypatch.setattr(
        "openbb_platform_api.utils.widgets.build_json",
        MagicMock(return_value={"auto": {"name": "Auto"}}),
    )

    result = widgets_service.get_widgets_json(
        _build=False, _openapi={}, widget_exclude_filter=[]
    )
    # Auto present; router-attached path with trailing-/ is self-excluded.
    assert "auto" in result
    assert "router_widget" not in result


def test_get_widgets_json_editable_writes_when_diff_and_overwrite(
    tmp_path, reset_widgets_service_state, monkeypatch
):
    """Editable + diff present + user answers ``y`` → file is rewritten
    with the fresh build.
    """
    widgets_service.FIRST_RUN = False
    widgets_path = tmp_path / "widgets.json"
    widgets_path.write_text(json.dumps({"old": {"name": "Stale"}}))

    fresh = {"new": {"name": "Fresh"}}
    monkeypatch.setattr(
        "openbb_platform_api.utils.widgets.build_json",
        MagicMock(return_value=fresh),
    )

    with patch("builtins.input", return_value="y"):
        result = widgets_service.get_widgets_json(
            _build=True,
            _openapi={},
            widget_exclude_filter=[],
            editable=True,
            widgets_path=str(widgets_path),
        )

    assert result == fresh
    # File on disk now reflects the fresh build.
    assert json.loads(widgets_path.read_text()) == fresh


def test_get_widgets_json_editable_appends_when_user_answers_n(
    tmp_path, reset_widgets_service_state, monkeypatch
):
    """User answers ``n`` → fresh build is appended to existing rather
    than overwriting (existing entries win).
    """
    widgets_service.FIRST_RUN = False
    widgets_path = tmp_path / "widgets.json"
    existing = {"old": {"name": "Stale"}}
    widgets_path.write_text(json.dumps(existing))

    fresh = {"new": {"name": "Fresh"}, "old": {"name": "Overwritten"}}
    monkeypatch.setattr(
        "openbb_platform_api.utils.widgets.build_json",
        MagicMock(return_value=fresh),
    )

    with patch("builtins.input", return_value="n"):
        result = widgets_service.get_widgets_json(
            _build=True,
            _openapi={},
            widget_exclude_filter=[],
            editable=True,
            widgets_path=str(widgets_path),
        )

    # Existing took precedence on the conflicting ``old`` key.
    assert result["old"]["name"] == "Stale"
    # New entries from the build still merged in.
    assert result["new"]["name"] == "Fresh"


def test_get_widgets_json_editable_ignores_when_user_answers_i(
    tmp_path, reset_widgets_service_state, monkeypatch
):
    """User answers ``i`` → file untouched; existing widgets returned."""
    widgets_service.FIRST_RUN = False
    widgets_path = tmp_path / "widgets.json"
    existing = {"keep_me": {"name": "Stable"}}
    widgets_path.write_text(json.dumps(existing))

    monkeypatch.setattr(
        "openbb_platform_api.utils.widgets.build_json",
        MagicMock(return_value={"new": {"name": "Fresh"}}),
    )

    with patch("builtins.input", return_value="i"):
        result = widgets_service.get_widgets_json(
            _build=True,
            _openapi={},
            widget_exclude_filter=[],
            editable=True,
            widgets_path=str(widgets_path),
        )
    # File on disk unchanged.
    assert json.loads(widgets_path.read_text()) == existing
    assert result == existing


def test_get_widgets_json_editable_creates_missing_file(
    tmp_path, reset_widgets_service_state, monkeypatch
):
    """When the widgets file doesn't exist, the editable path forces
    a build, creates the parent directory, and writes the result.
    """
    widgets_service.FIRST_RUN = False
    widgets_path = tmp_path / "deep" / "nested" / "widgets.json"
    fresh = {"x": {"name": "Fresh"}}
    monkeypatch.setattr(
        "openbb_platform_api.utils.widgets.build_json",
        MagicMock(return_value=fresh),
    )

    # No diff because the file didn't exist → no prompt.
    result = widgets_service.get_widgets_json(
        _build=False,  # forced to True internally because file didn't exist
        _openapi={},
        widget_exclude_filter=[],
        editable=True,
        widgets_path=str(widgets_path),
    )
    assert result == fresh
    assert widgets_path.exists()
    assert json.loads(widgets_path.read_text()) == fresh


def test_get_widgets_json_first_run_populates_path_widgets_from_app(
    reset_widgets_service_state, monkeypatch
):
    """First-run + a FastAPI app with extra widget routes →
    ``PATH_WIDGETS`` gets populated via ``run_async``. Exercises the
    ``FIRST_RUN`` mutation branch.
    """
    from fastapi import FastAPI

    widgets_service.FIRST_RUN = True
    widgets_service.PATH_WIDGETS = {}

    fake_app = FastAPI()

    monkeypatch.setattr(
        "openbb_platform_api.utils.widgets.build_json",
        MagicMock(return_value={}),
    )
    monkeypatch.setattr(
        "openbb_platform_api.utils.merge_widgets.has_additional_widgets",
        lambda app: True,
    )

    captured: dict = {}

    def fake_run_async(callable_or_coroutine, *args, **kwargs):
        captured["called"] = True
        return {"/extra/": {"router_widget": {"name": "Router"}}}

    monkeypatch.setattr("openbb_core.provider.utils.helpers.run_async", fake_run_async)

    widgets_service.get_widgets_json(
        _build=False,
        _openapi={},
        widget_exclude_filter=[],
        editable=False,
        widgets_path=None,
        app=fake_app,
    )

    assert captured.get("called") is True
    assert "/extra/" in widgets_service.PATH_WIDGETS


def test_get_widgets_json_editable_default_path_when_widgets_path_omitted(
    reset_widgets_service_state, monkeypatch, tmp_path
):
    """Editable + no ``widgets_path`` → derive path from
    ``sys.executable``'s parent. Exercises the env-default branch.
    """
    widgets_service.FIRST_RUN = False

    fresh = {"new": {"name": "Fresh"}}
    monkeypatch.setattr(
        "openbb_platform_api.utils.widgets.build_json",
        MagicMock(return_value=fresh),
    )
    # Point sys.executable at a real path under tmp_path so the derived
    # ``parent.parents[1] / "assets" / "widgets.json"`` location is
    # writable.
    fake_python = tmp_path / "envs" / "myenv" / "bin" / "python"
    fake_python.parent.mkdir(parents=True)
    fake_python.write_text("")
    monkeypatch.setattr("sys.executable", str(fake_python))

    result = widgets_service.get_widgets_json(
        _build=True,
        _openapi={},
        widget_exclude_filter=[],
        editable=True,
        widgets_path=None,  # ← exercises the default-path branch
    )
    assert result == fresh


def test_get_widgets_json_editable_falls_back_to_existing_when_write_fails(
    tmp_path, reset_widgets_service_state, monkeypatch
):
    """A disk-write failure during the editable build is logged but
    doesn't kill the response. When the existing file had content,
    that's what callers get back — favouring the user's stored config
    over an unsaved fresh build keeps the loaded session stable.
    """
    widgets_service.FIRST_RUN = False
    widgets_path = tmp_path / "widgets.json"
    existing = {"old": {"name": "Stale"}}
    widgets_path.write_text(json.dumps(existing))

    fresh = {"new": {"name": "Fresh"}}
    monkeypatch.setattr(
        "openbb_platform_api.utils.widgets.build_json",
        MagicMock(return_value=fresh),
    )

    real_open = open

    def failing_open(path, mode="r", *args, **kwargs):
        if "w" in mode:
            raise OSError("simulated write failure")
        return real_open(path, mode, *args, **kwargs)

    with (
        patch("builtins.open", side_effect=failing_open),
        patch("builtins.input", return_value="y"),
    ):
        result = widgets_service.get_widgets_json(
            _build=True,
            _openapi={},
            widget_exclude_filter=[],
            editable=True,
            widgets_path=str(widgets_path),
        )
    # Existing on-disk widgets returned because they were non-empty —
    # the function picks ``existing_widgets_json`` over the fresh
    # build when both are available and the write failed.
    assert result == existing


# ---------------------------------------------------------------------------
# Spec-driven source override — ``[\"Custom\"]`` → ``[spec_name]``
# ---------------------------------------------------------------------------


def test_get_widgets_json_overrides_custom_source_with_spec_source(
    reset_widgets_service_state, monkeypatch
):
    """Spec-driven launches stash the spec file's full name (extension
    included) on ``app.state.openbb_spec_source``. Every widget whose
    builder emitted the default ``["Custom"]`` source citation gets
    that label replaced with the spec filename so dashboards display
    the actual file the data came from
    (e.g. ``["fertilizer.spec"]`` for
    ``/etc/openbb/fertilizer.spec``).
    """
    monkeypatch.setattr(
        "openbb_platform_api.utils.widgets.build_json",
        lambda _o, _f: {
            "w1": {"source": ["Custom"], "name": "Widget 1"},
            "w2": {"source": ["Custom"], "name": "Widget 2"},
        },
    )
    app = MagicMock()
    app.routes = []
    app.state.openbb_spec_source = "fertilizer.spec"

    result = widgets_service.get_widgets_json(
        False, {}, [], editable=False, widgets_path=None, app=app
    )
    assert result["w1"]["source"] == ["fertilizer.spec"]
    assert result["w2"]["source"] == ["fertilizer.spec"]


def test_get_widgets_json_preserves_explicit_source_overrides(
    reset_widgets_service_state, monkeypatch
):
    """A widget whose ``source`` was explicitly set via
    ``widget_config`` (i.e. anything other than the default
    ``["Custom"]``) is left untouched — the spec-name override only
    replaces the default citation, never an author-supplied one.
    """
    monkeypatch.setattr(
        "openbb_platform_api.utils.widgets.build_json",
        lambda _o, _f: {
            "default_widget": {"source": ["Custom"], "name": "Auto"},
            "explicit_widget": {"source": ["FRED"], "name": "Hand-Set"},
        },
    )
    app = MagicMock()
    app.routes = []
    app.state.openbb_spec_source = "fertilizer.spec"

    result = widgets_service.get_widgets_json(
        False, {}, [], editable=False, widgets_path=None, app=app
    )
    # Default → overridden with spec filename.
    assert result["default_widget"]["source"] == ["fertilizer.spec"]
    # Explicit → untouched.
    assert result["explicit_widget"]["source"] == ["FRED"]


def test_get_widgets_json_no_override_when_spec_source_unset(
    reset_widgets_service_state, monkeypatch
):
    """Non-spec-driven launches (e.g. ``--app`` or default openbb-core)
    don't have ``openbb_spec_source`` on ``app.state``; the override
    is a no-op and the auto-generated ``["Custom"]`` source flows
    through.
    """
    monkeypatch.setattr(
        "openbb_platform_api.utils.widgets.build_json",
        lambda _o, _f: {"w1": {"source": ["Custom"], "name": "Widget 1"}},
    )
    # Plain MagicMock state — no ``openbb_spec_source`` attr; the
    # ``getattr(..., None)`` lookup in the helper returns None.
    app = MagicMock()
    app.routes = []
    app.state = MagicMock(spec=[])  # truly empty state namespace

    result = widgets_service.get_widgets_json(
        False, {}, [], editable=False, widgets_path=None, app=app
    )
    assert result["w1"]["source"] == ["Custom"]


def test_get_widgets_json_overrides_default_mcp_server_with_spec_source(
    reset_widgets_service_state, monkeypatch
):
    """``build_json`` hardcodes ``mcp_tool.mcp_server: "Open Data
    Platform"`` (v4 platform default). Spec-driven launches replace
    that with the spec file's name so the synthesized backend
    advertises itself under its OWN MCP namespace, not the
    platform's. The ``tool_id`` is also re-scoped with the spec
    stem prefix so MCP tool IDs stay globally unique across servers.
    """
    monkeypatch.setattr(
        "openbb_platform_api.utils.widgets.build_json",
        lambda _o, _f: {
            "w1": {
                "source": ["Custom"],
                "mcp_tool": {
                    "mcp_server": "Open Data Platform",
                    "tool_id": "resource_8bgf-5mdv.json",
                },
            },
            "w2": {
                "source": ["Custom"],
                "mcp_tool": {
                    "mcp_server": "Open Data Platform",
                    "tool_id": "equity_price_historical",
                },
            },
        },
    )
    app = MagicMock()
    app.routes = []
    app.state.openbb_spec_source = "fertilizer.spec"

    result = widgets_service.get_widgets_json(
        False, {}, [], editable=False, widgets_path=None, app=app
    )
    assert result["w1"]["mcp_tool"]["mcp_server"] == "fertilizer.spec"
    assert result["w2"]["mcp_tool"]["mcp_server"] == "fertilizer.spec"
    # ``tool_id`` gets the stem-prefixed scope so multiple spec-driven
    # launchers wired to the same MCP client don't collide.
    assert result["w1"]["mcp_tool"]["tool_id"] == "fertilizer__resource_8bgf-5mdv.json"
    assert result["w2"]["mcp_tool"]["tool_id"] == "fertilizer__equity_price_historical"


def test_get_widgets_json_tool_id_uses_path_stem_for_dotted_filenames(
    reset_widgets_service_state, monkeypatch
):
    """``Path().stem`` strips only the LAST extension, so a spec
    named ``my.app.spec`` becomes the namespace ``my.app``. Matches
    what most operators would call the namespace.
    """
    monkeypatch.setattr(
        "openbb_platform_api.utils.widgets.build_json",
        lambda _o, _f: {
            "w": {
                "source": ["Custom"],
                "mcp_tool": {
                    "mcp_server": "Open Data Platform",
                    "tool_id": "my_widget",
                },
            }
        },
    )
    app = MagicMock()
    app.routes = []
    app.state.openbb_spec_source = "my.app.spec"

    result = widgets_service.get_widgets_json(
        False, {}, [], editable=False, widgets_path=None, app=app
    )
    assert result["w"]["mcp_tool"]["tool_id"] == "my.app__my_widget"


def test_get_widgets_json_preserves_explicit_mcp_server_overrides(
    reset_widgets_service_state, monkeypatch
):
    """A widget whose ``mcp_tool.mcp_server`` was explicitly set via
    ``widget_config`` (anything other than the v4 platform default
    ``"Open Data Platform"``) is left untouched, including its
    ``tool_id``. The author owns the whole ``mcp_tool`` block when
    they override the namespace — the launcher doesn't second-guess
    the ID format.
    """
    monkeypatch.setattr(
        "openbb_platform_api.utils.widgets.build_json",
        lambda _o, _f: {
            "default_mcp": {
                "source": ["Custom"],
                "mcp_tool": {
                    "mcp_server": "Open Data Platform",
                    "tool_id": "default_mcp",
                },
            },
            "custom_mcp": {
                "source": ["Custom"],
                "mcp_tool": {
                    "mcp_server": "Hand-Set MCP",
                    "tool_id": "custom_mcp",
                },
            },
        },
    )
    app = MagicMock()
    app.routes = []
    app.state.openbb_spec_source = "fertilizer.spec"

    result = widgets_service.get_widgets_json(
        False, {}, [], editable=False, widgets_path=None, app=app
    )
    # Default → overridden with spec filename + stem-scoped tool_id.
    assert result["default_mcp"]["mcp_tool"]["mcp_server"] == "fertilizer.spec"
    assert result["default_mcp"]["mcp_tool"]["tool_id"] == "fertilizer__default_mcp"
    # Explicit → both fields untouched (author owns the namespace).
    assert result["custom_mcp"]["mcp_tool"]["mcp_server"] == "Hand-Set MCP"
    assert result["custom_mcp"]["mcp_tool"]["tool_id"] == "custom_mcp"


def test_get_widgets_json_skips_mcp_override_when_mcp_tool_missing_or_malformed(
    reset_widgets_service_state, monkeypatch
):
    """A widget without ``mcp_tool``, or with a non-dict
    ``mcp_tool``, is silently skipped — defensive against partial
    widget configs and forward-compatible if the schema changes.
    """
    monkeypatch.setattr(
        "openbb_platform_api.utils.widgets.build_json",
        lambda _o, _f: {
            "no_mcp": {"source": ["Custom"]},
            "malformed_mcp": {"source": ["Custom"], "mcp_tool": "not a dict"},
        },
    )
    app = MagicMock()
    app.routes = []
    app.state.openbb_spec_source = "fertilizer.spec"

    # No crash; both widgets still get the source override.
    result = widgets_service.get_widgets_json(
        False, {}, [], editable=False, widgets_path=None, app=app
    )
    assert result["no_mcp"]["source"] == ["fertilizer.spec"]
    assert "mcp_tool" not in result["no_mcp"]
    assert result["malformed_mcp"]["source"] == ["fertilizer.spec"]
    assert result["malformed_mcp"]["mcp_tool"] == "not a dict"


def test_get_widgets_json_no_override_when_app_is_none(
    reset_widgets_service_state, monkeypatch
):
    """Defensive: ``app`` may be ``None`` in code paths that don't
    pass it through (legacy callers). The override helper returns
    silently rather than raising on ``None.state``.
    """
    monkeypatch.setattr(
        "openbb_platform_api.utils.widgets.build_json",
        lambda _o, _f: {"w1": {"source": ["Custom"], "name": "Widget 1"}},
    )
    result = widgets_service.get_widgets_json(
        False, {}, [], editable=False, widgets_path=None, app=None
    )
    assert result["w1"]["source"] == ["Custom"]
