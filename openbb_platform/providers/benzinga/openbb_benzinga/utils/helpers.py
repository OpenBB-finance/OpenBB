"""Benzinga Helpers."""


from typing import Any, Dict

from openbb_core.provider import helpers


def get_data(url: str, **kwargs: Any) -> Dict:
    """Do an API request to Benzinga and return the data."""
    result = helpers.make_request(
        url, timeout=10, headers={"accept": "application/json"}, **kwargs
    )
    if result.status_code != 200:
        data = result.json()
        if data == ['Access denied for user 0 "anonymous"']:
            raise RuntimeError("API Key is invalid")
        if len(data) == 0:
            raise RuntimeError("No news found!")
        message = data.get("message")
        error = data.get("error")
        value = message or error
        raise RuntimeError(f"Error in Benzinga request -> {value}")

    return result.json()
