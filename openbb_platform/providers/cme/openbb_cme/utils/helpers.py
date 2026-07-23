"""CME Group Helpers."""

from datetime import date, timedelta
from typing import Literal

CME_SYMBOLS = Literal["ES", "NQ", "MES", "MNQ", "YM"]

# Maps root symbol → (product_id, full_name, exchange)
CME_PRODUCT_MAP: dict[str, dict] = {
    "ES": {
        "product_id": "133",
        "name": "E-mini S&P 500",
        "exchange": "CME/Globex",
        "tick_size": 0.25,
        "point_value": 50.0,
        "multiplier": 50,
        "currency": "USD",
    },
    "NQ": {
        "product_id": "146",
        "name": "E-mini Nasdaq-100",
        "exchange": "CME/Globex",
        "tick_size": 0.25,
        "point_value": 20.0,
        "multiplier": 20,
        "currency": "USD",
    },
    "MES": {
        "product_id": "8667",
        "name": "Micro E-mini S&P 500",
        "exchange": "CME/Globex",
        "tick_size": 0.25,
        "point_value": 5.0,
        "multiplier": 5,
        "currency": "USD",
    },
    "MNQ": {
        "product_id": "8668",
        "name": "Micro E-mini Nasdaq-100",
        "exchange": "CME/Globex",
        "tick_size": 0.25,
        "point_value": 2.0,
        "multiplier": 2,
        "currency": "USD",
    },
    "YM": {
        "product_id": "318",
        "name": "E-mini Dow ($5)",
        "exchange": "CBOT/Globex",
        "tick_size": 1.0,
        "point_value": 5.0,
        "multiplier": 5,
        "currency": "USD",
    },
}

BASE_URL = "https://www.cmegroup.com"

MONTH_ABBR = {
    "Jan": "01",
    "Feb": "02",
    "Mar": "03",
    "Apr": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07",
    "Aug": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dec": "12",
}


def parse_cme_value(v: str | None) -> float | None:
    """Parse a CME settlement field that may contain commas, dashes, or B/A markers."""
    if v is None:
        return None
    v = str(v).strip().replace(",", "").replace("+", "").strip("ABCDE")
    if v in ("", "-", "0-", "UNCH"):
        return None
    try:
        return float(v)
    except ValueError:
        return None


def parse_cme_month(month_str: str) -> str | None:
    """Convert CME month string ('Jun 25' or 'SEP 26') to ISO format ('2025-06')."""
    parts = month_str.strip().split()
    if len(parts) != 2:
        return None
    abbr, year_short = parts[0].title(), parts[1]
    month_num = MONTH_ABBR.get(abbr)
    if not month_num:
        return None
    year = f"20{year_short}" if len(year_short) == 2 else year_short
    return f"{year}-{month_num}"


def last_business_day(ref: date | None = None) -> date:
    """Return the most recent settled weekday.

    Without a ref this defaults to yesterday so the returned date always has
    published CME settlement data (today's settlements are not available until
    after market close).
    """
    d = ref if ref is not None else (date.today() - timedelta(days=1))
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


def business_days_between(start: date, end: date) -> list[date]:
    """Return all weekdays in [start, end] inclusive."""
    days: list[date] = []
    current = start
    while current <= end:
        if current.weekday() < 5:
            days.append(current)
        current += timedelta(days=1)
    return days


_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.cmegroup.com/",
}


