"""FMP Market Snapshots fetcher."""

from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_fmp.utils.helpers import MARKETS
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.market_snapshots import (
    MarketSnapshotsData,
    MarketSnapshotsQueryParams,
)
from openbb_provider.utils.helpers import make_request
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

    avg_volume: Optional[int] = Field(
        description="Average volume of the stock.", alias="avgVolume"
    )
    ma50: Optional[float] = Field(
        description="The 50-day moving average.", alias="priceAvg50"
    )
    ma200: Optional[float] = Field(
        description="The 200-day moving average.", alias="priceAvg200"
    )
    year_high: Optional[float] = Field(
        description="The 52-week high.", alias="yearHigh"
    )
    year_low: Optional[float] = Field(description="The 52-week low.", alias="yearLow")
    market_cap: Optional[float] = Field(
        description="Market cap of the stock.", alias="marketCap"
    )
    shares_outstanding: Optional[float] = Field(
        description="Number of shares outstanding.", alias="sharesOutstanding"
    )
    eps: Optional[float] = Field(description="Earnings per share.")
    pe: Optional[float] = Field(description="Price to earnings ratio.")
    exchange: Optional[str] = Field(description="The exchange of the stock.")


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
    def extract_data(
        query: FMPMarketSnapshotsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""

        api_key = credentials.get("fmp_api_key") if credentials else ""
        url = f"https://financialmodelingprep.com/api/v3/quotes/{query.market}?apikey={api_key}"
        response = make_request(url)

        if response.status_code != 200:
            raise RuntimeError(
                f"Error fetching data from FMP  -> {response.status_code}"
            )
        data = pd.DataFrame(response.json())
        data = data.drop(columns=["timestamp", "earningsAnnouncement"]).fillna(0)
        data = data[data["price"] > 0.01]
        data["name"] = data["name"].replace(0, "")
        return data.sort_values(by="changesPercentage", ascending=False).to_dict(
            orient="records"
        )

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPMarketSnapshotsData]:
        """Return the transformed data."""
        return [FMPMarketSnapshotsData.parse_obj(d) for d in data]
