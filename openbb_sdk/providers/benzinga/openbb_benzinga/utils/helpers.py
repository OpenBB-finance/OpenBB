"""Benzinga Helpers."""


from datetime import datetime
from typing import List

import requests
from openbb_provider.abstract.data import Data
from pydantic import BaseModel, Field, validator


def get_data(url: str) -> dict:
    r = requests.get(url, timeout=10, headers={"accept": "application/json"})
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
