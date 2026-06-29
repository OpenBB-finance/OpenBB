"""Runtime helpers shared by the BoC and StatsCan fetchers.

These functions are intentionally small and pure — no I/O — so they
can be unit-tested without VCR cassettes.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any


def safe_float(value: Any) -> float | None:
    """Coerce *value* to ``float``; return ``None`` on failure or empty.

    Both BoC and StatsCan encode missing observations as the empty
    string or the string ``".."`` (StatsCan convention). Normalize
    those to ``None`` so downstream pydantic models can apply their
    own optional semantics.
    """
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

    BoC Valet emits ``"2024-01-15"`` (ISO 8601 date) for daily series
    and ``"2024-01"`` for monthly series. StatsCan SDMX emits
    ``"2024-01"`` (monthly), ``"2024-Q1"`` (quarterly), or
    ``"2024"`` (annual). All four shapes are parsed here.
    """
    if not value or not isinstance(value, str):
        return None
    s = value.strip()
    if not s:
        return None

    # Quarterly: "2024-Q1"
    if "-Q" in s:
        year_str, q_str = s.split("-Q", 1)
        try:
            year = int(year_str)
            quarter = int(q_str)
        except ValueError:
            return None
        if quarter < 1 or quarter > 4:
            return None
        # First day of the quarter
        month = (quarter - 1) * 3 + 1
        return date(year, month, 1)

    # Annual: "2024"
    if s.isdigit() and len(s) == 4:
        return date(int(s), 1, 1)

    # Monthly: "2024-01"
    if len(s) == 7 and s[4] == "-":
        try:
            year = int(s[:4])
            month = int(s[5:7])
        except ValueError:
            return None
        if month < 1 or month > 12:
            return None
        return date(year, month, 1)

    # Daily ISO: "2024-01-15"
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def normalize_fx_symbol(symbol: str) -> str:
    """Normalize an FX symbol to BoC Valet's ``FX{BASE}{QUOTE}`` shape.

    BoC series names are uppercase concatenations like ``FXUSDCAD``.
    Accept ``USD/CAD``, ``USD-CAD``, ``usdcad``, ``usd cad`` etc.
    """
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
