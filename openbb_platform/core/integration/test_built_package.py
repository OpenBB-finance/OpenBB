"""End-to-end integration tests using a real built ``openbb`` static package.

These tests rely on the ``fake_extension_installed`` / ``run_in_obb``
fixtures defined in ``conftest.py``. The fixtures:

1. Write a synthetic OpenBB extension distribution to a temp dir.
2. ``pip install`` it as ``openbb-fake-integration`` so its
   ``openbb_core_extension`` and ``openbb_provider_extension`` entry
   points are visible to ``importlib.metadata``.
3. Spawn a subprocess that imports ``openbb`` with
   ``OPENBB_AUTO_BUILD=true``, which runs the real ``PackageBuilder``
   and emits ``openbb/package/fake_integration.py``.
4. After the session, uninstall the distribution and restore the
   pre-test contents of ``openbb/package`` and ``openbb/assets``.

The tests below then run small snippets in a fresh interpreter and
verify ``obb.fake_integration.list_indicators(...)`` is reachable on
the freshly-built static package.
"""

import pytest

pytestmark = pytest.mark.integration


def test_built_package_emits_fake_integration_module(fake_extension_installed):
    """``openbb-build`` writes a real ``fake_integration.py`` for the synthetic extension."""
    package_dir = fake_extension_installed["package_dir"]
    module = package_dir / "fake_integration.py"
    assert module.exists()
    source = module.read_text(encoding="utf-8")
    assert "list_indicators" in source
    assert "AUTO-GENERATED" in source.upper() or "auto-generated" in source


def test_obb_exposes_fake_integration_namespace(run_in_obb):
    """``from openbb import obb`` exposes the freshly-built ``fake_integration`` namespace."""
    snippet = (
        "RESULT = {"
        "    'has_namespace': hasattr(obb, 'fake_integration'),"
        "    'has_command': hasattr(getattr(obb, 'fake_integration', None),"
        "                            'list_indicators'),"
        "}"
    )
    result = run_in_obb(snippet)
    assert result["has_namespace"], (
        "obb.fake_integration is missing — generated package was not picked up"
    )
    assert result["has_command"], "obb.fake_integration.list_indicators is missing"


def test_obb_command_dispatches_through_real_runner(run_in_obb):
    """Calling the generated method runs through the real ``CommandRunner`` and synthetic provider."""
    snippet = (
        "out = obb.fake_integration.list_indicators(provider='fake_integration')\n"
        "rows = [r.model_dump() if hasattr(r, 'model_dump') else dict(r) "
        "        for r in out.results]\n"
        "RESULT = {'rows': rows}\n"
    )
    result = run_in_obb(snippet)
    assert len(result["rows"]) == 1
    row = result["rows"][0]
    assert row["symbol"] == "FAKE"
    assert row["extra"] == "ok"


def test_obb_coverage_reports_fake_integration_provider(run_in_obb):
    """The ``Coverage`` view on a real built ``obb`` includes the synthetic provider."""
    snippet = (
        "RESULT = {"
        "    'providers': sorted(obb.coverage.providers.keys()),"
        "    'commands': sorted(obb.coverage.commands.keys()),"
        "}"
    )
    result = run_in_obb(snippet)
    assert "fake_integration" in result["providers"]
    assert any("list_indicators" in cmd for cmd in result["commands"]), (
        f"expected list_indicators in commands, got {result['commands']!r}"
    )


# ---------------------------------------------------------------------------
# OBBject built-in conversion methods (require pandas)
# ---------------------------------------------------------------------------


pandas_required = pytest.mark.requires_pandas


@pandas_required
def test_obbject_to_dict_returns_real_records(run_in_obb):
    """``OBBject.to_dict(orient='records')`` round-trips real provider data."""
    snippet = (
        "out = obb.fake_integration.list_indicators(provider='fake_integration')\n"
        "RESULT = {'records': out.to_dict(orient='records')}\n"
    )
    result = run_in_obb(snippet)
    assert isinstance(result["records"], list)
    assert len(result["records"]) == 1
    assert result["records"][0]["symbol"] == "FAKE"
    assert result["records"][0]["extra"] == "ok"


