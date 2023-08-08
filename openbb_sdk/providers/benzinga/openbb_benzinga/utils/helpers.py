"""Benzinga Helpers."""


from datetime import datetime
from typing import Dict, List, Optional

import requests
from openbb_provider.models.stock_news import StockNewsData
from pydantic import BaseModel, Field


def get_data(url: str, **kwargs: Any) -> dict:
    r = helpers.make_request(
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


class BenzingaStockNewsData(StockNewsData):
    """Benzinga Global News data."""

    images: List[BenzingaImage] = Field(
        description="The images associated with the news."
    )
    channels: Optional[List[str]] = Field(
        description="The channels associated with the news."
    )
    stocks: Optional[List[str]] = Field(
        description="The stocks associated with the news."
    )
    tags: Optional[List[str]] = Field(description="The tags associated with the news.")
    teaser: Optional[str] = Field(description="The teaser of the news.")

    @staticmethod
    def from_dict(d: Dict) -> "BenzingaStockNewsData":
        """Create a BenzingaGlobalNewsData object from a dictionary."""
        return BenzingaStockNewsData(
            date=datetime.strptime(d.get("created", None), "%a, %d %b %Y %H:%M:%S %z"),
            title=d.get("title", None),
            images=[BenzingaImage(**d) for d in d.get("image", [])],
            text=d.get("body", None),
            teaser=d.get("teaser", None),
            url=d.get("url", None),
            channels=[d.get("name", None) for d in d.get("channels", [{}])],
            stocks=[d.get("name", None) for d in d.get("stocks", [{}])],
            image=d.get("image", [{}])[0].get("url", None)
            if d.get("image", None)
            else None,
        )
