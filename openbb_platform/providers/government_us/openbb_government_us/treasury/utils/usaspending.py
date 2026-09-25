"""USAspending API client."""

from typing import Any, Literal

BASE_URL = "https://api.usaspending.gov/api/v2/"


async def _request(
    url: str,
    method: Literal["GET", "POST"] = "GET",
    payload: dict | None = None,
    **kwargs: Any,
) -> Any:
    """Send a single request to the USAspending API.

    Parameters
    ----------
    url : str
        Absolute request URL.
    method : Literal["GET", "POST"]
        HTTP method.
    payload : dict | None
        JSON body to send with a POST.

    Returns
    -------
    Any
        The decoded JSON response.
    """
    from openbb_core.provider.utils.helpers import amake_request

    if payload is not None:
        kwargs["json"] = payload
        headers = dict(kwargs.pop("headers", None) or {})
        headers.setdefault("Content-Type", "application/json")
        kwargs["headers"] = headers

    return await amake_request(url, method=method, **kwargs)


def _check_response(response: Any, url: str) -> Any:
    """Validate a USAspending response body.

    Parameters
    ----------
    response : Any
        The decoded response body.
    url : str
        The request URL, used in error messages.

    Returns
    -------
    dict | list
        The validated response body. A few endpoints, such as
        'recipient/children/<key>/', return a bare array rather than an object.

    Raises
    ------
    OpenBBError
        If the body is neither a JSON object nor array, or carries an API
        error message.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    if isinstance(response, list):
        return response

    if not isinstance(response, dict):
        raise OpenBBError(f"Unexpected USAspending response -> {url} -> {response}")

    if "detail" in response:
        raise OpenBBError(f"USAspending API error -> {response['detail']}")

    return response


async def get_usaspending(path: str, **kwargs: Any) -> Any:
    """Send a GET request to a USAspending endpoint.

    Parameters
    ----------
    path : str
        Endpoint path under the v2 base, e.g. 'awards/CONT_IDV_X_1549/'.

    Returns
    -------
    Any
        The decoded JSON response, an object or a bare array.

    Raises
    ------
    OpenBBError
        If the request fails or the API returns an error.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    url = f"{BASE_URL}{path}"

    try:
        response = await _request(url, method="GET", **kwargs)
    except Exception as e:  # noqa: BLE001
        raise OpenBBError(
            f"USAspending request failed -> {url} -> {e.__class__.__name__}: {e}"
        ) from e

    return _check_response(response, url)


async def post_usaspending(path: str, payload: dict, **kwargs: Any) -> dict:
    """Send a POST request with a JSON body to a USAspending endpoint.

    Parameters
    ----------
    path : str
        Endpoint path under the v2 base, e.g. 'subawards/'.
    payload : dict
        The JSON request body.

    Returns
    -------
    dict
        The decoded JSON response.

    Raises
    ------
    OpenBBError
        If the request fails or the API returns an error.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    url = f"{BASE_URL}{path}"

    try:
        response = await _request(url, method="POST", payload=payload, **kwargs)
    except Exception as e:  # noqa: BLE001
        raise OpenBBError(
            f"USAspending request failed -> {url} -> {e.__class__.__name__}: {e}"
        ) from e

    return _check_response(response, url)
