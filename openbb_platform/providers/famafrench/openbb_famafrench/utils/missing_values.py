"""Fama-French missing-value handling."""

from math import isnan
from numbers import Real
from typing import Any

MISSING_VALUE_MARKERS = (-99.99, -999.0)


def is_missing_value(value: Any) -> bool:
    """Check for None, NaN, or a Fama-French missing-value marker."""
    if value is None:
        return True
    if isinstance(value, str):
        if not value.lstrip().startswith("-9"):
            return False
        try:
            value = float(value)
        except ValueError:
            return False
    if isinstance(value, bool) or not isinstance(value, Real):
        return False
    return isnan(value) or value in MISSING_VALUE_MARKERS


def replace_missing_values(
    records: list[dict[str, Any]], integer_fields: tuple[str, ...] = ()
) -> list[dict[str, Any]]:
    """Replace Fama-French missing-value markers with None."""
    cleaned: list[dict[str, Any]] = []
    for record in records:
        row: dict[str, Any] = {}
        for key, value in record.items():
            if is_missing_value(value):
                row[key] = None
            elif key in integer_fields:
                row[key] = int(float(value))
            else:
                row[key] = value
        cleaned.append(row)
    return cleaned
