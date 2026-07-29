"""CME Group Helpers."""

import asyncio
from datetime import date, datetime, timedelta

from openbb_cme.utils.client import CMEHttpClient, CMERequestError

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
    """Parse decimal or exchange-style fractional CME price fields."""
    if v is None:
        return None
    v = str(v).strip().replace(",", "").strip("ABCDE")
    if v in ("", "-", "0-", "UNCH"):
        return None
    if "'" in v:
        sign = -1 if v.startswith("-") else 1
        value = v.lstrip("+-")
        whole_text, fraction_text = value.split("'", maxsplit=1)
        if not fraction_text.isdigit():
            return None
        whole = float(whole_text) if whole_text else 0.0
        if len(fraction_text) == 1:
            fraction = int(fraction_text) / 8
        elif len(fraction_text) == 2:
            fraction = int(fraction_text) / 32
        else:
            fraction = int(fraction_text[:2]) / 32
            fraction += int(fraction_text[2:]) / 256
        return sign * (whole + fraction)
    try:
        return float(v.replace("+", ""))
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


async def _get_json(
    url: str,
    client: CMEHttpClient | None = None,
) -> dict | list:
    """
    Fetch JSON from a CME URL using curl-cffi to impersonate Chrome's TLS fingerprint,
    bypassing Akamai Bot Manager which blocks standard aiohttp/Python SSL fingerprints.
    """
    if client is not None:
        return await client.get_json(url)
    async with CMEHttpClient() as owned_client:
        return await owned_client.get_json(url)


async def fetch_settlements(
    symbol: str,
    trade_date: date,
    product_id: int | None = None,
    client: CMEHttpClient | None = None,
) -> list[dict]:
    """
    Fetch CME daily settlement data for a given symbol and trade date.

    Returns a list of dicts, one per active contract month.
    """
    # Imported locally to keep the HTTP primitive available to the catalog module.
    from openbb_cme.utils.catalog import resolve_product

    if product_id is None:
        product = await resolve_product(symbol, "Futures", client=client)
        if not product:
            return []
        product_id = product["product_id"]
    formatted = trade_date.strftime("%m/%d/%Y")
    url = (
        f"{BASE_URL}/CmeWS/mvc/Settlements/Futures/Settlements"
        f"/{product_id}/FUT?strategy=DEFAULT&tradeDate={formatted}"
    )
    response = await _get_json(url, client)

    if isinstance(response, dict):
        rows = response.get("settlements")
    elif isinstance(response, list):
        rows = response
    else:
        rows = None
    if not isinstance(rows, list):
        raise CMERequestError(
            f"CME returned an invalid futures settlement payload: {url}",
            url=url,
        )

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
    product_id: int | None = None,
    client: CMEHttpClient | None = None,
) -> tuple[date, list[dict]]:
    """Fetch the latest available settlements within a bounded lookback window."""
    trade_date = last_business_day(as_of)
    for _ in range(lookback_business_days):
        rows = await fetch_settlements(symbol, trade_date, product_id, client)
        if rows:
            return trade_date, rows
        trade_date = last_business_day(trade_date - timedelta(days=1))
    return trade_date, []


