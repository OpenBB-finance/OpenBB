"""Seeking Alpha Utilities."""

from datetime import timedelta

from openbb_core.provider.utils.helpers import amake_request

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Connection": "keep-alive",
}


def date_range(start_date, end_date):
    """Yield dates between start_date and end_date."""
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


async def get_seekingalpha_id(symbol: str, **kwargs) -> str:
    """Map a ticker symbol to its Seeking Alpha ID."""
    session = kwargs.get("session")
    url = "https://seekingalpha.com/api/v3/searches"
    querystring = {
        "filter[type]": "symbols",
        "filter[list]": "all",
        "page[size]": "100",
    }
    querystring["filter[query]"] = symbol
    if session:
        response = await amake_request(
            url, headers=HEADERS, params=querystring, session=session
        )
    else:
        response = await amake_request(url, headers=HEADERS, params=querystring)
    ids = response.get("symbols")  # type: ignore

    return str(ids[0].get("id", "")) if isinstance(ids, list) and ids else ""
