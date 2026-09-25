"""Access to the v2 FRED API."""

from typing import Any

ROOT = "https://api.stlouisfed.org/fred/v2"
MAX_PAGES = 12
PAGE_LIMIT = 500000


def headers(api_key: str | None) -> dict:
    """Return the headers a v2 request carries.

    Parameters
    ----------
    api_key : str or None
        The FRED API key.

    Returns
    -------
    dict
        The request headers, carrying the key as a bearer token.
    """
    from openbb_fred.utils.api import headers as request_headers

    return request_headers(api_key or "")


async def release_observations(
    release_id: str | int,
    api_key: str | None,
    use_cache: bool = True,
) -> tuple[dict, dict]:
    """Read every series on a release, with its observations.

    Parameters
    ----------
    release_id : str or int
        The FRED release id.
    api_key : str or None
        The FRED API key.
    use_cache : bool
        Whether to read and write the on-disk cache.

    Returns
    -------
    tuple[dict, dict]
        The release description, and each series keyed by its id.

    Raises
    ------
    OpenBBError
        If the release is unknown or the key is not accepted.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_fred.utils.rate_limiter import fred_get

    request = headers(api_key)
    release: dict = {}
    series: dict[str, dict] = {}
    cursor: str | None = None

    for _ in range(MAX_PAGES):
        url = (
            f"{ROOT}/release/observations?release_id={release_id}"
            f"&format=json&limit={PAGE_LIMIT}"
        )

        if cursor:
            from urllib.parse import quote

            url += f"&next_cursor={quote(cursor)}"

        payload = await fred_get(url, use_cache=use_cache, headers=request)

        if not isinstance(payload, dict):
            break

        if payload.get("code"):
            raise OpenBBError(f"FRED rejected the request: {payload.get('message')}")

        release = payload.get("release") or release

        for entry in payload.get("series") or []:
            held = series.setdefault(entry["series_id"], {**entry, "observations": []})
            held["observations"].extend(entry.get("observations") or [])

        cursor = payload.get("next_cursor")

        if not payload.get("has_more") or not cursor:
            break

    if not series:
        raise OpenBBError(f"No series are published for release {release_id}.")

    return release, series


def published(observations: "list[dict]") -> dict[str, Any]:
    """Return the observations carrying a value, keyed by date.

    Parameters
    ----------
    observations : list[dict]
        The date and value pairs the API returned.

    Returns
    -------
    dict
        The value observed on each date.
    """
    return {
        o["date"]: float(o["value"])
        for o in observations
        if o.get("value") not in (".", "", None)
    }
