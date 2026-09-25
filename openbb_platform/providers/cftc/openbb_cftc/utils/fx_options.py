"""FX vanilla-option trade extraction from DTCC PPD forex slice records."""

from collections.abc import Iterable
from datetime import date as dateType

NOT_PROVIDED = frozenset({"9.9999999999"})

_OPTION_TYPES = {
    "Van": "Vanilla",
    "NDO": "Non-Deliverable",
    "Dig": "Digital",
    "Bar": "Barrier",
    "DigBar": "Digital Barrier",
    "Targ": "Target",
}


def option_type(fisn: str) -> str | None:
    """Readable option family from the FISN token."""
    parts = fisn.split()

    if len(parts) < 2 or parts[0] != "NA/O":
        return None

    return _OPTION_TYPES.get(parts[1], parts[1])


def _split_currencies(pair: str) -> set[str]:
    """Split a pair filter into ISO currency codes."""
    cleaned = (pair or "").upper().replace("/", "").replace(" ", "").replace(",", "")

    return {cleaned[i : i + 3] for i in range(0, len(cleaned), 3)}


def _package_id(record: dict) -> str | None:
    """Group a package's legs: they execute atomically at one price or spread."""
    if (record.get("Package indicator") or "").strip().upper() != "TRUE":
        return None

    executed = (record.get("Execution Timestamp") or "").strip()
    price = (record.get("Package transaction price") or "").strip()

    if price in NOT_PROVIDED:
        price = ""

    level = price or (record.get("Package transaction spread") or "").strip()

    return f"{executed}|{level}" if executed else None


def curate_option(record: dict, dissemination_date: dateType) -> dict | None:
    """Add a print's dissemination date, pair, tenor and package key, or None if undatable."""
    from openbb_cftc.utils.curve import parse_date

    executed = parse_date(record.get("Execution Timestamp"))
    expiry = parse_date(record.get("Expiration Date"))
    legs = (record.get("UPI Underlier Name") or "").strip().split()

    if executed is None or expiry is None or len(legs) != 2:
        return None

    row = dict(record)
    row["dissemination_date"] = dissemination_date
    row["pair"] = f"{legs[0]}/{legs[1]}"
    row["option_type"] = option_type((record.get("UPI FISN") or "").strip())
    row["days_to_expiry"] = (expiry - executed).days
    row["package_id"] = _package_id(record)

    return row


def extract_option_trades(
    records: Iterable[dict],
    dissemination_date: dateType,
    *,
    pair: str | None = None,
    action_type: str | None = None,
    option_kind: str | None = None,
    settled: str | None = None,
    min_notional: float | None = None,
    ticker: str | None = None,
    limit: int | None = None,
) -> list[dict]:
    """Select the FX option prints matching a query, newest reported event first."""
    from openbb_cftc.utils.curve import parse_notional

    wanted = _split_currencies(pair) if pair else set()
    settle = settled.strip().upper() if settled else None
    upi = ticker.strip().upper() if ticker else None
    rows: list[dict] = []

    for record in records:
        fisn = (record.get("UPI FISN") or "").strip()

        if not fisn.startswith("NA/O "):
            continue

        if (
            upi
            and (record.get("Unique Product Identifier") or "").strip().upper() != upi
        ):
            continue

        if (
            action_type
            and (record.get("Action type") or "").strip().upper()
            != action_type.strip().upper()
        ):
            continue

        if (
            option_kind
            and (option_type(fisn) or "").upper() != option_kind.strip().upper()
        ):
            continue

        legs = set((record.get("UPI Underlier Name") or "").strip().upper().split())

        if wanted and not wanted <= legs:
            continue

        if (
            settle
            and (record.get("Settlement currency-Leg 1") or "").strip().upper()
            != settle
        ):
            continue

        if min_notional is not None:
            first, _ = parse_notional(record.get("Notional amount-Leg 1"))
            second, _ = parse_notional(record.get("Notional amount-Leg 2"))

            if max(first or 0.0, second or 0.0) < min_notional:
                continue

        row = curate_option(record, dissemination_date)

        if row is not None:
            rows.append(row)

    rows.sort(
        key=lambda r: r.get("Event timestamp") or r.get("Execution Timestamp") or "",
        reverse=True,
    )

    return rows[:limit] if limit else rows
