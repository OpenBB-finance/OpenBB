"""FMP Stock Insider Trading fetcher."""


from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import create_url, get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_insider_trading import (
    StockInsiderTradingData,
    StockInsiderTradingQueryParams,
)


class FMPStockInsiderTradingQueryParams(StockInsiderTradingQueryParams):
    """FMP Stock Insider Trading Query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Stock-Insider-Trading
    """


class FMPStockInsiderTradingData(StockInsiderTradingData):
    """FMP Stock Insider Trading Data."""


class FMPStockInsiderTradingFetcher(
    Fetcher[
        FMPStockInsiderTradingQueryParams,
        List[FMPStockInsiderTradingData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPStockInsiderTradingQueryParams:
        """Transform the query params."""
        return FMPStockInsiderTradingQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPStockInsiderTradingQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        # This changes the actual type of a pydantic class, but its a quick and clean way to format properly
        query.transactionType = ",".join(query.transactionType)  # type: ignore
        url = create_url(4, "insider-trading", api_key, query)

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPStockInsiderTradingData]:
        """Return the transformed data."""
        return [FMPStockInsiderTradingData.parse_obj(d) for d in data]
