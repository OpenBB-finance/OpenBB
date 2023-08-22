"""Benzinga Helpers."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider import helpers
from openbb_provider.standard_models.stock_news import StockNewsData
from pydantic import BaseModel, Field


def get_data(url: str, **kwargs: Any) -> dict:
    """Do an API request to Benzinga and return the data."""
    result = helpers.make_request(
        url, timeout=10, headers={"accept": "application/json"}, **kwargs
    )
    if result.status_code != 200:
        data = result.json()
        if data == ['Access denied for user 0 "anonymous"']:
            raise RuntimeError("API Key is invalid")
        message = data.get("message")
        error = data.get("error")
        value = message or error
        raise RuntimeError(f"Error in Benzinga request -> {value}")

    return result.json()


class BenzingaImage(BaseModel):
    size: str
    url: str


class BenzingaStockNewsData(StockNewsData):
    """Benzinga Global News data."""

    images: List[BenzingaImage] = Field(description="Images associated with the news.")
    channels: Optional[List[str]] = Field(
        description="Channels associated with the news."
    )
    stocks: Optional[List[str]] = Field(description="Stocks associated with the news.")
    tags: Optional[List[str]] = Field(description="Tags associated with the news.")
    teaser: Optional[str] = Field(description="Teaser of the news.")

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