async def fetch_product_calendar(
    product_id: int,
    product_type: str = "Futures",
    client: CMEHttpClient | None = None,
) -> list[dict]:
    """Fetch the official listed-contract calendar for a CME product."""
    calendar_type = "Options" if product_type == "Options" else "Future"
    url = f"{BASE_URL}/CmeWS/mvc/ProductCalendar/{calendar_type}/{product_id}"
    response = await _get_json(url, client)
    if not isinstance(response, list):
        raise CMERequestError(
            f"CME returned an invalid product calendar payload: {url}",
            url=url,
        )

    if calendar_type == "Options":
        if any(
            not isinstance(group, dict)
            or not isinstance(group.get("calendarEntries"), list)
            for group in response
        ):
            raise CMERequestError(
                f"CME returned an invalid options calendar payload: {url}",
                url=url,
            )
        entries = [
            {
                **entry,
                "product_id": group.get("productId"),
                "option_type": group.get("optionType"),
                "option_name": group.get("name"),
                "weekly": group.get("weekly", False),
                "daily": group.get("daily", False),
            }
            for group in response
            if isinstance(group, dict)
            for entry in group.get("calendarEntries", [])
            if isinstance(entry, dict)
        ]
    else:
        entries = [row for row in response if isinstance(row, dict)]

    results: list[dict] = []
    for row in entries:
        expiration = None
        for key in ("lastTrade", "settlement"):
            value = row.get(key)
            if value and value != "-":
                try:
                    expiration = datetime.strptime(value, "%d %b %Y")
                    break
                except ValueError:
                    continue
        results.append(
            {
                "symbol": row.get("productCode"),
                "description": row.get("option_name") or row.get("contractMonth"),
                "contract_month": row.get("contractMonth"),
                "first_trade_date": row.get("firstTrade"),
                "last_trade_date": row.get("lastTrade"),
                "settlement_date": row.get("settlement"),
                "expiration": expiration,
                "is_active": True,
                "option_type": row.get("option_type"),
                "weekly": row.get("weekly"),
                "daily": row.get("daily"),
                "product_id": row.get("product_id", product_id),
            }
        )
    return results


async def fetch_option_expirations(
    product_id: int,
    client: CMEHttpClient | None = None,
) -> list[dict]:
    """Fetch the available option expirations and their recent trade dates."""
    url = (
        f"{BASE_URL}/CmeWS/mvc/Settlements/Options/TradeDateAndExpirations/{product_id}"
    )
    response, calendar = await asyncio.gather(
        _get_json(url, client),
        fetch_product_calendar(product_id, "Options", client),
    )
    if not isinstance(response, list):
        raise CMERequestError(
            f"CME returned an invalid option expiration payload: {url}",
            url=url,
        )

    calendar_by_contract = {
        row.get("symbol"): row
        for row in calendar
        if row.get("symbol") and row.get("expiration")
    }
    results: list[dict] = []
    for group in response:
        if not isinstance(group, dict) or not isinstance(
            group.get("expirations"), list
        ):
            raise CMERequestError(
                f"CME returned an invalid option expiration group: {url}",
                url=url,
            )
        for expiration in group["expirations"]:
            if not isinstance(expiration, dict):
                raise CMERequestError(
                    f"CME returned an invalid option expiration: {url}",
                    url=url,
                )
            key = expiration.get("expiration")
            if not isinstance(key, dict):
                raise CMERequestError(
                    f"CME returned invalid option expiration metadata: {url}",
                    url=url,
                )
            contract_id = expiration.get("contractId")
            calendar_row = calendar_by_contract.get(contract_id, {})
            calendar_expiration = calendar_row.get("expiration")
            results.append(
                {
                    "product_id": int(expiration.get("productId", product_id)),
                    "option_type": group.get("optionType"),
                    "name": group.get("name"),
                    "label": expiration.get("label"),
                    "month_year": key.get("twoDigitsCode"),
                    "contract_id": contract_id,
                    "expiration_date": (
                        calendar_expiration.date()
                        if isinstance(calendar_expiration, datetime)
                        else None
                    ),
                    "trade_dates": [
                        row.get("formatedDate")
                        for row in expiration.get("tradeDates", [])
                        if row.get("formatedDate")
                    ],
                }
            )
    return results


async def fetch_option_settlements(
    product_id: int,
    month_year: str,
    contract_id: str,
    trade_date: date,
    client: CMEHttpClient | None = None,
) -> list[dict]:
    """Fetch strike-level call and put settlements for one option expiration."""
    formatted = trade_date.strftime("%m/%d/%Y")
    url = (
        f"{BASE_URL}/CmeWS/mvc/Settlements/Options/Settlements/{product_id}/OOF"
        f"?strategy=DEFAULT&optionProductId={product_id}"
        f"&monthYear={month_year}&optionExpiration={contract_id}"
        f"&tradeDate={formatted}&pageSize=500"
    )
    response = await _get_json(url, client)
    settlements = response.get("settlements") if isinstance(response, dict) else None
    if not isinstance(settlements, list):
        raise CMERequestError(
            f"CME returned an invalid option settlement payload: {url}",
            url=url,
        )
    return [
        row
        for row in settlements
        if isinstance(row, dict) and row.get("strike") != "Total"
    ]
