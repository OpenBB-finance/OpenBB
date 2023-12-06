"""FMP Market Snapshots Model."""

from typing import Any, Dict, List, Optional, Union

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.market_snapshots import (
    MarketSnapshotsData,
    MarketSnapshotsQueryParams,
)
from openbb_fmp.utils.definitions import MARKETS
from openbb_fmp.utils.helpers import get_data
from pydantic import Field


class FMPMarketSnapshotsQueryParams(MarketSnapshotsQueryParams):
    """FMP Market Snapshots Query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Most-of-the-EuroNext
    """

    market: MARKETS = Field(
        description="The market to fetch data for.", default="NASDAQ"
    )


class FMPMarketSnapshotsData(MarketSnapshotsData):
    """FMP Market Snapshots Data."""

    __alias_dict__ = {
        "high": "dayHigh",
        "low": "dayLow",
        "prev_close": "previousClose",
        "change_percent": "changesPercentage",
    }

    price: Optional[float] = Field(
        description="The last price of the stock.", default=None
    )

    avg_volume: Optional[int] = Field(
        description="Average volume of the stock.", alias="avgVolume", default=None
    )
    ma50: Optional[float] = Field(
        description="The 50-day moving average.", alias="priceAvg50", default=None
    )
    ma200: Optional[float] = Field(
        description="The 200-day moving average.", alias="priceAvg200", default=None
    )
    year_high: Optional[float] = Field(
        description="The 52-week high.", alias="yearHigh", default=None
    )
    year_low: Optional[float] = Field(
        description="The 52-week low.", alias="yearLow", default=None
    )
    market_cap: Optional[float] = Field(
        description="Market cap of the stock.", alias="marketCap", default=None
    )
    shares_outstanding: Optional[float] = Field(
        description="Number of shares outstanding.",
        alias="sharesOutstanding",
        default=None,
    )
    eps: Optional[float] = Field(description="Earnings per share.", default=None)
    pe: Optional[float] = Field(description="Price to earnings ratio.", default=None)
    exchange: Optional[str] = Field(
        description="The exchange of the stock.", default=None
    )
    timestamp: Optional[Union[int, float]] = Field(
        description="The timestamp of the data.", default=None
    )
    earnings_announcement: Optional[str] = Field(
        description="The earnings announcement of the stock.",
        alias="earningsAnnouncement",
        default=None,
    )
    name: Optional[str] = Field(
        description="The name associated with the stock symbol.", default=None
    )


class FMPMarketSnapshotsFetcher(
    Fetcher[
        FMPMarketSnapshotsQueryParams,
        List[FMPMarketSnapshotsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPMarketSnapshotsQueryParams:
        """Transform the query params."""
        return FMPMarketSnapshotsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPMarketSnapshotsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""
        url = f"https://financialmodelingprep.com/api/v3/quotes/{query.market}?apikey={api_key}"

        return await get_data(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPMarketSnapshotsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPMarketSnapshotsData]:
        """Return the transformed data."""
        return [FMPMarketSnapshotsData.model_validate(d) for d in data]
