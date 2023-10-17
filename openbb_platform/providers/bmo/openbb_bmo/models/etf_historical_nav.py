"""BMO ETF Historical NAV fetcher."""

from typing import Any, Dict, List, Optional

from openbb_bmo.utils.helpers import get_fund_properties
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_historical_nav import (
    EtfHistoricalNavData,
    EtfHistoricalNavQueryParams,
)
from pydantic import Field


class BmoEtfHistoricalNavQueryParams(EtfHistoricalNavQueryParams):
    """BMO ETF Historical NAV query.

    Source: https://www.bmogam.com/
    """


class BmoEtfHistoricalNavData(EtfHistoricalNavData):
    """Bmo ETF Historical NAV Data."""

    __alias_dict__ = {
        "nav": "net_asset_value",
    }

    net_assets: Optional[float] = Field(
        description="The net assets of the fund.", default=None
    )
    market_price: Optional[float] = Field(
        description="The closing market price of the fund.", default=None
    )
    index_value: Optional[float] = Field(
        description="The value of the tracking index.", default=None
    )
    fund_1_day_growth: Optional[float] = Field(
        description="The 1-day growth of the fund.", default=None
    )
    index_1_day_growth: Optional[float] = Field(
        description="The 1-day growth of the tracking index.", default=None
    )
    shares_outstanding: Optional[float] = Field(
        description="The number of shares outstanding.", default=None
    )


class BmoEtfHistoricalNavFetcher(
    Fetcher[
        BmoEtfHistoricalNavQueryParams,
        List[BmoEtfHistoricalNavData],
    ]
):
    """Transform the query, extract and transform the data from the BMO endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BmoEtfHistoricalNavQueryParams:
        """Transform the query."""
        return BmoEtfHistoricalNavQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BmoEtfHistoricalNavQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the BMO endpoint."""

        symbol = query.symbol.upper()
        symbol = symbol.replace(".TO", "").replace(".TSX", "").replace("-", ".")  # noqa
        results = []

        data = get_fund_properties(symbol)

        if isinstance(data, List) and len(data) == 1 and "timeseries" in data[0]:
            key = -1
            # Find the correct position in the data for the historical NAV.
            for i in range(0, len(data[0]["timeseries"])):
                if data[0]["timeseries"][i]["code"] == "prices":
                    key = i
            if key != -1:
                results = data[0]["timeseries"][key]["values"]

        return results

    @staticmethod
    def transform_data(
        data: List[Dict],
        **kwargs: Any,
    ) -> List[BmoEtfHistoricalNavData]:
        """Transform the data."""
        return [BmoEtfHistoricalNavData.model_validate(d) for d in data]
