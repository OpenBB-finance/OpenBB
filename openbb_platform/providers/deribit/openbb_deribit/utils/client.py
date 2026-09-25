"""Transport for the Deribit public JSON-RPC API."""

from typing import Any

BASE_URL = "https://www.deribit.com/api/v2"
REQUEST_TIMEOUT = 60
TOO_MANY_REQUESTS = 429


def build_url(method: str, params: dict[str, Any] | None = None) -> str:
    """Return the request URL for one public method.

    Parameters
    ----------
    method : str
        The method name, without the 'public/' prefix.
    params : dict or None
        The query parameters. Entries with a value of None are dropped, and
        booleans are sent as the lower-case literals the API expects.

    Returns
    -------
    str
        The fully-qualified request URL.
    """
    from urllib.parse import urlencode

    query = {
        key: str(value).lower() if isinstance(value, bool) else value
        for key, value in (params or {}).items()
        if value is not None
    }
    url = f"{BASE_URL}/public/{method}"

    return f"{url}?{urlencode(query)}" if query else url


async def request(
    method: str,
    params: dict[str, Any] | None = None,
    use_cache: bool = True,
) -> Any:
    """Call one public method and return its result.

    Parameters
    ----------
    method : str
        The method name, without the 'public/' prefix.
    params : dict or None
        The query parameters.
    use_cache : bool
        Whether to read and write the on-disk response cache.

    Returns
    -------
    Any
        The 'result' member of the JSON-RPC response.

    Raises
    ------
    OpenBBError
        If the API reports an error, or the response cannot be read.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_deribit.utils.session import get_cached_session, get_session

    url = build_url(method, params)
    session = await get_cached_session() if use_cache else await get_session()

    try:
        response = await session.get(url, timeout=REQUEST_TIMEOUT)

        if response.status != 200:
            raise OpenBBError(
                f"Deribit answered public/{method} with HTTP {response.status}."
                + (
                    " The request rate was exceeded; narrow the query or retry."
                    if response.status == TOO_MANY_REQUESTS
                    else ""
                )
            )

        payload = await response.json(content_type=None)
    except OpenBBError:
        raise
    except Exception as error:  # noqa: BLE001
        raise OpenBBError(
            f"Deribit request failed for public/{method} ->"
            f" {error.__class__.__name__}: {error}"
        ) from error

    if not isinstance(payload, dict):
        raise OpenBBError(f"Unexpected Deribit response for public/{method}.")

    if payload.get("error"):
        detail = payload["error"]
        message = detail.get("message") if isinstance(detail, dict) else detail
        reason = detail.get("data") if isinstance(detail, dict) else None
        raise OpenBBError(
            f"Deribit returned an error for public/{method} -> {message}"
            + (f" {reason}" if reason else "")
        )

    return payload.get("result")


async def gather(
    calls: "list[tuple[str, dict[str, Any] | None]]",
    use_cache: bool = True,
) -> list:
    """Call several public methods at once.

    Parameters
    ----------
    calls : list[tuple[str, dict or None]]
        Each method name with its query parameters.
    use_cache : bool
        Whether to read and write the on-disk response cache.

    Returns
    -------
    list
        The result of each call, in the order it was given, with an exception
        in place of any result that could not be read.
    """
    import asyncio

    return await asyncio.gather(
        *(request(method, params, use_cache) for method, params in calls),
        return_exceptions=True,
    )
