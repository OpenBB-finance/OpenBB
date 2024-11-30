"""Provider helpers."""

import asyncio
import os
from datetime import date, datetime, timedelta, timezone
from difflib import SequenceMatcher
from functools import partial
from inspect import iscoroutinefunction
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    List,
    Literal,
    Optional,
    TypeVar,
    Union,
    cast,
)

from anyio.from_thread import start_blocking_portal
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.utils.client import (
    ClientResponse,
    ClientSession,
    get_user_agent,
)
from typing_extensions import ParamSpec

if TYPE_CHECKING:
    from requests import Response  # pylint: disable=import-outside-toplevel

T = TypeVar("T")
P = ParamSpec("P")
D = TypeVar("D", bound="Data")


def check_item(item: str, allowed: List[str], threshold: float = 0.75) -> None:
    """Check if an item is in a list of allowed items and raise an error if not.

    Parameters
    ----------
    item : str
        The item to check.
    allowed : List[str]
        The list of allowed items.
    threshold : float, optional
        The similarity threshold for the error message, by default 0.75

    Raises
    ------
    ValueError
        If the item is not in the allowed list.
    """
    if item not in allowed:
        similarities = map(
            lambda c: (c, SequenceMatcher(None, item, c).ratio()), allowed
        )
        similar, score = max(similarities, key=lambda x: x[1])
        if score > threshold:
            raise ValueError(f"'{item}' is not available. Did you mean '{similar}'?")
        raise ValueError(f"'{item}' is not available.")


def get_querystring(items: dict, exclude: List[str]) -> str:
    """Turn a dictionary into a querystring, excluding the keys in the exclude list.

    Parameters
    ----------
    items: dict
        The dictionary to be turned into a querystring.

    exclude: List[str]
        The keys to be excluded from the querystring.

    Returns
    -------
    str
        The querystring.
    """
    for key in exclude:
        items.pop(key, None)

    query_items = []
    for key, value in items.items():
        if value is None:
            continue
        if isinstance(value, list):
            for item in value:
                query_items.append(f"{key}={item}")
        else:
            query_items.append(f"{key}={value}")

    querystring = "&".join(query_items)

    return f"{querystring}" if querystring else ""


def get_python_request_settings() -> dict:
    """Get the python settings."""
    # pylint: disable=import-outside-toplevel
    from openbb_core.app.service.system_service import SystemService

    python_settings = SystemService().system_settings.python_settings.model_dump()
    http_settings = python_settings.get("http", {})
    allowed_keys = [
        "cafile",
        "certfile",
        "keyfile",
        "password",
        "verify_ssl",
        "fingerprint",
        "proxy",
        "proxy_auth",
        "proxy_headers",
        "timeout",
        "auth",
        "headers",
        "cookies",
        "server_hostname",
    ]

    return {
        k: v for k, v in http_settings.items() if v is not None and k in allowed_keys
    }


def get_certificates() -> Optional[str]:
    """Handle request certificate environment variable for Requests library.

    This function is used to set the REQUESTS_CA_BUNDLE environment variable for the Requests library
    based on the system settings. If a custom certificate file is provided, it will be combined with the
    default CA bundle. If a custom certificate file is not provided, the default CA bundle will be used.

    We do this so that we can use a custom certificate file for requests, while still using the default CA
    and without limiting the user to only using the custom certificate file.

    We also set the proxy environment variables for the session, if they are provided in the system settings.

    Returns
    -------
    Optional[str]
        The original value of the REQUESTS_CA_BUNDLE environment variable.
        Used to restore the variable after the request is made.
    """
    request_settings = get_python_request_settings()
    old_verify = os.environ.get("REQUESTS_CA_BUNDLE")

    if request_settings.get("verify_ssl") is False:
        os.environ["REQUESTS_CA_BUNDLE"] = ""
    else:
        if request_settings.get("cafile"):
            os.environ["REQUESTS_CA_BUNDLE"] = combine_certificates(
                request_settings["cafile"]
            )
        if old_verify and not request_settings.get("cafile"):
            certs = os.environ.pop("REQUESTS_CA_BUNDLE", None)
            if certs:
                os.environ["REQUESTS_CA_BUNDLE"] = combine_certificates(certs)
        if (
            request_settings.get("cafile")
            and old_verify
            and request_settings["cafile"] != old_verify
        ):
            os.environ["REQUESTS_CA_BUNDLE"] = combine_certificates(
                request_settings["cafile"], old_verify
            )

    if request_settings.get("proxy"):
        os.environ["HTTPS_PROXY"] = request_settings["proxy"]
        os.environ["HTTP_PROXY"] = request_settings["proxy"]

    return old_verify


