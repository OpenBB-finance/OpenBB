"""Build and execute ECB SDMX 2.1 data queries (``format=jsondata``)."""

from __future__ import annotations

from openbb_ecb.utils.metadata._constants import BASE_URL

DATA_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "OpenBB Platform - ECB",
}


def build_data_url(
    flow_ref: str,
    key: str = "",
    start_date: str | None = None,
    end_date: str | None = None,
    detail: str = "full",
    first_n: int | None = None,
    last_n: int | None = None,
    include_history: bool = False,
) -> str:
    """Construct an ECB SDMX 2.1 data-query URL returning SDMX-JSON.

    ``flow_ref`` is a dataflow id (``EXR``) or full ``AGENCY,FLOW,VERSION``.
    ``key`` is the dot-joined dimension key (``D.USD.EUR.SP00.A``); ``+``
    means OR and an empty segment is a wildcard.
    """
    params: list[str] = ["format=jsondata", f"detail={detail}"]
    if start_date:
        params.append(f"startPeriod={start_date}")
    if end_date:
        params.append(f"endPeriod={end_date}")
    if first_n:
        params.append(f"firstNObservations={int(first_n)}")
    if last_n:
        params.append(f"lastNObservations={int(last_n)}")
    if include_history:
        params.append("includeHistory=true")
    return f"{BASE_URL}/data/{flow_ref}/{key}?{'&'.join(params)}"


async def _request_sdmx(url: str, raise_empty: bool) -> dict | None:
    """GET an SDMX-JSON message; return the dict, or None on a 404 no-raise.

    Raises ``OpenBBError`` on a 404 (when ``raise_empty``) or any other error
    status. A non-dict body resolves to ``None``.
    """
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.errors import EmptyDataError
    from openbb_core.provider.utils.helpers import amake_request

    async def _response_callback(response, _):
        """Return JSON, or text/status for non-JSON (e.g. 404 'No results')."""
        if response.status == 200:
            return await response.json()
        return {"_status": response.status, "_text": await response.text()}

    message = await amake_request(
        url, headers=DATA_HEADERS, response_callback=_response_callback
    )
    if isinstance(message, dict) and "_status" in message:
        status = message["_status"]
        if status == 404 and not raise_empty:
            return None
        if status == 404:
            raise OpenBBError(
                EmptyDataError(f"No data found for the query. URL -> {url}")
            )
        raise OpenBBError(
            f"ECB request failed ({status}). URL -> {url} -> "
            f"{message.get('_text', '')[:300]}"
        )
    return message if isinstance(message, dict) else None


async def fetch_sdmx_data(
    flow_ref: str,
    key: str = "",
    start_date: str | None = None,
    end_date: str | None = None,
    detail: str = "full",
    first_n: int | None = None,
    last_n: int | None = None,
    raise_empty: bool = True,
) -> list[dict]:
    """Fetch and flatten an ECB data query into observation records."""
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.errors import EmptyDataError

    from openbb_ecb.utils.helpers import parse_sdmx_json

    url = build_data_url(
        flow_ref,
        key,
        start_date=start_date,
        end_date=end_date,
        detail=detail,
        first_n=first_n,
        last_n=last_n,
    )
    message = await _request_sdmx(url, raise_empty)
    records = parse_sdmx_json(message) if message else []
    if not records and raise_empty:
        raise OpenBBError(EmptyDataError(f"No data found for the query. URL -> {url}"))
    return records


async def fetch_series_keys(
    flow_ref: str,
    key: str = "",
    raise_empty: bool = False,
) -> list[dict]:
    """Enumerate the existing series in a dataflow (``detail=serieskeysonly``).

    Returns one record per actual series (key + decoded dimension labels), with
    no observations — the SDMX way to list every series in (a slice of) a flow.
    """
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.errors import EmptyDataError

    from openbb_ecb.utils.helpers import parse_series_keys

    url = build_data_url(flow_ref, key, detail="serieskeysonly")
    message = await _request_sdmx(url, raise_empty)
    records = parse_series_keys(message) if message else []
    if not records and raise_empty:
        raise OpenBBError(
            EmptyDataError(f"No series found for the query. URL -> {url}")
        )
    return records
