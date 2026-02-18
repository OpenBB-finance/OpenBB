"""Universe builder with local-file and quality-filter support."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from openbb_quant_ml.service.constants import ARTIFACT_ROOT, CACHE_DIR, RAW_STORE_DIR, UNIVERSE_CONFIG_PATH
from openbb_quant_ml.service.storage import load_json, save_json, utc_now_iso

UNIVERSE_INPUT_DIR = Path(__file__).resolve().parent.parent / "universe"
UNIVERSE_META_PATH = ARTIFACT_ROOT / "universe" / "universe_meta.json"


@dataclass
class UniverseFilters:
    min_price: float = 3.0
    min_adv_usd: float = 2_000_000.0
    min_history_days: int = 252
    max_missing_ratio: float = 0.15


def _safe_symbol(symbol: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"_", "-", "."} else "_" for ch in str(symbol))


def _read_symbols_from_text(path: Path) -> list[str]:
    rows = path.read_text(encoding="utf-8").splitlines()
    return [row.strip().upper() for row in rows if row.strip()]


def _read_symbols_from_csv(path: Path) -> list[str]:
    symbols: list[str] = []
    with path.open(encoding="utf-8") as file:
        reader = csv.DictReader(file)
        cols = [col for col in (reader.fieldnames or []) if col]
        symbol_col = "symbol" if "symbol" in cols else cols[0] if cols else None
        if symbol_col is None:
            return symbols
        for row in reader:
            value = str(row.get(symbol_col, "")).strip().upper()
            if value:
                symbols.append(value)
    return symbols


def _load_config() -> dict[str, Any]:
    if not UNIVERSE_CONFIG_PATH.exists():
        return {"assets": [], "universe_sets": {}}
    import yaml

    with UNIVERSE_CONFIG_PATH.open(encoding="utf-8") as file:
        payload = yaml.safe_load(file) or {}
    payload.setdefault("assets", [])
    payload.setdefault("universe_sets", {})
    payload.setdefault("filters", {})
    return payload


def _local_symbols(universe_id: str) -> list[str]:
    txt = UNIVERSE_INPUT_DIR / f"{universe_id}.txt"
    csv_path = UNIVERSE_INPUT_DIR / f"{universe_id}.csv"
    if txt.exists():
        return _read_symbols_from_text(txt)
    if csv_path.exists():
        return _read_symbols_from_csv(csv_path)
    return []


def _cached_price_path(symbol: str) -> Path | None:
    candidates = [
        RAW_STORE_DIR / f"{_safe_symbol(symbol)}.parquet",
        CACHE_DIR / f"{_safe_symbol(symbol)}.parquet",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def _load_cached_symbol_frame(symbol: str) -> pd.DataFrame:
    path = _cached_price_path(symbol)
    if path is None:
        return pd.DataFrame()
    frame = pd.read_parquet(path)
    if frame.empty:
        return frame
    frame["date"] = pd.to_datetime(frame["date"]).dt.tz_localize(None)
    return frame.sort_values("date").reset_index(drop=True)


def _quality_stats(frame: pd.DataFrame) -> dict[str, float]:
    if frame.empty:
        return {
            "last_price": 0.0,
            "adv_usd": 0.0,
            "history_days": 0.0,
            "missing_ratio": 1.0,
        }
    close = pd.to_numeric(frame.get("close"), errors="coerce")
    volume = pd.to_numeric(frame.get("volume"), errors="coerce")
    adv = (close * volume).tail(60).mean()
    return {
        "last_price": float(close.dropna().iloc[-1]) if close.dropna().shape[0] else 0.0,
        "adv_usd": float(adv) if pd.notna(adv) else 0.0,
        "history_days": float(frame["date"].nunique()),
        "missing_ratio": float(close.isna().mean()),
    }


def build_universe(
    universe_id: str | None = None,
    filters: UniverseFilters | None = None,
    end_date: date | None = None,
) -> dict[str, Any]:
    """Build train/trade universe from configured/local sources."""
    universe_key = str(universe_id or "default").strip() or "default"
    cfg = _load_config()
    active_filters = filters or UniverseFilters()
    cfg_filters = cfg.get("filters", {})
    if isinstance(cfg_filters, dict):
        active_filters = UniverseFilters(
            min_price=float(cfg_filters.get("min_price", active_filters.min_price)),
            min_adv_usd=float(cfg_filters.get("min_adv_usd", active_filters.min_adv_usd)),
            min_history_days=int(cfg_filters.get("min_history_days", active_filters.min_history_days)),
            max_missing_ratio=float(cfg_filters.get("max_missing_ratio", active_filters.max_missing_ratio)),
        )

    txt_path = UNIVERSE_INPUT_DIR / f"{universe_key}.txt"
    csv_path = UNIVERSE_INPUT_DIR / f"{universe_key}.csv"
    local_found = txt_path.exists() or csv_path.exists()

    symbols = _local_symbols(universe_key) if local_found else []
    if (not symbols) and (not local_found):
        sets = cfg.get("universe_sets", {})
        configured = sets.get(universe_key, {}) if isinstance(sets, dict) else {}
        if isinstance(configured, dict):
            symbols = [str(item).upper() for item in configured.get("symbols", []) if str(item).strip()]
    if (not symbols) and (not local_found):
        symbols = [str(item.get("symbol", "")).upper() for item in cfg.get("assets", []) if item.get("symbol")]
    symbols = sorted(set(symbols))

    stats_rows: list[dict[str, Any]] = []
    for symbol in symbols:
        frame = _load_cached_symbol_frame(symbol)
        stats = _quality_stats(frame)
        stats_rows.append({"symbol": symbol, **stats})

    train_universe: list[str] = []
    trade_universe: list[str] = []
    for row in stats_rows:
        if row["last_price"] >= active_filters.min_price and row["adv_usd"] >= active_filters.min_adv_usd:
            trade_universe.append(str(row["symbol"]))
        if (
            row["last_price"] >= active_filters.min_price
            and row["adv_usd"] >= active_filters.min_adv_usd
            and row["history_days"] >= active_filters.min_history_days
            and row["missing_ratio"] <= active_filters.max_missing_ratio
        ):
            train_universe.append(str(row["symbol"]))

    # Cache-miss fallback: keep configured symbols if no rows passed filters yet.
    if not train_universe:
        train_universe = symbols
    if not trade_universe:
        trade_universe = symbols

    payload = {
        "universe_id": universe_key,
        "as_of_date": (end_date or date.today()).isoformat(),
        "filters": {
            "min_price": active_filters.min_price,
            "min_adv_usd": active_filters.min_adv_usd,
            "min_history_days": active_filters.min_history_days,
            "max_missing_ratio": active_filters.max_missing_ratio,
        },
        "train_universe": sorted(set(train_universe)),
        "trade_universe": sorted(set(trade_universe)),
        "symbol_stats": stats_rows,
        "updated_at": utc_now_iso(),
    }

    stored = load_json(UNIVERSE_META_PATH, default={"universes": {}})
    universes = stored.setdefault("universes", {})
    universes[universe_key] = payload
    save_json(UNIVERSE_META_PATH, stored)
    return payload