def restore_certs(old_verify) -> None:
    """Restore the original request certificate environment variable after use.

    We do this for the Requests library to ensure that the original value of the REQUESTS_CA_BUNDLE
    environment variable is restored after the request is made.
    """
    if old_verify:
        os.environ["REQUESTS_CA_BUNDLE"] = old_verify
    else:
        _ = os.environ.pop("REQUESTS_CA_BUNDLE", None)


async def amake_request(
    url: str,
    method: Literal["GET", "POST"] = "GET",
    timeout: int = 10,
    response_callback: Optional[
        Callable[[ClientResponse, ClientSession], Awaitable[Union[dict, List[dict]]]]
    ] = None,
    **kwargs,
) -> Union[dict, List[dict]]:
    """
    Abstract helper to make requests from a url with potential headers and params.

    Parameters
    ----------
    url : str
        Url to make the request to
    method : str, optional
        HTTP method to use.  Can be "GET" or "POST", by default "GET"
    timeout : int, optional
        Timeout in seconds, by default 10.  Can be overwritten by user setting, request_timeout
    response_callback : Callable[[ClientResponse, ClientSession], Awaitable[Union[dict, List[dict]]]], optional
        Async callback with response and session as arguments that returns the json, by default None
    session : ClientSession, optional
        Custom session to use for requests, by default None


    Returns
    -------
    Union[dict, List[dict]]
        Response json
    """
    # pylint: disable=import-outside-toplevel
    import aiohttp  # noqa
    import ssl
    from openbb_core.env import Env

    Env()

    if method.upper() not in ["GET", "POST"]:
        raise ValueError("Method must be GET or POST")

    kwargs["timeout"] = kwargs.pop("preferences", {}).get("request_timeout", timeout)

    response_callback = response_callback or (
        lambda r, _: asyncio.ensure_future(r.json())
    )

    # We need to handle SSL context and proxy settings for AIOHTTP.
    # We will accommodate the Requests environment variable for the CA bundle.
    python_settings = get_python_request_settings()

    if (
        os.environ.get("HTTP_PROXY")
        or os.environ.get("HTTPS_PROXY")
        or python_settings.get("proxy")
        or python_settings.get("verify_ssl") is False
    ):
        python_settings["proxy"] = (
            python_settings.get("proxy")
            or os.environ.get("HTTP_PROXY")
            or os.environ.get("HTTPS_PROXY")
        )

        python_settings["ssl"] = False
        python_settings["verify_ssl"] = None
    elif (
        python_settings.get("certfile")
        or python_settings.get("cafile")
        or os.environ.get("REQUESTS_CA_BUNDLE")
    ):
        ca = python_settings.get("cafile") or os.environ.get("REQUESTS_CA_BUNDLE")
        cert = python_settings.get("certfile")
        key = python_settings.get("keyfile")
        password = python_settings.get("password")
        ssl_context = ssl.create_default_context()

        if ca:
            ssl_context.load_verify_locations(cafile=ca)

        if cert:
            ssl_context.load_cert_chain(
                certfile=cert,
                keyfile=key,
                password=password,
            )

        python_settings["ssl"] = ssl_context

    ssl_kwargs = {
        k: v
        for k, v in python_settings.items()
        if k in ["ssl", "verify_ssl", "fingerprint"] and v is not None
    }

    if python_settings:
        kwargs.update(
            {k: v for k, v in python_settings.items() if not k.endswith("file")}
        )

    connector = (
        aiohttp.TCPConnector(ttl_dns_cache=300, **ssl_kwargs) if ssl_kwargs else None
    )

    conn_kwargs = {"connector": connector} if connector else {}

    with_session = kwargs.pop("with_session", "session" in kwargs)
    session: ClientSession = kwargs.pop(
        "session", ClientSession(trust_env=True, **conn_kwargs)
    )

    try:
        response = await session.request(method, url, **kwargs)
        return await response_callback(response, session)
    finally:
        if not with_session:
            await session.close()


