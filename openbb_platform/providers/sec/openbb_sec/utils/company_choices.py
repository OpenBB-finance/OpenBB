"""Company-choice options for SEC Workspace widgets, sourced from DoltHub."""

from openbb_core.app.model.abstract.error import OpenBBError

_DOLT_URL = "https://www.dolthub.com/api/v1alpha1/deeleeramone/sec-company-facts/main"

_PAGE_SIZE = 1000

_CACHE_KEY = "sec_company_choices"

_COMPANIES_SQL = """
SELECT
    pt.ticker AS ticker,
    COALESCE(NULLIF(TRIM(pt.name), ''), c.entity_name, pt.ticker) AS name,
    pt.cik AS cik,
    MIN(t.`rank`) AS `rank`
FROM primary_tickers pt
JOIN tickers t ON t.cik = pt.cik AND t.ticker = pt.ticker
LEFT JOIN companies c ON c.cik = pt.cik
JOIN processed_ciks p ON p.cik = pt.cik
WHERE t.is_primary = 1
  AND p.has_balance
  AND p.has_income
  AND p.has_cash_flow
GROUP BY pt.ticker, pt.cik, pt.name, c.entity_name
ORDER BY `rank` ASC, ticker ASC
"""


async def get_company_choices(use_cache: bool = True) -> list[dict]:
    """Return symbol-dropdown choices for every company with standardized financials."""
    from urllib.parse import quote

    from openbb_sec.utils.cache import aget_cached, aset_cached, cached_request

    if use_cache:
        cached = await aget_cached(_CACHE_KEY)
        if cached is not None:
            return cached

    base = " ".join(_COMPANIES_SQL.split())
    rows: list = []
    offset = 0
    while True:
        url = f"{_DOLT_URL}?q={quote(f'{base} LIMIT {_PAGE_SIZE} OFFSET {offset}')}"
        response = await cached_request(
            url, use_cache=use_cache, expire=86400, timeout=180
        )
        if (
            isinstance(response, dict)
            and response.get("query_execution_status") == "Error"
        ):
            raise OpenBBError(
                response.get("query_execution_message") or "Dolt query failed."
            )
        page = response.get("rows", []) if isinstance(response, dict) else []
        rows.extend(page)
        if len(page) < _PAGE_SIZE:
            break
        offset += _PAGE_SIZE

    by_ticker: dict[str, dict] = {}
    for row in rows:
        ticker = str(row.get("ticker") or "").strip().upper()
        if not ticker:
            continue
        if ticker not in by_ticker:
            by_ticker[ticker] = row
            continue
        prev_rank = by_ticker[ticker].get("rank")
        curr_rank = row.get("rank")
        try:
            prev_val = float(prev_rank) if prev_rank is not None else float("inf")
        except (TypeError, ValueError):
            prev_val = float("inf")
        try:
            curr_val = float(curr_rank) if curr_rank is not None else float("inf")
        except (TypeError, ValueError):
            curr_val = float("inf")
        if curr_val < prev_val:
            by_ticker[ticker] = row

    choices = []
    for ticker, row in by_ticker.items():
        label = row.get("name") or ticker
        cik = row.get("cik") or ""
        choices.append(
            {
                "label": label,
                "value": ticker,
                "extraInfo": {
                    "description": f"{ticker} | {cik}",
                    "rightOfDescription": row.get("sic_name") or "",
                },
            }
        )

    if use_cache and choices:
        await aset_cached(_CACHE_KEY, choices, expire=86400)
    return choices
