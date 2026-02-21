"""Universe resolve policy tests."""

from __future__ import annotations

from pathlib import Path

from openbb_quant_ml.service import (
    universe as uv,
    universe_builder as ub,
)
from openbb_quant_ml.service.universe_policy import get_legacy_universe_meta


def test_unknown_universe_returns_empty(monkeypatch, tmp_path: Path):
    universe_dir = tmp_path / "universe_input"
    universe_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(ub, "UNIVERSE_INPUT_DIR", universe_dir)
    monkeypatch.setattr(uv, "UNIVERSE_INPUT_DIR", universe_dir)

    assert uv.get_symbols_for_universe("does_not_exist") == []


def test_default_universe_returns_default_symbols(monkeypatch, tmp_path: Path):
    cfg_path = tmp_path / "universe.yaml"
    cfg_path.write_text(
        "\n".join(
            [
                'version: "v1"',
                "assets:",
                "  - symbol: SPY",
                "    category: us_equity_etf",
                "  - symbol: QQQ",
                "    category: us_tech_etf",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(uv, "UNIVERSE_CONFIG_PATH", cfg_path)

    symbols = uv.get_symbols_for_universe("default")
    assert symbols == ["SPY", "QQQ"]


def test_universe_size_status_for_guarded_universe():
    actual, minimum, meets = uv.get_universe_size_status("sp500", ["AAPL", "MSFT"])
    assert actual == 2
    assert minimum == 450
    assert meets is False


def test_local_csv_symbols_are_resolved_without_filter_fallback(monkeypatch, tmp_path: Path):
    universe_dir = tmp_path / "universe_input"
    universe_dir.mkdir(parents=True, exist_ok=True)
    (universe_dir / "sp500.csv").write_text("symbol\nMSFT\nAAPL\n", encoding="utf-8")

    monkeypatch.setattr(ub, "UNIVERSE_INPUT_DIR", universe_dir)
    monkeypatch.setattr(uv, "UNIVERSE_INPUT_DIR", universe_dir)

    assert uv.get_symbols_for_universe("sp500") == ["AAPL", "MSFT"]


def test_global_core_equity_alias_resolves_to_all_in_one(monkeypatch, tmp_path: Path):
    universe_dir = tmp_path / "universe_input"
    universe_dir.mkdir(parents=True, exist_ok=True)
    (universe_dir / "all_in_one.csv").write_text("symbol\nMSFT\nAAPL\n", encoding="utf-8")
    monkeypatch.setattr(ub, "UNIVERSE_INPUT_DIR", universe_dir)
    monkeypatch.setattr(uv, "UNIVERSE_INPUT_DIR", universe_dir)

    assert uv.get_symbols_for_universe("global_core_equity") == ["AAPL", "MSFT"]


def test_legacy_universe_meta_marks_deprecated():
    meta = get_legacy_universe_meta("sp500")
    assert meta["deprecated"] is True
    assert meta["replacement_id"] == "global_core_equity"
