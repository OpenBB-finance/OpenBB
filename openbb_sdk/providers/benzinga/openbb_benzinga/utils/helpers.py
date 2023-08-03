"""Benzinga Helpers."""


from typing import Any

from openbb_provider import utils
from pydantic import BaseModel


def get_data(url: str, **kwargs: Any) -> dict:
    r = utils.make_request(
        url, timeout=10, headers={"accept": "application/json"}, **kwargs
    )
    if r.status_code != 200:
        data = r.json()
        if data == ['Access denied for user 0 "anonymous"']:
            raise RuntimeError("API Key is invalid")
        message = data.get("message")
        error = data.get("error")
        value = message or error
        raise RuntimeError(f"Error in Benzinga request -> {value}")

    return r.json()


class BenzingaImage(BaseModel):
    size: str
    url: str
