"""Ultima Helpers."""


from typing import Any, Dict

from openbb_core.provider import helpers


def get_data(url: str, **kwargs: Any) -> Dict:
    """Do an API request to Ultima and return the data."""
    auth = kwargs.pop("auth", "")
    if auth is None or len(auth) == 0:
        raise RuntimeError("Ultima API key is required.")
    if "Bearer" not in auth:
        auth = f"Bearer {auth}"
    result = helpers.make_request(
        url,
        timeout=10,
        headers={"accept": "application/json", "Authorization": auth},
        **kwargs,
    )
    if result.status_code != 200:
        data = result.json()
        message = data.get("message")
        raise RuntimeError(f"Error in Ultima request -> {message}")

    return result.json()