async def amake_requests(
    urls: Union[str, List[str]],
    response_callback: Optional[
        Callable[[ClientResponse, ClientSession], Awaitable[Union[dict, List[dict]]]]
    ] = None,
    **kwargs,
):
    """Make multiple requests asynchronously.

    Parameters
    ----------
    urls : Union[str, List[str]]
        List of urls to make requests to
    method : Literal["GET", "POST"], optional
        HTTP method to use.  Can be "GET" or "POST", by default "GET"
    timeout : int, optional
        Timeout in seconds, by default 10.  Can be overwritten by user setting, request_timeout
    response_callback : Callable[[ClientResponse, ClientSession], Awaitable[Union[dict, List[dict]]]], optional
        Async callback with response and session as arguments that returns the json, by default None
    session : ClientSession, optional
        Custom session to use for requests, by default None

    Returns
    -------
    Union[dict, List[dict]]
        Response json
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.env import Env

    Env()
    session: ClientSession = kwargs.pop("session", ClientSession(trust_env=True))
    kwargs["response_callback"] = response_callback

    urls = urls if isinstance(urls, list) else [urls]

    try:
        results = []

        for result in await asyncio.gather(
            *[amake_request(url, session=session, **kwargs) for url in urls],
            return_exceptions=True,
        ):
            is_exception = isinstance(result, Exception)

            if is_exception and kwargs.get("raise_for_status", False):
                raise result  # type: ignore[misc]

            if is_exception or not result:
                continue

            results.extend(
                result if isinstance(result, list) else [result]  # type: ignore[list-item]
            )

        return results

    finally:
        await session.close()


def combine_certificates(cert: str, bundle: Optional[str] = None) -> str:
    """Combine a certificate and a bundle into a single certificate file. Use the default bundle if none is provided."""
    # pylint: disable=import-outside-toplevel
    import atexit  # noqa
    import certifi
    import shutil
    from pathlib import Path
    from warnings import warn

    if not Path(cert).exists():
        raise FileNotFoundError(f"Certificate file '{cert}' not found")

    if cert.split(".")[0].endswith("_combined"):
        return cert

    combined_cert = cert.split(".")[0] + "_combined." + cert.split(".")[1]

    if Path(combined_cert).exists():
        return combined_cert

    if not bundle:
        bundle = certifi.where()

    try:
        with open(combined_cert, "wb") as combined_cert_file:
            # Write the default CA bundle to the combined certificate file
            with open(bundle, "rb") as bundle_file:
                shutil.copyfileobj(bundle_file, combined_cert_file)

            # Write the custom CA certificate to the combined certificate file
            with open(cert, "rb") as cert_file:
                shutil.copyfileobj(cert_file, combined_cert_file)

        # Register the combined certificate file for deletion
        atexit.register(os.remove, combined_cert)

        return combined_cert
    except Exception as e:  # pylint: disable=broad-except
        warn(
            f"An error occurred while handling the certificates file -> {e.__class__.__name__}: {e}"
        )
        return cert


def make_request(
    url: str, method: str = "GET", timeout: int = 10, **kwargs
) -> "Response":
    """Abstract helper to make requests from a url with potential headers and params.

    Parameters
    ----------
    url : str
        Url to make the request to
    method : str, optional
        HTTP method to use.  Can be "GET" or "POST", by default "GET"
    timeout : int, optional
        Timeout in seconds, by default 10.  Can be overwritten by user setting, request_timeout

    Returns
    -------
    Response
        Request response object

    Raises
    ------
    ValueError
        If invalid method is passed
    """
    # pylint: disable=import-outside-toplevel
    import requests
    from openbb_core.env import Env

    # We want to add a user agent to the request, so check if there are any headers
    # If there are headers, check if there is a user agent, if not add one.
    # Some requests seem to work only with a specific user agent, so we want to be able to override it.
    Env()
    python_settings = get_python_request_settings()
    headers = kwargs.pop("headers", {})
    headers.update(python_settings.pop("headers", {}))
    preferences = kwargs.pop("preferences", None)

    if preferences and "request_timeout" in preferences:
        timeout = preferences["request_timeout"] or timeout
    elif "timeout" in python_settings:
        timeout = python_settings["timeout"]

    if "User-Agent" not in headers:
        headers["User-Agent"] = get_user_agent()

    # Allow a custom session for caching, if desired
    _session = kwargs.pop("session", None) or requests

    if (
        python_settings.get("cafile") is not None
        and os.environ.get("REQUESTS_CA_BUNDLE") is not None
    ):
        kwargs["verify"] = (
            combine_certificates(
                python_settings["cafile"], os.environ.get("REQUESTS_CA_BUNDLE")
            )
            if python_settings["cafile"] != os.environ.get("REQUESTS_CA_BUNDLE")
            else combine_certificates(python_settings["cafile"])
        )
    elif python_settings.get("cafile") is not None:
        kwargs["verify"] = combine_certificates(python_settings["cafile"])
    elif os.environ.get("REQUESTS_CA_BUNDLE") and python_settings.get("cafile") is None:
        certs = os.environ.get("REQUESTS_CA_BUNDLE", "")
        kwargs["verify"] = combine_certificates(certs)

    if python_settings.get("verify_ssl") is False:
        kwargs["verify"] = False

    if python_settings.get("certfile"):
        kwargs["cert"] = (
            (python_settings["certfile"], python_settings.get("keyfile"))
            if python_settings.get("keyfile") is not None
            else python_settings["certfile"]
        )

    if python_settings.get("proxy"):
        kwargs["proxies"] = {
            "http": python_settings["proxy"],
            "https": python_settings["proxy"],
        }

    if method.upper() == "GET":
        return _session.get(
            url,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )
    if method.upper() == "POST":
        return _session.post(
            url,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )
    raise ValueError("Method must be GET or POST")


def to_snake_case(string: str) -> str:
    """Convert a string to snake case."""
    import re  # pylint: disable=import-outside-toplevel

    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", string)
    return (
        re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
        .lower()
        .replace(" ", "_")
        .replace("__", "_")
    )


async def maybe_coroutine(
    func: Callable[P, Union[T, Awaitable[T]]], /, *args: P.args, **kwargs: P.kwargs
) -> T:
    """Check if a function is a coroutine and run it accordingly."""
    if not iscoroutinefunction(func):
        return cast(T, func(*args, **kwargs))

    return await func(*args, **kwargs)


def run_async(
    func: Callable[P, Awaitable[T]], /, *args: P.args, **kwargs: P.kwargs
) -> T:
    """Run a coroutine function in a blocking context."""
    if not iscoroutinefunction(func):
        return cast(T, func(*args, **kwargs))

    with start_blocking_portal() as portal:
        try:
            return portal.call(partial(func, *args, **kwargs))
        finally:
            portal.call(portal.stop)


def filter_by_dates(
    data: List[D], start_date: Optional[date] = None, end_date: Optional[date] = None
) -> List[D]:
    """Filter data by dates."""
    if start_date is None and end_date is None:
        return data

    def _filter(d: Data) -> bool:
        _date = getattr(d, "date", None)
        dt = _date.date() if _date and isinstance(_date, datetime) else _date
        if dt:
            if start_date and end_date:
                return start_date <= dt <= end_date
            if start_date:
                return dt >= start_date
            if end_date:
                return dt <= end_date
            return True
        return False

    return list(filter(_filter, data))


def safe_fromtimestamp(
    timestamp: Union[float, int], tz: Optional[timezone] = None
) -> datetime:
    """datetime.fromtimestamp alternative which supports negative timestamps on Windows platform."""
    if os.name == "nt" and timestamp < 0:
        return datetime(1970, 1, 1, tzinfo=tz) + timedelta(seconds=timestamp)
    return datetime.fromtimestamp(timestamp, tz)
