"""Provider helpers."""
import asyncio
import re
from functools import partial
from inspect import iscoroutinefunction
from typing import Awaitable, Callable, List, Literal, Optional, TypeVar, Union, cast

from anyio import start_blocking_portal
from typing_extensions import ParamSpec

from openbb_core.provider.utils.client import (
    ClientResponse,
    ClientSession,
)

T = TypeVar("T")
P = ParamSpec("P")


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


async def make_request(
    url: str,
    method: Literal["GET", "POST"] = "GET",
    timeout: int = 10,
    response_callback: Optional[
        Callable[[ClientResponse, ClientSession], Awaitable[Union[dict, List[dict]]]]
    ] = None,
    **kwargs,
) -> Union[dict, List[dict]]:
    """Abstract helper to make requests from a url with potential headers and params.


    Parameters
    ----------
    url : str
        Url to make the request to
    method : str, optional
        HTTP method to use.  Can be "GET" or "POST", by default "GET"
    timeout : int, optional
        Timeout in seconds, by default 10.  Can be overwritten by user setting, request_timeout
    response_callback : Callable[[aiohttp.ClientResponse], Awaitable[Union[dict, List[dict]]]], optional
        Callback to run on the response, by default None


    Returns
    -------
    Union[dict, List[dict]]
        Response json
    """
    response_callback = response_callback or (
        lambda r, _: asyncio.ensure_future(r.json())
    )

    kwargs["timeout"] = kwargs.pop("preferences", {}).get("request_timeout", timeout)
    with_session = kwargs.pop("with_session", False)
    session: ClientSession = kwargs.pop("session", ClientSession())

    response = await session.request(method, url, **kwargs)
    data = await response_callback(response, session)

    if not with_session:
        await session.close()

    return data


async def make_requests(urls: List[str], **kwargs) -> Union[dict, List[dict]]:
    """Make multiple requests asynchronously.

    Parameters
    ----------
    urls : List[str]
        List of urls to make requests to
    method : Literal["GET", "POST"], optional
        HTTP method to use.  Can be "GET" or "POST", by default "GET"
    timeout : int, optional
        Timeout in seconds, by default 10.  Can be overwritten by user setting, request_timeout
    response_callback : Callable[[ClientResponse, ClientSession], Awaitable[Union[dict, List[dict]]]], optional
        Callback to run on the response, by default None

    Returns
    -------
    Union[dict, List[dict]]
        Response json
    """
    session: ClientSession = kwargs.pop("session", ClientSession())
    kwargs["with_session"] = True

    results = await asyncio.gather(
        *[make_request(url, session=session, **kwargs) for url in urls]
    )

    await session.close()

    if isinstance(results[0], list):
        return [item for sublist in results for item in sublist]

    return results


def to_snake_case(string: str) -> str:
    """Convert a string to snake case."""
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
        return portal.call(partial(func, *args, **kwargs))
