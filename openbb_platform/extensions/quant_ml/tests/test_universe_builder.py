"""Universe builder tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from openbb_quant_ml.service import universe_builder as ub


def _write_cache(path: Path, symbol: str, price: float, volume: float, periods: int = 300) -> None:
    dates = pd.date_range("2024-01-01", periods=periods, freq="B")
    frame = pd.DataFrame(
        {
            "date": dates,
            "open": price * 0.99,
            "high": price * 1.01,
            "low": price * 0.98,
            "close": price,
            "volume": volume,
            "symbol": symbol,
        }
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)


def test_build_universe_with_filters(monkeypatch, tmp_path: Path):
    cfg_path = tmp_path / "universe.yaml"
    cfg_path.write_text(
        "\n".join(
            [
                'version: "v1"',
                "assets:",
                "  - symbol: SPY",
                "    category: us_equity_etf",
                "  - symbol: LOWVOL",
                "    category: test",
                "filters:",
                "  min_price: 3",
                "  min_adv_usd: 2000000",
                "  min_history_days: 200",
                "  max_missing_ratio: 0.2",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(ub, "UNIVERSE_CONFIG_PATH", cfg_path)
    monkeypatch.setattr(ub, "UNIVERSE_INPUT_DIR", tmp_path / "universe_input")
    monkeypatch.setattr(ub, "UNIVERSE_META_PATH", tmp_path / "universe_meta.json")
    monkeypatch.setattr(ub, "RAW_STORE_DIR", tmp_path / "raw_store")
    monkeypatch.setattr(ub, "CACHE_DIR", tmp_path / "cache")

    _write_cache(tmp_path / "raw_store" / "SPY.parquet", "SPY", price=500.0, volume=5_000_000.0)
    _write_cache(tmp_path / "raw_store" / "LOWVOL.parquet", "LOWVOL", price=2.0, volume=50_000.0)

    payload = ub.build_universe(universe_id="default")
    assert "SPY" in payload["train_universe"]
    assert "SPY" in payload["trade_universe"]
    assert "LOWVOL" not in payload["trade_universe"]


def test_local_empty_csv_does_not_fallback(monkeypatch, tmp_path: Path):
    cfg_path = tmp_path / "universe.yaml"
    cfg_path.write_text(
        "\n".join(
            [
                'version: "v1"',
                "assets:",
                "  - symbol: SPY",
                "    category: us_equity_etf",
            ]
        ),
        encoding="utf-8",
    )

    universe_dir = tmp_path / "universe_input"
    universe_dir.mkdir(parents=True, exist_ok=True)
    (universe_dir / "sp500.csv").write_text("symbol\n", encoding="utf-8")

    monkeypatch.setattr(ub, "UNIVERSE_CONFIG_PATH", cfg_path)
    monkeypatch.setattr(ub, "UNIVERSE_INPUT_DIR", universe_dir)
    monkeypatch.setattr(ub, "UNIVERSE_META_PATH", tmp_path / "universe_meta.json")
    monkeypatch.setattr(ub, "RAW_STORE_DIR", tmp_path / "raw_store")
    monkeypatch.setattr(ub, "CACHE_DIR", tmp_path / "cache")

    payload = ub.build_universe(universe_id="sp500")
    assert payload["train_universe"] == []
    assert payload["trade_universe"] == []
