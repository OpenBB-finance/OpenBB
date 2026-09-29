"""Typed access to the FRED API, through the throttled and cached transport."""

from typing import Any

ROOT_URL = "https://api.stlouisfed.org/fred"
GEO_ROOT_URL = "https://api.stlouisfed.org/geofred"


def build_url(
    path: str, api_key: str | None, *, root: str = ROOT_URL, **params: Any
) -> str:
    """Build a FRED request URL.

    Parameters
    ----------
    path : str
        The endpoint path, relative to the API root.
    api_key : str or None
        The FRED API key.
    root : str
        The API root the path is read from.
    **params : Any
        Query parameters, with None values dropped.

    Returns
    -------
    str
        The signed request URL.
    """
    from urllib.parse import urlencode

    query = {k: v for k, v in params.items() if v is not None}
    query["api_key"] = api_key or ""
    query["file_type"] = "json"

    return f"{root}/{path.lstrip('/')}?{urlencode(query, doseq=True)}"


def headers(api_key: str | None = None) -> dict:
    """Return the headers a FRED request carries.

    Parameters
    ----------
    api_key : str or None
        A key to send as a bearer token, for the endpoints that read one from
        the header rather than the query string.

    Returns
    -------
    dict
        The request headers.
    """
    from aiohttp.http import SERVER_SOFTWARE

    sent = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "User-Agent": SERVER_SOFTWARE,
    }

    if api_key is not None:
        sent["Authorization"] = f"Bearer {api_key or ''}"

    return sent


def _as_date(value: Any) -> Any:
    """Return a date as ``YYYY-MM-DD``, and anything else unchanged."""
    return value.strftime("%Y-%m-%d") if hasattr(value, "strftime") else value or None


def observations_url(
    series_id: str,
    api_key: str | None,
    start_date=None,
    end_date=None,
    **params: Any,
) -> str:
    """Build the observations URL for one FRED series.

    Parameters
    ----------
    series_id : str
        The FRED series id, such as 'IORB'.
    api_key : str or None
        The FRED API key.
    start_date : date or None
        The earliest observation to return.
    end_date : date or None
        The latest observation to return.
    **params : Any
        Any further parameters the endpoint accepts.

    Returns
    -------
    str
        The signed request URL.
    """
    params.pop("preferences", None)
    params.pop("use_cache", None)

    return build_url(
        "series/observations",
        api_key,
        series_id=series_id,
        observation_start=_as_date(start_date),
        observation_end=_as_date(end_date),
        **params,
    )


def observation_dates(value: Any) -> list:
    """Return the period-start dates a release table is asked for.

    Parameters
    ----------
    value : Any
        The ``date`` query parameter, in any shape it accepts.

    Returns
    -------
    list
        One entry per requested period, or ``[None]`` for the latest.
    """
    from openbb_fred.utils.query import join_dates

    joined = join_dates(value)

    if not joined:
        return [None]

    return sorted({f"{entry[:-2]}01" for entry in joined.split(",")})


def release_tables_url(
    release_id: Any,
    element_id: Any,
    api_key: str | None,
    observation_date: str | None = None,
) -> str:
    """Build the release tables URL for one element of a release.

    Parameters
    ----------
    release_id : Any
        The FRED release id.
    element_id : Any
        The element within the release, or None for the whole release.
    api_key : str or None
        The FRED API key.
    observation_date : str or None
        The period to read, or None for the latest.

    Returns
    -------
    str
        The signed request URL.
    """
    return build_url(
        "release/tables",
        api_key,
        release_id=release_id,
        element_id=element_id,
        observation_date=observation_date,
        include_observation_values="true",
    )


def published_value(value: Any) -> float | None:
    """Return one observation as a number.

    Parameters
    ----------
    value : Any
        The observation as FRED wrote it.

    Returns
    -------
    float or None
        The value, or None on a date FRED published nothing for.
    """
    if value in (".", "", None):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _observations(payload: Any, series_id: str) -> list[dict]:
    """Return the observations carried by one response.

    Parameters
    ----------
    payload : Any
        The response the endpoint returned.
    series_id : str
        The series the response was asked for.

    Returns
    -------
    list[dict]
        One entry per observation.

    Raises
    ------
    OpenBBError
        If FRED reports an error, or the series has no observations.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    if not payload:
        raise OpenBBError(f"No data exists for series id: {series_id}")

    if isinstance(payload, dict) and payload.get("error_message"):
        raise OpenBBError(payload["error_message"])

    return payload.get("observations", [])


async def get_observations(
    series_id: str,
    api_key: str | None,
    start_date=None,
    end_date=None,
    use_cache: bool = True,
    **params: Any,
) -> list[dict]:
    """Get the observations for one FRED series.

    Parameters
    ----------
    series_id : str
        The FRED series id, such as 'IORB'.
    api_key : str or None
        The FRED API key.
    start_date : date or None
        The earliest observation to return.
    end_date : date or None
        The latest observation to return.
    use_cache : bool
        Whether to read and write the response cache.
    **params : Any
        Any further parameters the endpoint accepts.

    Returns
    -------
    list[dict]
        One entry per observation.

    Raises
    ------
    OpenBBError
        If FRED reports an error, or the series has no observations.
    """
    from openbb_fred.utils.rate_limiter import fred_get

    url = observations_url(series_id, api_key, start_date, end_date, **params)

    return _observations(await fred_get(url, use_cache=use_cache), series_id)


async def get_observations_many(
    series_ids: "list[str]",
    api_key: str | None,
    start_date=None,
    end_date=None,
    use_cache: bool = True,
    **params: Any,
) -> "list[list[dict]]":
    """Get the observations for many FRED series, in the order asked for.

    Parameters
    ----------
    series_ids : list[str]
        The FRED series ids to read.
    api_key : str or None
        The FRED API key.
    start_date : date or None
        The earliest observation to return.
    end_date : date or None
        The latest observation to return.
    use_cache : bool
        Whether to read and write the response cache.
    **params : Any
        Any further parameters the endpoint accepts.

    Returns
    -------
    list[list[dict]]
        The observations for each series, aligned with ``series_ids``.

    Raises
    ------
    OpenBBError
        If FRED reports an error, or a series has no observations.
    """
    from openbb_fred.utils.rate_limiter import fred_get_many

    urls = [
        observations_url(series_id, api_key, start_date, end_date, **params)
        for series_id in series_ids
    ]
    payloads = await fred_get_many(urls, use_cache=use_cache)

    return [
        _observations(payload, series_id)
        for payload, series_id in zip(payloads, series_ids)
    ]


def unwrap_series(
    response: Any,
) -> "tuple[list, dict]":
    """Split a series fetch into its rows and its metadata.

    Parameters
    ----------
    response : Any
        An ``AnnotatedResult``, or the rows on their own.

    Returns
    -------
    tuple[list, dict]
        The rows, and the metadata keyed by series id.
    """
    result = getattr(response, "result", None)

    if result is None:
        return list(response or []), {}

    return list(result or []), getattr(response, "metadata", None) or {}
