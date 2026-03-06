"""Tests for unused features audit helpers."""

from __future__ import annotations

import json
from pathlib import Path

from openbb_platform.tools import unused_features_audit as ufa


class _DummyDist:
    def __init__(self, version: str):
        self.version = version


class _DummyEntryPoint:
    def __init__(self, name: str, version: str):
        self.name = name
        self.dist = _DummyDist(version)


def test_load_entry_points(monkeypatch):
    data = {
        "openbb_core_extension": [_DummyEntryPoint("equity", "1.0.0")],
        "openbb_provider_extension": [_DummyEntryPoint("yfinance", "1.0.0")],
        "openbb_obbject_extension": [],
    }

    def _entry_points(*, group):  # noqa: ANN001
        return data[group]

    monkeypatch.setattr(ufa.importlib_metadata, "entry_points", _entry_points)
    payload = ufa._load_entry_points()
    assert payload["openbb_core_extension"] == ["equity@1.0.0"]
    assert payload["openbb_provider_extension"] == ["yfinance@1.0.0"]


def test_parse_extensions_py_declared_names(tmp_path: Path):
    path = tmp_path / "__extensions__.py"
    path.write_text(
        "\n".join(
            [
                '"""',
                "Extensions:",
                "    - equity@1.0.0",
                "    - yfinance@1.0.0",
                '"""',
            ]
        ),
        encoding="utf-8",
    )
    names = ufa._parse_extensions_py_declared_names(path)
    assert names == ["equity", "yfinance"]


