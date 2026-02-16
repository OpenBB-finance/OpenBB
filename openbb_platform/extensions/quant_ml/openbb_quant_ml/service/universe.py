"""Universe config helpers."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import yaml

from openbb_quant_ml.service.constants import UNIVERSE_CONFIG_PATH
from openbb_quant_ml.service.universe_builder import (
    UNIVERSE_INPUT_DIR,
)

UNIVERSE_MINIMUM_COUNTS: dict[str, int] = {
    "sp500": 450,
    "nasdaq100": 95,
    "dow30": 25,
    "sox": 25,
    "kospi200": 180,
    "kosdaq100": 90,
}


def load_universe_config() -> dict[str, Any]:
    """Load universe configuration YAML."""
    with UNIVERSE_CONFIG_PATH.open(encoding="utf-8") as file:
        payload = yaml.safe_load(file) or {}
    payload.setdefault("version", "v1")
    payload.setdefault("assets", [])
    return payload


def get_default_symbols() -> list[str]:
    """Return default universe symbols."""
    payload = load_universe_config()
    assets = payload.get("assets", [])
    return [asset["symbol"] for asset in assets if asset.get("symbol")]


def get_universe_minimum_required(universe_id: str | None) -> int:
    """Return minimum required symbol count for guarded universe ids."""
    key = str(universe_id or "").strip().lower()
    return int(UNIVERSE_MINIMUM_COUNTS.get(key, 0))


def get_universe_size_status(universe_id: str | None, symbols: list[str]) -> tuple[int, int, bool]:
    """Return (actual_count, minimum_required, meets_minimum) tuple."""
    actual = len({str(item).strip().upper() for item in symbols if str(item).strip()})
    minimum = get_universe_minimum_required(universe_id)
    meets_minimum = minimum <= 0 or actual >= minimum
    return actual, minimum, meets_minimum


def list_universe_ids() -> list[str]:
    """List universe identifiers discoverable from local universe files."""
    base = Path(UNIVERSE_INPUT_DIR)
    ids: set[str] = {"default"}
    if base.exists():
        for path in base.glob("*.csv"):
            ids.add(path.stem)
        for path in base.glob("*.txt"):
            ids.add(path.stem)
    return sorted(ids)


def universe_file_exists(universe_id: str) -> bool:
    """Return True when a local file exists for the given universe id."""
    key = str(universe_id or "").strip()
    if not key or key == "default":
        return True if key == "default" else False
    base = Path(UNIVERSE_INPUT_DIR)
    return (base / f"{key}.csv").exists() or (base / f"{key}.txt").exists()


def get_universe_file_path(universe_id: str) -> Path | None:
    """Return local universe file path when present."""
    key = str(universe_id or "").strip()
    if not key or key == "default":
        return None
    base = Path(UNIVERSE_INPUT_DIR)
    csv_path = base / f"{key}.csv"
    if csv_path.exists():
        return csv_path
    txt_path = base / f"{key}.txt"
    if txt_path.exists():
        return txt_path
    return None


def get_universe_count_hint(universe_id: str) -> int:
    """Return quick symbol-count hint from local files without full parsing."""
    key = str(universe_id or "").strip()
    if key == "default":
        return len(get_default_symbols())
    path = get_universe_file_path(key)
    if path is None:
        return 0
    try:
        if path.suffix.lower() == ".txt":
            rows = path.read_text(encoding="utf-8").splitlines()
            return len([row for row in rows if row.strip()])
        rows = path.read_text(encoding="utf-8").splitlines()
        if not rows:
            return 0
        data_rows = [row for row in rows[1:] if row.strip()]
        return len(data_rows)
    except OSError:
        return 0


def _read_symbols_from_universe_file(path: Path) -> list[str]:
    try:
        if path.suffix.lower() == ".txt":
            rows = path.read_text(encoding="utf-8").splitlines()
            return [row.strip().upper() for row in rows if row.strip()]
        symbols: list[str] = []
        with path.open(encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            columns = [column for column in (reader.fieldnames or []) if column]
            symbol_col = "symbol" if "symbol" in columns else columns[0] if columns else None
            if symbol_col is None:
                return symbols
            for row in reader:
                value = str(row.get(symbol_col, "")).strip().upper()
                if value:
                    symbols.append(value)
        return symbols
    except OSError:
        return []


def get_symbols_for_universe(universe_id: str | None) -> list[str]:
    """Resolve symbols from universe id with explicit unknown-id behavior."""
    if universe_id is None:
        return get_default_symbols()

    key = str(universe_id).strip()
    if not key:
        return get_default_symbols()
    if key == "default":
        return get_default_symbols()

    path = get_universe_file_path(key)
    if path is None:
        return []

    symbols = _read_symbols_from_universe_file(path)
    return sorted({str(item) for item in symbols if str(item).strip()})
