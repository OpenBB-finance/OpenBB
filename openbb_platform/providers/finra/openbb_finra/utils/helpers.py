"""Value parsing helpers for the FINRA data services."""

from datetime import date, datetime
from functools import lru_cache
from typing import Any


def clean(value: Any) -> str | None:
    """Return a stripped string, or None for a blank or not-available value.

    Parameters
    ----------
    value : Any
        The raw value.

    Returns
    -------
    str | None
        The stripped text, or None.
    """
    from openbb_finra.utils.constants import NA_TOKENS

    if value is None:
        return None

    text = str(value).strip()

    return None if text.upper() in NA_TOKENS else text


def to_float(value: Any) -> float | None:
    """Return the value as a float, or None when it is not a number.

    Parameters
    ----------
    value : Any
        The raw value.

    Returns
    -------
    float | None
        The parsed number, or None.
    """
    if value is None or isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    text = clean(value)

    if text is None:
        return None

    try:
        return float(text.replace(",", ""))
    except ValueError:
        return None


def to_bool(value: Any) -> bool | None:
    """Return the value as a bool, or None when it is not a recognised flag.

    Parameters
    ----------
    value : Any
        The raw value.

    Returns
    -------
    bool | None
        The parsed flag, or None.
    """
    if isinstance(value, bool):
        return value

    text = clean(value)

    if text is None:
        return None

    upper = text.upper()

    if upper in {"Y", "YES", "TRUE", "T", "1"}:
        return True

    if upper in {"N", "NO", "FALSE", "F", "0"}:
        return False

    return None


def to_date(value: Any) -> str | None:
    """Return the value as an ISO date string, or None when it is not a date.

    Parameters
    ----------
    value : Any
        A date, or text as YYYY-MM-DD, YYYYMMDD, or MM/DD/YYYY.

    Returns
    -------
    str | None
        The date as YYYY-MM-DD, or None.
    """
    import re

    if isinstance(value, (datetime, date)):
        return (value.date() if isinstance(value, datetime) else value).isoformat()

    text = clean(value) or ""

    if len(text) >= 10 and text[4] == "-" and text[7] == "-":
        return text[:10]

    if len(text) == 8 and text.isdigit():
        return f"{text[:4]}-{text[4:6]}-{text[6:]}"

    match = re.match(r"^(\d{2})[-/](\d{2})[-/](\d{4})(?:\s.*)?$", text)

    return f"{match[3]}-{match[1]}-{match[2]}" if match else None


def first(*values: Any) -> Any:
    """Return the first value that is not blank.

    Parameters
    ----------
    *values : Any
        The candidate values, in order of preference.

    Returns
    -------
    Any
        The first value that is not None or a not-available token.
    """
    for value in values:
        if clean(value) is not None:
            return value

    return None


def decode(table: dict[str, str], value: Any) -> str | None:
    """Return the description of a code, or the code when it has none.

    Parameters
    ----------
    table : dict[str, str]
        The descriptions, keyed by upper-case code.
    value : Any
        The raw code.

    Returns
    -------
    str | None
        The description, the code itself when it is not in the table, or None.
    """
    text = clean(value)

    return None if text is None else table.get(text.upper(), text)


@lru_cache(maxsize=1)
def market_names() -> dict[str, str]:
    """Return the Market Data Center's names for its exchange ids.

    Returns
    -------
    dict[str, str]
        The exchange names keyed by exchange id.
    """
    import json
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "assets" / "market_data_exchanges.json"

    return json.loads(path.read_text(encoding="utf-8"))


def split_symbols(value: str) -> list[str]:
    """Return the distinct, upper-cased symbols of a comma-separated string.

    Parameters
    ----------
    value : str
        One symbol, or several separated by commas.

    Returns
    -------
    list[str]
        The symbols, in the order given.
    """
    symbols = [part.strip().upper() for part in value.split(",")]

    return list(dict.fromkeys(symbol for symbol in symbols if symbol))


def drop_none(record: dict) -> dict:
    """Return the record without the keys whose value is None.

    Parameters
    ----------
    record : dict
        The record.

    Returns
    -------
    dict
        The record with only the populated keys.
    """
    return {key: value for key, value in record.items() if value is not None}


def normalize_trace_record(record: dict, bond_type: str | None = None) -> dict:
    """Return a TRACE record with typed values and decoded codes.

    Parameters
    ----------
    record : dict
        The raw record, keyed by the camelCase TRACE field names.
    bond_type : str | None
        The bond type the record came from, used to decode the coupon type.

    Returns
    -------
    dict
        The record keyed by the same field names, with parsed values.
    """
    from openbb_finra.utils.constants import (
        AMORTIZATION_TYPES,
        COUPON_TYPES,
        INDUSTRY_GROUPS,
        INTEREST_TYPES,
        MONTHS,
        MORTGAGE_PRODUCTS,
        PRICE_TYPES,
        PRODUCT_SUB_TYPES,
        PRODUCT_TYPES,
        SUB_PRODUCT_TYPES,
        TRACE_BOOL_FIELDS,
        TRACE_DATE_FIELDS,
        TRACE_GRADES,
        TRACE_NUMBER_FIELDS,
    )

    decodes: dict[str, dict[str, str]] = {
        "couponType": COUPON_TYPES.get(bond_type or "", {}),
        "industryGroup": INDUSTRY_GROUPS,
        "traceGradeCode": TRACE_GRADES,
        "productSubTypeCode": PRODUCT_SUB_TYPES,
        "subProductType": SUB_PRODUCT_TYPES,
        "interestType": INTEREST_TYPES,
        "mortgageProduct": MORTGAGE_PRODUCTS,
        "amortizationType": AMORTIZATION_TYPES,
        "settlementDateMonth": MONTHS,
        "priceType": PRICE_TYPES,
        "productType": PRODUCT_TYPES,
    }
    output: dict = {}

    for field, value in record.items():
        if field in TRACE_NUMBER_FIELDS:
            output[field] = to_float(value)
        elif field == "isPerpetual" and isinstance(value, str):
            flag = value.strip().upper()
            output[field] = (
                flag in {"PERPETUAL", "Y"}
                if flag in {"PERPETUAL", "NOT PERPETUAL", "Y", "N"}
                else None
            )
        elif field in TRACE_BOOL_FIELDS:
            output[field] = to_bool(value)
        elif field in TRACE_DATE_FIELDS:
            output[field] = to_date(value)
        else:
            text = clean(value)
            output[field] = (
                decodes[field].get(text.upper(), text)
                if text is not None and field in decodes
                else text
            )

    return drop_none(output)
