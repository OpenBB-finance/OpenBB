"""BMO ETF Holdings fetcher."""

from datetime import date as dateType
from typing import Any, Dict, List, Optional

from openbb_bmo.utils.helpers import (
    get_fund_properties,
)
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.etf_holdings import (
    EtfHoldingsData,
    EtfHoldingsQueryParams,
)
from pydantic import Field


class BmoEtfHoldingsQueryParams(EtfHoldingsQueryParams):
    """Bmo ETF Holdings query.

    Source: https://www.bmogam.com/
    """


class BmoEtfHoldingsData(EtfHoldingsData):
    """Bmo ETF Holdings Data."""

    symbol: Optional[str] = Field(
        description="The ticker symbol of the asset.",
        default=None,
        alias="bloomberg_ticker",
    )
    name: Optional[str] = Field(
        description="The name of the asset.", default=None, alias="holding_name"
    )
    label: Optional[str] = Field(description="The label of the asset.", default=None)
    isin: Optional[str] = Field(description="The ISIN of the asset.", default=None)
    asset_group: Optional[str] = Field(
        description="The type of asset.",
        default=None,
    )
    weight: Optional[float] = Field(
        description="The weight of the asset in the portfolio.",
        default=None,
    )
    shares: Optional[float] = Field(
        description="The number of shares or contracts of the asset held.",
        alias="number_of_share_held",
        default=None,
    )
    currency: Optional[str] = Field(
        description="The currency of the asset.",
        default=None,
    )
    market_value: Optional[float] = Field(
        description="The market value of the holding.",
        default=None,
        alias="base_market_value",
    )
    value: Optional[float] = Field(
        description="The value of the holding.",
        default=None,
    )
    par_value: Optional[float] = Field(
        description="The par value of the holding.",
        default=None,
    )
    income_rate: Optional[float] = Field(
        description="The income rate of the holding.",
        default=None,
    )
    maturity_date: Optional[dateType] = Field(
        description="The maturity date of the holding.",
        default=None,
    )
    sector: Optional[str] = Field(
        description="The sector of the asset.", default=None, alias="major_sector"
    )
    holdings_date: Optional[dateType] = Field(
        description="The date of the holdings.", default=None, alias="as_of_date"
    )


class BmoEtfHoldingsFetcher(
    Fetcher[
        BmoEtfHoldingsQueryParams,
        List[BmoEtfHoldingsData],
    ]
):
    """Transform the query, extract and transform the data from the Bmo endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BmoEtfHoldingsQueryParams:
        """Transform the query."""
        return BmoEtfHoldingsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BmoEtfHoldingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the BMO endpoint."""

        symbol = query.symbol.upper()
        symbol = symbol.replace(".TO", "").replace(".TSX", "").replace("-", ".")  # noqa
        results = []
        data = get_fund_properties(symbol, query)
        if len(data) == 1:
            data = data[0]
        if "allocations" in data:
            key = -1
            # Find the correct position in the data for the holdings data.
            for i in range(0, len(data["allocations"])):
                if data["allocations"][i]["code"] == "holdings":
                    key = i
            if key != -1:
                try:
                    results = data["allocations"][key]["values"]
                except Exception as e:
                    raise RuntimeError(e)
        return results

    @staticmethod
    def transform_data(
        data: List[Dict],
    ) -> List[BmoEtfHoldingsData]:
        """Transform the data."""
        return [BmoEtfHoldingsData.model_validate(d) for d in data]
