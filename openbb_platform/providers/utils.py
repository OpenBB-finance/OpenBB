"""Provider Utility Functions"""

import random
from datetime import timedelta

import requests
from requests_cache import CachedSession


def make_session(**kwargs):
    """Create a session.  If user defines cache, use requests_cache."""

    if user_settings.cache:
        cache_time = kwargs.pop("cache_time", 1)
        session = CachedSession(
            "openbb_cache",
            use_cache_dir=True,  # Save files in the default user cache dir
            cache_control=True,  # Use Cache-Control response headers for expiration, if available
            expire_after=timedelta(
                minutes=cache_time
            ),  # Otherwise expire responses after one day
            allowable_codes=[200],
            allowable_methods=["GET", "POST"],  # Cache whatever HTTP methods you want
            ignored_parameters=[
                "api_key",
                "apikey",
                "apiKey",
            ],  # Don't match this request param, and redact if from the cache
        )
        return session
    return requests


def get_user_agent() -> str:
    """Get a not very random user agent."""
    user_agent_strings = [
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:86.1) Gecko/20100101 Firefox/86.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:86.1) Gecko/20100101 Firefox/86.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:82.1) Gecko/20100101 Firefox/82.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:83.0) Gecko/20100101 Firefox/83.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:84.0) Gecko/20100101 Firefox/84.0",
    ]

    return random.choice(user_agent_strings)  # nosec


def request(
    url: str, method: str = "GET", timeout: int = 0, **kwargs
) -> requests.Response:
    """Abstract helper to make requests from a url with potential headers and params.

    Parameters
    ----------
    url : str
        Url to make the request to
    method : str, optional
        HTTP method to use.  Can be "GET" or "POST", by default "GET"

    Returns
    -------
    requests.Response
        Request response object

    Raises
    ------
    ValueError
        If invalid method is passed
    """
    current_user = get_current_user()
    _session = kwargs.pop("session", make_session(**kwargs))
    # We want to add a user agent to the request, so check if there are any headers
    # If there are headers, check if there is a user agent, if not add one.
    # Some requests seem to work only with a specific user agent, so we want to be able to override it.
    headers = kwargs.pop("headers", {})
    timeout = timeout or current_user.preferences.REQUEST_TIMEOUT

    if "User-Agent" not in headers:
        headers["User-Agent"] = get_user_agent()
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
