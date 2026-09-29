"""CIRO Debt Information Processor access."""

from typing import Any

BASE_URL = "https://bondtradedata.ciro.ca"

ENDPOINTS = {
    "securities": "/debtip/securities/list",
    "issuers": "/debtip/issuers/list",
    "designated_bonds": "/debtip/designatedbonds/list",
    "query_issuer": "/debtip/query/issuer/{issuerName}",
    "query_security": "/debtip/query/security/{securityId}",
    "transactions": "/debtip/query/transaction/list",
}

MAX_WINDOW_DAYS = 90

ACCOUNT_TYPES = {"all": "all", "retail": "retail", "institutional": "institutional"}

ACCOUNT_TYPE_LABELS = {"R": "retail", "I": "institutional"}


async def _post_json(path: str, payload: dict) -> Any:
    """Post JSON to a CIRO endpoint through an impersonating session."""
    import asyncio
    import json

    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_tmx.utils.curl_session import request_with_retry

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Referer": f"{BASE_URL}/",
    }

    def _request():
        response = request_with_retry(
            "ciro",
            "POST",
            BASE_URL + path,
            headers=headers,
            data=json.dumps(payload),
            timeout=300,
        )

        if response.status_code != 200:
            raise OpenBBError(
                f"CIRO request failed with status {response.status_code}."
            )

        return response.json() if response.content else {}

    return await asyncio.to_thread(_request)


async def get_issuers() -> list[str]:
    """Get every issuer CIRO publishes debt trade data for.

    Returns
    -------
    list[str]
        The issuer names.
    """
    from openbb_tmx.utils.curl_session import get_json

    return await get_json("ciro", BASE_URL + ENDPOINTS["issuers"])


async def get_security_ids() -> list[str]:
    """Get every security identifier CIRO publishes debt trade data for.

    Returns
    -------
    list[str]
        The security identifiers, as CUSIPs.
    """
    from openbb_tmx.utils.curl_session import get_json

    return await get_json("ciro", BASE_URL + ENDPOINTS["securities"])


def _windows(start, end) -> list[tuple]:
    """Split a date range into windows the API will accept.

    Parameters
    ----------
    start : date
        The first date to cover.
    end : date
        The last date to cover.

    Returns
    -------
    list[tuple]
        Consecutive (from, to) pairs, none longer than the API limit.
    """
    from datetime import timedelta

    spans: list[tuple] = []
    cursor = start

    while cursor <= end:
        stop = min(cursor + timedelta(days=MAX_WINDOW_DAYS - 1), end)
        spans.append((cursor, stop))
        cursor = stop + timedelta(days=1)

    return spans


async def get_bond_trades(
    sec_key: str,
    start_date,
    end_date,
    account_type: str = "all",
    concurrency: int = 4,
) -> list[dict]:
    """Get every reported trade for one bond across a date range.

    Parameters
    ----------
    sec_key : str
        The CIRO security key.
    start_date : date
        The first date to cover.
    end_date : date
        The last date to cover.
    account_type : str
        One of 'all', 'retail', or 'institutional'.
    concurrency : int
        How many windows to request at once.

    Returns
    -------
    list[dict]
        Every trade in the range, oldest first.
    """
    import asyncio

    semaphore = asyncio.Semaphore(concurrency)
    results: list[dict] = []

    async def fetch(window) -> None:
        async with semaphore:
            payload = {
                "secKey": str(sec_key),
                "acctType": ACCOUNT_TYPES.get(account_type, "all"),
                "from": window[0].strftime("%Y-%m-%d"),
                "to": window[1].strftime("%Y-%m-%d"),
            }
            response = await _post_json(ENDPOINTS["transactions"], payload)

            if isinstance(response, dict) and response.get("txnData"):
                results.extend(response["txnData"])

    await asyncio.gather(*(fetch(w) for w in _windows(start_date, end_date)))

    return sorted(
        results,
        key=lambda t: (t.get("execDate") or "", t.get("execTime") or ""),
    )
