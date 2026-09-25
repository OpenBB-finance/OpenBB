"""FX forward and swap trade extraction from DTCC PPD forex slice records."""

from collections.abc import Iterable
from datetime import date as dateType

from openbb_cftc.utils.fx_options import _package_id, _split_currencies

_FORWARD_PRODUCTS = {
    "NA/Fwd": "Forward",
    "NA/Fwd NDF": "Non-Deliverable Forward",
    "NA/Swaps": "FX Swap",
    "NA/Swaps NDS": "Non-Deliverable Swap",
    "NA/FX Fwd Nstd": "Non-Standard Forward",
}


def forward_product(fisn: str) -> str | None:
    """Readable product from the FISN prefix, or None when it is not a plain forward or swap."""
    parts = fisn.split()

    if len(parts) < 3:
        return None

    return _FORWARD_PRODUCTS.get(" ".join(parts[:-2]))


def curate_forward(record: dict, dissemination_date: dateType) -> dict | None:
    """Add a print's dissemination date, pair, product, tenor and package key, or None."""
    from openbb_cftc.utils.curve import parse_date

    executed = parse_date(record.get("Execution Timestamp"))
    expiry = parse_date(record.get("Expiration Date"))
    legs = (record.get("UPI Underlier Name") or "").strip().split()

    if executed is None or expiry is None or len(legs) != 2:
        return None

    row = dict(record)
    row["dissemination_date"] = dissemination_date
    row["pair"] = f"{legs[0]}/{legs[1]}"
    row["product_type"] = forward_product((record.get("UPI FISN") or "").strip())
    row["days_to_expiry"] = (expiry - executed).days
    row["package_id"] = _package_id(record)

    return row


def extract_forward_trades(
    records: Iterable[dict],
    dissemination_date: dateType,
    *,
    pair: str | None = None,
    action_type: str | None = None,
    product: str | None = None,
    settled: str | None = None,
    min_notional: float | None = None,
    ticker: str | None = None,
    limit: int | None = None,
) -> list[dict]:
    """Select the FX forward and swap prints matching a query, newest reported event first."""
    from openbb_cftc.utils.curve import parse_notional

    wanted = _split_currencies(pair) if pair else set()
    settle = settled.strip().upper() if settled else None
    upi = ticker.strip().upper() if ticker else None
    rows: list[dict] = []

    for record in records:
        product_type = forward_product((record.get("UPI FISN") or "").strip())

        if product_type is None:
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

        if product and product_type.upper() != product.strip().upper():
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

        row = curate_forward(record, dissemination_date)

        if row is not None:
            rows.append(row)

    rows.sort(
        key=lambda r: r.get("Event timestamp") or r.get("Execution Timestamp") or "",
        reverse=True,
    )

    return rows[:limit] if limit else rows
