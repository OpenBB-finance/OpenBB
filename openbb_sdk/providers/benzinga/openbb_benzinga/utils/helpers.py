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


class BenzingaBaseNewsData(Data):
    created: datetime = Field(alias="date")
    title: str
    image: List[BenzingaImage]
    body: str = Field(alias="text")
    url: str

    @validator("created", pre=True)
    def time_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%a, %d %b %Y %H:%M:%S %z")
