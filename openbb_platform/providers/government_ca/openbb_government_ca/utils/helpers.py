"""Runtime helpers shared by the BoC and StatsCan fetchers."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any


def safe_float(value: Any) -> float | None:
    """Coerce *value* to ``float``; return ``None`` on failure or empty."""
    if value is None:
        return None
    if isinstance(value, str):
        s = value.strip()
        if s in {"", "..", "...", "NaN", "nan", "N/A", "n/a", "NA"}:
            return None
        try:
            return float(s)
        except ValueError:
            return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def parse_observation_date(value: str) -> date | None:
    """Parse a date string from either BoC Valet or StatsCan SDMX.

    Supports ISO daily (``2024-01-15``), monthly (``2024-01``),
    quarterly (``2024-Q1``), and annual (``2024``) formats.
    """
    if not value or not isinstance(value, str):
        return None
    s = value.strip()
    if not s:
        return None

    if "-Q" in s:
        year_str, q_str = s.split("-Q", 1)
        try:
            year = int(year_str)
            quarter = int(q_str)
        except ValueError:
            return None
        if quarter < 1 or quarter > 4:
            return None
        month = (quarter - 1) * 3 + 1
        return date(year, month, 1)

    if s.isdigit() and len(s) == 4:
        try:
            return date(int(s), 1, 1)
        except ValueError:
            return None

    if len(s) == 7 and s[4] == "-":
        try:
            year = int(s[:4])
            month = int(s[5:7])
        except ValueError:
            return None
        if month < 1 or month > 12:
            return None
        return date(year, month, 1)

    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def normalize_fx_symbol(symbol: str) -> str:
    """Normalize an FX symbol to BoC Valet's ``FX{BASE}{QUOTE}`` shape."""
    if not isinstance(symbol, str):  # pragma: no cover - defensive
        raise TypeError(f"symbol must be str, got {type(symbol).__name__}")
    cleaned = (
        symbol.upper()
        .replace("/", "")
        .replace("-", "")
        .replace(" ", "")
        .replace("_", "")
    )
    if not cleaned.startswith("FX") and len(cleaned) == 6:
        cleaned = "FX" + cleaned
    if not cleaned.startswith("FX") or len(cleaned) != 8:
        raise ValueError(
            f"FX symbol must look like 'USDCAD' or 'FXUSDCAD'; got {symbol!r}."
        )
    return cleaned
