"""FMP Stock Insider Trading fetcher."""


from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_insider_trading import (
    StockInsiderTradingData,
    StockInsiderTradingQueryParams,
)
from openbb_provider.utils.helpers import get_querystring


class FMPStockInsiderTradingQueryParams(StockInsiderTradingQueryParams):
    """FMP Stock Insider Trading Query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Stock-Insider-Trading
    """

    __alias_dict__ = {
        "transaction_type": "transactionType",
    }


class FMPStockInsiderTradingData(StockInsiderTradingData):
    """FMP Stock Insider Trading Data."""

    __alias_dict__ = {
        "acquisition_or_disposition": "acquistionOrDisposition",
        "last_number_of_13f_shares": "lastNumberOf13FShares",
    }


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

        base_url = "https://financialmodelingprep.com/api/v4/insider-trading"
        query_str = get_querystring(query.model_dump(by_alias=True), ["page"])

        data: List[Dict] = []

        limit_reached = 0
        page = 0

        while limit_reached <= query.limit:
            url = f"{base_url}?{query_str}&page={page}&apikey={api_key}"
            data.extend(get_data_many(url, **kwargs))
            limit_reached += len(data)
            page += 1

        return data[: query.limit]

    @staticmethod
    def transform_data(
        query: FMPStockInsiderTradingQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPStockInsiderTradingData]:
        """Return the transformed data."""
        data = sorted(data, key=lambda x: x["filingDate"], reverse=True)
        return [FMPStockInsiderTradingData.model_validate(d) for d in data]
