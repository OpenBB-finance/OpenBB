"""CDS index print extraction from DTCC PPD slice records."""

from collections.abc import Iterable
from datetime import date as dateType


def tenor_at_execution(maturity: dateType, executed: dateType) -> str | None:
    """Snap the years from execution to maturity onto a standard CDS index tenor."""
    from openbb_cftc.utils.constants import (
        CDS_STANDARD_TENORS,
        CDS_TENOR_TOLERANCE_YEARS,
        DAYS_PER_YEAR,
    )

    years = (maturity - executed).days / DAYS_PER_YEAR

    if years <= 0:
        return None

    nearest = min(CDS_STANDARD_TENORS, key=lambda tenor: abs(years - tenor))

    if abs(years - nearest) <= CDS_TENOR_TOLERANCE_YEARS:
        return f"{nearest:g}Y"

    return f"{max(round(years), 1)}Y"


def is_index_print(record: dict) -> bool:
    """Return whether a credits record is a CDS index print."""
    from openbb_cftc.utils.constants import CDS_INDEX_FISNS

    return (record.get("UPI FISN") or "").strip() in CDS_INDEX_FISNS


def curate_print(record: dict, dissemination_date: dateType) -> dict | None:
    """Add a print's dissemination date and tenor, or None when it cannot be dated."""
    from openbb_cftc.utils.curve import parse_date

    maturity = parse_date(record.get("Expiration Date"))
    executed = parse_date(record.get("Execution Timestamp"))

    if maturity is None or executed is None:
        return None

    row = dict(record)
    row["dissemination_date"] = dissemination_date
    row["tenor"] = tenor_at_execution(maturity, executed)

    return row


def extract_prints(
    records: Iterable[dict],
    dissemination_date: dateType,
    index: str | None = None,
    tenor: str | None = None,
    min_notional: float | None = None,
    limit: int | None = None,
) -> list[dict]:
    """Select the CDS index prints matching a query and curate each into a row."""
    from openbb_cftc.utils.curve import parse_notional

    rows: list[dict] = []

    for record in records:
        if not is_index_print(record):
            continue

        if (
            index
            and (record.get("UPI Underlier Name") or "").strip().upper()
            != index.strip().upper()
        ):
            continue

        row = curate_print(record, dissemination_date)

        if row is None:
            continue

        if tenor and (row["tenor"] or "").upper() != tenor.strip().upper():
            continue

        if min_notional is not None:
            notional, _ = parse_notional(record.get("Notional amount-Leg 1"))

            if notional is None or notional < min_notional:
                continue

        rows.append(row)

        if limit and len(rows) >= limit:
            break

    return rows