@pandas_required
def test_obbject_to_dataframe_via_inline_check(run_in_obb):
    """``OBBject.to_dataframe()`` produces a real ``pandas.DataFrame``.

    The DataFrame itself can't cross the JSON boundary, so the check is
    performed in the child interpreter and only the boolean is returned.
    """
    snippet = (
        "import pandas as pd\n"
        "out = obb.fake_integration.list_indicators(provider='fake_integration')\n"
        "df = out.to_dataframe()\n"
        "RESULT = {"
        "    'is_dataframe': isinstance(df, pd.DataFrame),"
        "    'columns': sorted(df.columns.tolist()),"
        "    'symbol_value': df['symbol'].iloc[0],"
        "}\n"
    )
    result = run_in_obb(snippet)
    assert result["is_dataframe"] is True
    assert "symbol" in result["columns"]
    assert "extra" in result["columns"]
    assert result["symbol_value"] == "FAKE"


@pandas_required
def test_obbject_to_llm_emits_json_string(run_in_obb):
    """``OBBject.to_llm()`` returns a JSON-encoded string of the records."""
    snippet = (
        "import json\n"
        "out = obb.fake_integration.list_indicators(provider='fake_integration')\n"
        "llm = out.to_llm()\n"
        "RESULT = {"
        "    'is_str': isinstance(llm, str),"
        "    'parsed': json.loads(llm),"
        "}\n"
    )
    result = run_in_obb(snippet)
    assert result["is_str"] is True
    assert isinstance(result["parsed"], list)
    assert result["parsed"][0]["symbol"] == "FAKE"


# ---------------------------------------------------------------------------
# OBBject extension (accessor) — openbb_obbject_extension entry point
# ---------------------------------------------------------------------------


def test_fake_accessor_is_registered_on_obbject_class(run_in_obb):
    """The ``openbb_obbject_extension`` entry point registers the accessor on ``OBBject``.

    ``Extension.obbject_accessor`` adds the accessor name to
    ``OBBject.accessors`` and sets the ``CachedAccessor`` descriptor as
    a class attribute. Both must be true on ``import openbb``.
    """
    snippet = (
        "from openbb_core.app.model.obbject import OBBject\n"
        "RESULT = {"
        "    'in_accessors': 'fake_accessor' in OBBject.accessors,"
        "    'has_descriptor': hasattr(OBBject, 'fake_accessor'),"
        "}\n"
    )
    result = run_in_obb(snippet)
    assert result["in_accessors"], (
        "fake_accessor was not added to OBBject.accessors — openbb_obbject_extension entry point did not load"
    )
    assert result["has_descriptor"], "OBBject has no fake_accessor descriptor"


def test_fake_accessor_methods_run_against_real_obbject(run_in_obb):
    """The custom accessor's methods execute against a real ``OBBject`` instance."""
    snippet = (
        "out = obb.fake_integration.list_indicators(provider='fake_integration')\n"
        "RESULT = {"
        "    'upper': out.fake_accessor.upper_symbols(),"
        "    'count': out.fake_accessor.row_count(),"
        "}\n"
    )
    result = run_in_obb(snippet)
    assert result["upper"] == ["FAKE"]
    assert result["count"] == 1


def test_fake_accessor_instance_is_cached_per_obbject(run_in_obb):
    """``CachedAccessor`` caches the accessor instance on the OBBject after first access."""
    snippet = (
        "out = obb.fake_integration.list_indicators(provider='fake_integration')\n"
        "first = out.fake_accessor\n"
        "second = out.fake_accessor\n"
        "RESULT = {'identical': first is second}\n"
    )
    result = run_in_obb(snippet)
    assert result["identical"] is True