async def _get_json(url: str) -> dict | list:
    """
    Fetch JSON from a CME URL using curl-cffi to impersonate Chrome's TLS fingerprint,
    bypassing Akamai Bot Manager which blocks standard aiohttp/Python SSL fingerprints.
    """
    # pylint: disable=import-outside-toplevel
    from curl_cffi.requests import AsyncSession

    async with AsyncSession(impersonate="chrome120") as session:
        resp = await session.get(url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.json()


async def fetch_settlements(symbol: str, trade_date: date) -> list[dict]:
    """
    Fetch CME daily settlement data for a given symbol and trade date.

    Returns a list of dicts, one per active contract month.
    """
    spec = CME_PRODUCT_MAP.get(symbol.upper(), {})
    product_id = spec.get("product_id", symbol.upper())
    formatted = trade_date.strftime("%m/%d/%Y")
    url = (
        f"{BASE_URL}/CmeWS/mvc/Settlements/Futures/Settlements"
        f"/{product_id}/FUT?strategy=DEFAULT&tradeDate={formatted}"
    )
    response = await _get_json(url)

    if isinstance(response, dict):
        rows = response.get("settlements", [])
    elif isinstance(response, list):
        rows = response
    else:
        return []

    results: list[dict] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        month_str = row.get("month", "")
        expiration = parse_cme_month(month_str)
        if not expiration:
            continue
        results.append(
            {
                "date": trade_date,
                "symbol": symbol.upper(),
                "expiration": expiration,
                "open": parse_cme_value(row.get("open")),
                "high": parse_cme_value(row.get("high")),
                "low": parse_cme_value(row.get("low")),
                "close": parse_cme_value(row.get("settle")),
                "volume": parse_cme_value(row.get("volume")),
                "settlement_price": parse_cme_value(row.get("settle")),
                "open_interest": parse_cme_value(row.get("openInterest")),
            }
        )
    return results


async def fetch_latest_settlements(
    symbol: str,
    as_of: date | None = None,
    lookback_business_days: int = 5,
) -> tuple[date, list[dict]]:
    """Fetch the latest available settlements within a bounded lookback window."""
    trade_date = last_business_day(as_of)
    for _ in range(lookback_business_days):
        rows = await fetch_settlements(symbol, trade_date)
        if rows:
            return trade_date, rows
        trade_date = last_business_day(trade_date - timedelta(days=1))
    return trade_date, []


_CME_MONTH_CODES = {
    "01": "F",
    "02": "G",
    "03": "H",
    "04": "J",
    "05": "K",
    "06": "M",
    "07": "N",
    "08": "Q",
    "09": "U",
    "10": "V",
    "11": "X",
    "12": "Z",
}

_CME_MONTH_NAMES = {
    "01": "Jan",
    "02": "Feb",
    "03": "Mar",
    "04": "Apr",
    "05": "May",
    "06": "Jun",
    "07": "Jul",
    "08": "Aug",
    "09": "Sep",
    "10": "Oct",
    "11": "Nov",
    "12": "Dec",
}


def _third_friday(year: int, month: int) -> date:
    """Return the date of the 3rd Friday in the given month."""
    first = date(year, month, 1)
    first_friday = first + timedelta(days=(4 - first.weekday()) % 7)
    return first_friday + timedelta(weeks=2)


async def fetch_product_calendar(product_id: str) -> list[dict]:
    """Derive listed contract months from CME settlement data by product ID."""
    symbol = next(
        (
            sym
            for sym, spec in CME_PRODUCT_MAP.items()
            if spec["product_id"] == product_id
        ),
        None,
    )
    if not symbol:
        return []

    _, rows = await fetch_latest_settlements(symbol)
    spec = CME_PRODUCT_MAP[symbol]

    results: list[dict] = []
    for row in rows:
        expiration_iso = row.get("expiration", "")
        if not expiration_iso or "-" not in expiration_iso:
            continue
        try:
            year_s, month_s = expiration_iso.split("-")
            year, month = int(year_s), int(month_s)
            month_code = _CME_MONTH_CODES.get(month_s, "")
            year_short = year_s[2:]
            contract_symbol = f"{symbol}{month_code}{year_short}"
            month_name = _CME_MONTH_NAMES.get(month_s, "")
            exp_date = _third_friday(year, month)
            exp_iso = exp_date.isoformat() + "T00:00:00"
        except (ValueError, IndexError):
            continue
        results.append(
            {
                "symbol": contract_symbol,
                "product_code": symbol,
                "description": f"{spec['name']} {month_name} {year_s}",
                "expiration": exp_iso,
                "is_active": True,
            }
        )
    return results