def test_generate_audit(tmp_path: Path, monkeypatch):
    repo = tmp_path
    (repo / "openbb_platform/core/openbb/assets").mkdir(parents=True, exist_ok=True)
    (repo / "openbb_platform/core/openbb/package").mkdir(parents=True, exist_ok=True)
    (repo / "desktop/src/lib").mkdir(parents=True, exist_ok=True)
    (repo / "desktop/src/routes").mkdir(parents=True, exist_ok=True)
    (repo / "desktop/src/components").mkdir(parents=True, exist_ok=True)

    reference = {
        "info": {
            "extensions": {
                "openbb_core_extension": ["equity@1.0.0"],
                "openbb_provider_extension": ["yfinance@1.0.0"],
                "openbb_obbject_extension": [],
            }
        }
    }
    (repo / "openbb_platform/core/openbb/assets/reference.json").write_text(
        json.dumps(reference),
        encoding="utf-8",
    )
    (repo / "openbb_platform/core/openbb/package/__extensions__.py").write_text(
        '"""- equity@1.0.0\\n- yfinance@1.0.0"""',
        encoding="utf-8",
    )
    (repo / "desktop/src/lib/quantApi.ts").write_text(
        "\n".join(
            [
                "export function usedQuant() { return 1; }",
                "export function unusedQuant() { return 2; }",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "desktop/src/lib/macroApi.ts").write_text(
        "export function usedMacro() { return 1; }",
        encoding="utf-8",
    )
    (repo / "desktop/src/routes/quant.tsx").write_text(
        "import { usedQuant } from '../lib/quantApi'; usedQuant();",
        encoding="utf-8",
    )
    (repo / "desktop/src/components/macro.tsx").write_text(
        "import { usedMacro } from '../lib/macroApi'; usedMacro();",
        encoding="utf-8",
    )
    (repo / "desktop/src/routes/macro.tsx").write_text(
        "import { usedMacro } from '../lib/macroApi'; usedMacro();",
        encoding="utf-8",
    )
    (repo / "desktop/src/routes/execution.tsx").write_text(
        "import { usedQuant } from '../lib/quantApi'; usedQuant();",
        encoding="utf-8",
    )
    (repo / "desktop/src/routes/ops.tsx").write_text(
        "import { usedQuant } from '../lib/quantApi'; usedQuant();",
        encoding="utf-8",
    )

    data = {
        "openbb_core_extension": [_DummyEntryPoint("equity", "1.0.0")],
        "openbb_provider_extension": [_DummyEntryPoint("yfinance", "1.0.0")],
        "openbb_obbject_extension": [],
    }

    def _entry_points(*, group):  # noqa: ANN001
        return data[group]

    monkeypatch.setattr(ufa.importlib_metadata, "entry_points", _entry_points)
    report = ufa.generate_audit(repo)

    assert report["metrics"]["reference_drift"] == 0
    assert report["metrics"]["extensions_py_drift"] == 0
    assert report["desktop_api_usage"]["quantApi"]["unused_exports"] == ["unusedQuant"]


def test_load_repo_extension_map_prefers_local_pyprojects(tmp_path: Path):
    repo = tmp_path
    ext_dir = repo / "openbb_platform" / "extensions" / "quant_ml"
    provider_dir = repo / "openbb_platform" / "providers" / "yfinance"
    ext_dir.mkdir(parents=True, exist_ok=True)
    provider_dir.mkdir(parents=True, exist_ok=True)

    (ext_dir / "pyproject.toml").write_text(
        "\n".join(
            [
                "[tool.poetry]",
                'name = "openbb-quant-ml"',
                'version = "0.1.0"',
                "",
                '[tool.poetry.plugins."openbb_core_extension"]',
                'quant_ml = "openbb_quant_ml.quant_ml_router:router"',
                'macro = "openbb_quant_ml.macro_alias_router:router"',
            ]
        ),
        encoding="utf-8",
    )
    (provider_dir / "pyproject.toml").write_text(
        "\n".join(
            [
                "[tool.poetry]",
                'name = "openbb-yfinance"',
                'version = "1.5.2"',
                "",
                '[tool.poetry.plugins."openbb_provider_extension"]',
                'yfinance = "openbb_yfinance:yfinance_provider"',
            ]
        ),
        encoding="utf-8",
    )

    payload = ufa._load_repo_extension_map(repo)
    assert payload["openbb_core_extension"] == ["macro@0.1.0", "quant_ml@0.1.0"]
    assert payload["openbb_provider_extension"] == ["yfinance@1.5.2"]


def test_estimate_unused_route_count_handles_quant_hooks(tmp_path: Path):
    desktop_src = tmp_path / "desktop" / "src"
    (desktop_src / "routes").mkdir(parents=True, exist_ok=True)
    (desktop_src / "hooks").mkdir(parents=True, exist_ok=True)
    (desktop_src / "components" / "macro").mkdir(parents=True, exist_ok=True)

    (desktop_src / "routes" / "quant.tsx").write_text(
        "import { useQuantTraining } from '../hooks/useQuantTraining'; useQuantTraining;",
        encoding="utf-8",
    )
    (desktop_src / "hooks" / "useQuantTraining.ts").write_text(
        'import { startTrain } from "../lib/quantApi"; startTrain;',
        encoding="utf-8",
    )
    (desktop_src / "routes" / "dashboard.tsx").write_text(
        'import { fetchDashboardBootstrap } from "../lib/quantApi"; fetchDashboardBootstrap;',
        encoding="utf-8",
    )
    (desktop_src / "routes" / "trading.tsx").write_text(
        'import { fetchTradingStatus } from "../lib/quantApi"; fetchTradingStatus;',
        encoding="utf-8",
    )
    (desktop_src / "routes" / "macro.tsx").write_text(
        'import { MacroPage } from "../components/macro/MacroPage"; MacroPage;',
        encoding="utf-8",
    )
    (desktop_src / "components" / "macro" / "MacroPage.tsx").write_text(
        'import { fetchMacroCatalog } from "../../lib/macroApi"; fetchMacroCatalog;',
        encoding="utf-8",
    )
    (desktop_src / "routes" / "execution.tsx").write_text(
        'import { previewExecutionOrders } from "../lib/quantApi"; previewExecutionOrders;',
        encoding="utf-8",
    )
    (desktop_src / "routes" / "ops.tsx").write_text(
        'import { fetchOpsStatus } from "../lib/quantApi"; fetchOpsStatus;',
        encoding="utf-8",
    )

    assert ufa._estimate_unused_route_count(desktop_src) == 0


def test_estimate_unused_route_count_flags_missing_route_coverage(tmp_path: Path):
    desktop_src = tmp_path / "desktop" / "src"
    (desktop_src / "routes").mkdir(parents=True, exist_ok=True)
    (desktop_src / "components" / "macro").mkdir(parents=True, exist_ok=True)

    (desktop_src / "routes" / "quant.tsx").write_text("export default function Quant() { return null; }", encoding="utf-8")
    (desktop_src / "routes" / "dashboard.tsx").write_text(
        'import { fetchDashboardBootstrap } from "../lib/quantApi"; fetchDashboardBootstrap;',
        encoding="utf-8",
    )
    (desktop_src / "routes" / "trading.tsx").write_text(
        'import { fetchTradingStatus } from "../lib/quantApi"; fetchTradingStatus;',
        encoding="utf-8",
    )
    (desktop_src / "routes" / "macro.tsx").write_text(
        'import { fetchMacroCatalog } from "../lib/macroApi"; fetchMacroCatalog;',
        encoding="utf-8",
    )
    (desktop_src / "routes" / "execution.tsx").write_text(
        'import { previewExecutionOrders } from "../lib/quantApi"; previewExecutionOrders;',
        encoding="utf-8",
    )
    (desktop_src / "routes" / "ops.tsx").write_text(
        'import { fetchOpsStatus } from "../lib/quantApi"; fetchOpsStatus;',
        encoding="utf-8",
    )

    assert ufa._estimate_unused_route_count(desktop_src) == 1


def test_diff_lists_ignores_version_only_changes():
    diff = ufa._diff_lists(
        ["quant_ml@0.1.0", "yfinance@1.5.2"],
        ["quant_ml@0.0.9", "yfinance@1.5.1"],
    )

    assert diff.missing == []
    assert diff.stale == []
