"""FiscalData API client."""

from datetime import date as dateType
from typing import Any

BASE_URL = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/"
MAX_PAGE_SIZE = 10000
MAX_RETRIES = 3


def default_start_date(
    start: dateType | None, end: dateType | None, lookback_days: int
) -> dateType:
    """Return the effective start date, defaulting to a trailing window.

    Parameters
    ----------
    start : date | None
        Requested start date; returned as-is when provided.
    end : date | None
        Requested end date, used as the window anchor; today when None.
    lookback_days : int
        Length of the trailing window applied when start is None, so the
        default query is bounded instead of returning the full history.

    Returns
    -------
    date
        The requested start date, or the anchor minus the trailing window.
    """
    from datetime import timedelta

    if start is not None:
        return start
    anchor = end or dateType.today()
    return anchor - timedelta(days=lookback_days)


def build_filters(conditions: list[tuple[str, str, Any]]) -> str | None:
    """Build a FiscalData filter string from (field, operator, value) conditions.

    Parameters
    ----------
    conditions : list[tuple[str, str, Any]]
        Conditions as (field, operator, value); entries with a None value are
        skipped. Operators are eq, lt, lte, gt, gte, or in.

    Returns
    -------
    str | None
        The comma-joined filter string, or None when no condition applies.
    """
    parts = [
        f"{field}:{operator}:{value}"
        for field, operator, value in conditions
        if value is not None
    ]
    return ",".join(parts) if parts else None


async def get_fiscal_data(
    endpoint: str,
    filters: str | None = None,
    sort: str | None = None,
    page_size: int = MAX_PAGE_SIZE,
    **kwargs: Any,
) -> list[dict]:
    """Fetch every page of a FiscalData API table.

    Parameters
    ----------
    endpoint : str
        Table path under the fiscal_service base, e.g.
        'v2/accounting/od/debt_to_penny'.
    filters : str | None
        FiscalData filter string, e.g. 'record_date:gte:2024-01-01'.
    sort : str | None
        Sort key, e.g. 'record_date' or '-record_date'.
    page_size : int
        Rows per page, capped by the API at 10000.

    Returns
    -------
    list[dict]
        All rows across pages, with the literal string 'null' and empty or
        whitespace-only strings mapped to None.

    Raises
    ------
    EmptyDataError
        If the query returns no rows.
    OpenBBError
        If the API responds with an error payload or an invalid body.
    """
    import asyncio

    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.errors import EmptyDataError
    from openbb_core.provider.utils.helpers import amake_request

    params = [f"page[size]={page_size}"]
    if filters:
        params.append(f"filter={filters}")
    if sort:
        params.append(f"sort={sort}")
    base = f"{BASE_URL}{endpoint}?{'&'.join(params)}"

    async def fetch_page(page_number: int) -> dict:
        url = f"{base}&page[number]={page_number}"
        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                response = await amake_request(url, **kwargs)
            except Exception as e:  # noqa: BLE001
                last_error = e
                await asyncio.sleep(2**attempt)
                continue
            if isinstance(response, dict) and "data" in response:
                return response
            if isinstance(response, dict) and "error" in response:
                raise OpenBBError(
                    f"FiscalData API error -> {response.get('error')}:"
                    f" {response.get('message')}"
                )
            last_error = OpenBBError(f"Unexpected FiscalData response -> {response}")
            await asyncio.sleep(2**attempt)
        raise OpenBBError(
            f"FiscalData request failed after {MAX_RETRIES} attempts -> {url}"
        ) from last_error

    first_page = await fetch_page(1)
    rows: list[dict] = list(first_page.get("data", []))
    total_pages = int(first_page.get("meta", {}).get("total-pages", 1) or 1)

    for page_number in range(2, total_pages + 1):
        page = await fetch_page(page_number)
        rows.extend(page.get("data", []))

    if not rows:
        raise EmptyDataError("The request was returned empty.")

    def clean(value: Any) -> Any:
        """Map the literal 'null' and empty or whitespace-only strings to None."""
        if isinstance(value, str) and (value == "null" or not value.strip()):
            return None
        return value

    return [{key: clean(value) for key, value in row.items()} for row in rows]
