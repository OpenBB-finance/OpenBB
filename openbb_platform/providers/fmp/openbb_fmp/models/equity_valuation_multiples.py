"""FMP Equity Valuation Multiples Model."""

# pylint: disable=unused-argument

import asyncio
from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_valuation_multiples import (
    EquityValuationMultiplesData,
    EquityValuationMultiplesQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from openbb_fmp.utils.helpers import create_url, response_callback


class FMPEquityValuationMultiplesQueryParams(EquityValuationMultiplesQueryParams):
    """FMP Equity Valuation Multiples Query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Company-Key-Metrics
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


class FMPEquityValuationMultiplesData(EquityValuationMultiplesData):
    """FMP Equity Valuation Multiples Data."""

    __alias_dict__ = {
        "revenue_per_share_ttm": "revenuePerShareTTM",
        "net_income_per_share_ttm": "netIncomePerShareTTM",
        "operating_cash_flow_per_share_ttm": "operatingCashFlowPerShareTTM",
        "free_cash_flow_per_share_ttm": "freeCashFlowPerShareTTM",
        "cash_per_share_ttm": "cashPerShareTTM",
        "book_value_per_share_ttm": "bookValuePerShareTTM",
        "tangible_book_value_per_share_ttm": "tangibleBookValuePerShareTTM",
        "shareholders_equity_per_share_ttm": "shareholdersEquityPerShareTTM",
        "interest_debt_per_share_ttm": "interestDebtPerShareTTM",
        "market_cap_ttm": "marketCapTTM",
        "enterprise_value_ttm": "enterpriseValueTTM",
        "pe_ratio_ttm": "peRatioTTM",
        "price_to_sales_ratio_ttm": "priceToSalesRatioTTM",
        "pocf_ratio_ttm": "pocfratioTTM",
        "pfcf_ratio_ttm": "pfcfRatioTTM",
        "pb_ratio_ttm": "pbRatioTTM",
        "ptb_ratio_ttm": "ptbRatioTTM",
        "ev_to_sales_ttm": "evToSalesTTM",
        "enterprise_value_over_ebitda_ttm": "enterpriseValueOverEBITDATTM",
        "ev_to_operating_cash_flow_ttm": "evToOperatingCashFlowTTM",
        "ev_to_free_cash_flow_ttm": "evToFreeCashFlowTTM",
        "earnings_yield_ttm": "earningsYieldTTM",
        "free_cash_flow_yield_ttm": "freeCashFlowYieldTTM",
        "debt_to_equity_ttm": "debtToEquityTTM",
        "debt_to_assets_ttm": "debtToAssetsTTM",
        "debt_to_market_cap_ttm": "debtToMarketCapTTM",
        "net_debt_to_ebitda_ttm": "netDebtToEBITDATTM",
        "current_ratio_ttm": "currentRatioTTM",
        "interest_coverage_ttm": "interestCoverageTTM",
        "income_quality_ttm": "incomeQualityTTM",
        "dividend_yield_ttm": "dividendYieldTTM",
        "payout_ratio_ttm": "payoutRatioTTM",
        "sales_general_and_administrative_to_revenue_ttm": "salesGeneralAndAdministrativeToRevenueTTM",
        "research_and_development_to_revenue_ttm": "researchAndDevelopementToRevenueTTM",
        "intangibles_to_total_assets_ttm": "intangiblesToTotalAssetsTTM",
        "capex_to_operating_cash_flow_ttm": "capexToOperatingCashFlowTTM",
        "capex_to_revenue_ttm": "capexToRevenueTTM",
        "capex_to_depreciation_ttm": "capexToDepreciationTTM",
        "stock_based_compensation_to_revenue_ttm": "stockBasedCompensationToRevenueTTM",
        "graham_number_ttm": "grahamNumberTTM",
        "roic_ttm": "roicTTM",
        "return_on_tangible_assets_ttm": "returnOnTangibleAssetsTTM",
        "graham_net_net_ttm": "grahamNetNetTTM",
        "working_capital_ttm": "workingCapitalTTM",
        "tangible_asset_value_ttm": "tangibleAssetValueTTM",
        "net_current_asset_value_ttm": "netCurrentAssetValueTTM",
        "invested_capital_ttm": "investedCapitalTTM",
        "average_receivables_ttm": "averageReceivablesTTM",
        "average_payables_ttm": "averagePayablesTTM",
        "average_inventory_ttm": "averageInventoryTTM",
        "days_sales_outstanding_ttm": "daysSalesOutstandingTTM",
        "days_payables_outstanding_ttm": "daysPayablesOutstandingTTM",
        "days_of_inventory_on_hand_ttm": "daysOfInventoryOnHandTTM",
        "receivables_turnover_ttm": "receivablesTurnoverTTM",
        "payables_turnover_ttm": "payablesTurnoverTTM",
        "inventory_turnover_ttm": "inventoryTurnoverTTM",
        "roe_ttm": "roeTTM",
        "capex_per_share_ttm": "capexPerShareTTM",
        "dividend_yield_percentage_ttm": "dividendYieldPercentageTTM",
        "dividend_to_market_cap_ttm": "debtToMarketCapTTM",
        "dividend_per_share_ttm": "dividendPerShareTTM",
    }


class FMPEquityValuationMultiplesFetcher(
    Fetcher[
        FMPEquityValuationMultiplesQueryParams,
        List[FMPEquityValuationMultiplesData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> FMPEquityValuationMultiplesQueryParams:
        """Transform the query params."""
        return FMPEquityValuationMultiplesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPEquityValuationMultiplesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        symbols = query.symbol.split(",")

        results = []

        async def get_one(symbol):
            """Get data for one symbol."""
            url = create_url(
                3, f"key-metrics-ttm/{symbol}", api_key, query, exclude=["symbol"]
            )
            result = await amake_request(
                url, response_callback=response_callback, **kwargs
            )
            if not result:
                warn(f"Symbol Error: No data found for {symbol}.")
            if result:
                data = [{**d, "symbol": symbol} for d in result]
                results.extend(data)

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        if not results:
            raise EmptyDataError("No data found for given symbols.")

        return results

    @staticmethod
    def transform_data(
        query: FMPEquityValuationMultiplesQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FMPEquityValuationMultiplesData]:
        """Return the transformed data."""
        return [FMPEquityValuationMultiplesData.model_validate(d) for d in data]
