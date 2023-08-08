"""FMP Stock Insider Trading fetcher."""


from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.stock_insider_trading import (
    StockInsiderTradingData,
    StockInsiderTradingQueryParams,
)

from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPStockInsiderTradingQueryParams(StockInsiderTradingQueryParams):
    """FMP Stock Insider Trading Query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Stock-Insider-Trading
    """


class FMPStockInsiderTradingData(StockInsiderTradingData):
    """FMP Stock Insider Trading Data."""

    class Config:
        fields = {
            "filing_date": "filingDate",
            "transaction_date": "transactionDate",
            "reporting_cik": "reportingCik",
            "transaction_type": "transactionType",
            "securities_owned": "securitiesOwned",
            "company_cik": "companyCik",
            "reporting_name": "reportingName",
            "type_of_owner": "typeOfOwner",
            "acquistion_or_disposition": "acquistionOrDisposition",
            "form_type": "formType",
            "securities_transacted": "securitiesTransacted",
            "security_name": "securityName",
            "investors_holding": "investorsHolding",
            "last_number_of_13f_shares": "lastNumberOf13FShares",
            "total_invested": "totalInvested",
            "ownership_percent": "ownershipPercent",
            "new_positions": "newPositions",
            "increased_positions": "increasedPositions",
            "closed_positions": "closedPositions",
            "reduced_positions": "reducedPositions",
            "total_calls": "totalCalls",
            "total_puts": "totalPuts",
            "put_call_ratio": "putCallRatio",
        }


class FMPStockInsiderTradingFetcher(
    Fetcher[
        FMPStockInsiderTradingQueryParams,
        List[FMPStockInsiderTradingData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPStockInsiderTradingQueryParams:
        return FMPStockInsiderTradingQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPStockInsiderTradingQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> List[FMPStockInsiderTradingData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        # This changes the actual type of a pydantic class, but its a quick and clean way to format properly
        query.transactionType = ",".join(query.transactionType)  # type: ignore
        url = create_url(4, "insider-trading", api_key, query)

        return get_data_many(url, FMPStockInsiderTradingData, **kwargs)

    @staticmethod
    def transform_data(
        data: List[FMPStockInsiderTradingData],
    ) -> List[FMPStockInsiderTradingData]:
        return data
        return data
