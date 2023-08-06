"""FMP Stock Ownership fetcher."""


from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.stock_ownership import (
    StockOwnershipData,
    StockOwnershipQueryParams,
)

from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPStockOwnershipQueryParams(StockOwnershipQueryParams):
    """FMP Stock Ownership query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Stock-Ownership-by-Holders
    """


class FMPStockOwnershipData(StockOwnershipData):
    """FMP Stock Ownership Data."""

    class Config:
        fields = {
            "filing_date": "filingDate",
            "investor_name": "investorName",
            "security_name": "securityName",
            "type_of_security": "typeOfSecurity",
            "security_cusip": "securityCusip",
            "shares_type": "sharesType",
            "put_call_share": "putCallShare",
            "investment_discretion": "investmentDiscretion",
            "industry_title": "industryTitle",
            "last_weight": "lastWeight",
            "change_in_weight": "changeInWeight",
            "change_in_weight_percentage": "changeInWeightPercentage",
            "market_value": "marketValue",
            "last_market_value": "lastMarketValue",
            "change_in_market_value": "changeInMarketValue",
            "change_in_market_value_percentage": "changeInMarketValuePercentage",
            "shares_number": "sharesNumber",
            "last_shares_number": "lastSharesNumber",
            "change_in_shares_number": "changeInSharesNumber",
            "change_in_shares_number_percentage": "changeInSharesNumberPercentage",
            "quarter_end_price": "quarterEndPrice",
            "avg_price_paid": "avgPricePaid",
            "is_new": "isNew",
            "is_sold_out": "isSoldOut",
            "last_ownership": "lastOwnership",
            "change_in_ownership": "changeInOwnership",
            "change_in_ownership_percentage": "changeInOwnershipPercentage",
            "holding_period": "holdingPeriod",
            "first_added": "firstAdded",
            "performance_percentage": "performancePercentage",
            "last_performance": "lastPerformance",
            "change_in_performance": "changeInPerformance",
            "is_counted_for_performance": "isCountedForPerformance",
        }


class FMPStockOwnershipFetcher(
    Fetcher[
        StockOwnershipQueryParams,
        List[StockOwnershipData],
        StockOwnershipQueryParams,
        List[FMPStockOwnershipData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPStockOwnershipQueryParams:
        return FMPStockOwnershipQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPStockOwnershipQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[FMPStockOwnershipData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            4,
            "institutional-ownership/institutional-holders/symbol-ownership-percent",
            api_key,
            query,
        )

        sorted_data = get_data_many(url, FMPStockOwnershipData, **kwargs)
        sorted_data.sort(key=lambda x: x.filing_date, reverse=True)

        return sorted_data

    @staticmethod
    def transform_data(data: List[FMPStockOwnershipData]) -> List[StockOwnershipData]:
        return [StockOwnershipData.parse_obj(d.dict()) for d in data]
