"""FMP Stock Multiples Fetcher."""


from typing import Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer
from openbb_provider.models.stock_multiples import (
    StockMultiplesData,
    StockMultiplesQueryParams,
)


from pydantic import Field

from openbb_fmp.utils.helpers import create_url, get_data_one


class FMPStockMultiplesQueryParams(StockMultiplesQueryParams):
    """FMP Stock Multiples QueryParams.

    Source: https://site.financialmodelingprep.com/developer/docs/#Company-Key-Metrics

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    limit : Optional[int]
        The limit of the key metrics ttm to be returned.
    """


class FMPStockMultiplesData(StockMultiplesData):
    """FMP Stock Multiples Data."""

    revenuePerShareTTM: Optional[float] = Field(alias="revenue_per_share_ttm")
    netIncomePerShareTTM: Optional[float] = Field(alias="net_income_per_share_ttm")
    operatingCashFlowPerShareTTM: Optional[float] = Field(
        alias="operating_cash_flow_per_share_ttm"
    )
    freeCashFlowPerShareTTM: Optional[float] = Field(
        alias="free_cash_flow_per_share_ttm"
    )
    cashPerShareTTM: Optional[float] = Field(alias="cash_per_share_ttm")
    bookValuePerShareTTM: Optional[float] = Field(alias="book_value_per_share_ttm")
    tangibleBookValuePerShareTTM: Optional[float] = Field(
        alias="tangible_book_value_per_share_ttm"
    )
    shareholdersEquityPerShareTTM: Optional[float] = Field(
        alias="shareholders_equity_per_share_ttm"
    )
    interestDebtPerShareTTM: Optional[float] = Field(
        alias="interest_debt_per_share_ttm"
    )
    marketCapTTM: Optional[float] = Field(alias="market_cap_ttm")
    enterpriseValueTTM: Optional[float] = Field(alias="enterprise_value_ttm")
    peRatioTTM: Optional[float] = Field(alias="pe_ratio_ttm")
    priceToSalesRatioTTM: Optional[float] = Field(alias="price_to_sales_ratio_ttm")
    pocfratioTTM: Optional[float] = Field(alias="pocf_ratio_ttm")
    pfcfRatioTTM: Optional[float] = Field(alias="pfcf_ratio_ttm")
    pbRatioTTM: Optional[float] = Field(alias="pb_ratio_ttm")
    ptbRatioTTM: Optional[float] = Field(alias="ptb_ratio_ttm")
    evToSalesTTM: Optional[float] = Field(alias="ev_to_sales_ttm")
    enterpriseValueOverEBITDATTM: Optional[float] = Field(
        alias="enterprise_value_over_ebitda_ttm"
    )
    evToOperatingCashFlowTTM: Optional[float] = Field(
        alias="ev_to_operating_cash_flow_ttm"
    )
    evToFreeCashFlowTTM: Optional[float] = Field(alias="ev_to_free_cash_flow_ttm")
    earningsYieldTTM: Optional[float] = Field(alias="earnings_yield_ttm")
    freeCashFlowYieldTTM: Optional[Optional[float]] = Field(
        alias="free_cash_flow_yield_ttm"
    )
    debtToEquityTTM: Optional[float] = Field(alias="debt_to_equity_ttm")
    debtToAssetsTTM: Optional[float] = Field(alias="debt_to_assets_ttm")
    netDebtToEBITDATTM: Optional[float] = Field(alias="net_debt_to_ebitda_ttm")
    currentRatioTTM: Optional[float] = Field(alias="current_ratio_ttm")
    interestCoverageTTM: Optional[float] = Field(alias="interest_coverage_ttm")
    incomeQualityTTM: Optional[float] = Field(alias="income_quality_ttm")
    dividendYieldTTM: Optional[Optional[float]] = Field(alias="dividend_yield_ttm")
    payoutRatioTTM: Optional[Optional[float]] = Field(alias="payout_ratio_ttm")
    salesGeneralAndAdministrativeToRevenueTTM: Optional[float] = Field(
        alias="sales_general_and_administrative_to_revenue_ttm"
    )
    researchAndDevelopementToRevenueTTM: Optional[float] = Field(
        alias="research_and_development_to_revenue_ttm"
    )
    intangiblesToTotalAssetsTTM: Optional[float] = Field(
        alias="intangibles_to_total_assets_ttm"
    )
    capexToOperatingCashFlowTTM: Optional[float] = Field(
        alias="capex_to_operating_cash_flow_ttm"
    )
    capexToRevenueTTM: Optional[float] = Field(alias="capex_to_revenue_ttm")
    capexToDepreciationTTM: Optional[float] = Field(alias="capex_to_depreciation_ttm")
    stockBasedCompensationToRevenueTTM: Optional[float] = Field(
        alias="stock_based_compensation_to_revenue_ttm"
    )
    grahamNumberTTM: Optional[float] = Field(alias="graham_number_ttm")
    roicTTM: Optional[float] = Field(alias="roic_ttm")
    returnOnTangibleAssetsTTM: Optional[float] = Field(
        alias="return_on_tangible_assets_ttm"
    )
    grahamNetNetTTM: Optional[float] = Field(alias="graham_net_net_ttm")
    workingCapitalTTM: Optional[float] = Field(alias="working_capital_ttm")
    tangibleAssetValueTTM: Optional[float] = Field(alias="tangible_asset_value_ttm")
    netCurrentAssetValueTTM: Optional[float] = Field(
        alias="net_current_asset_value_ttm"
    )
    investedCapitalTTM: Optional[float] = Field(alias="invested_capital_ttm")
    averageReceivablesTTM: Optional[float] = Field(alias="average_receivables_ttm")
    averagePayablesTTM: Optional[float] = Field(alias="average_payables_ttm")
    averageInventoryTTM: Optional[float] = Field(alias="average_inventory_ttm")
    daysSalesOutstandingTTM: Optional[float] = Field(alias="days_sales_outstanding_ttm")
    daysPayablesOutstandingTTM: Optional[float] = Field(
        alias="days_payables_outstanding_ttm"
    )
    daysOfInventoryOnHandTTM: Optional[float] = Field(
        alias="days_of_inventory_on_hand_ttm"
    )
    receivablesTurnoverTTM: Optional[float] = Field(alias="receivables_turnover_ttm")
    payablesTurnoverTTM: Optional[float] = Field(alias="payables_turnover_ttm")
    inventoryTurnoverTTM: Optional[float] = Field(alias="inventory_turnover_ttm")
    roeTTM: Optional[float] = Field(alias="roe_ttm")
    capexPerShareTTM: Optional[float] = Field(alias="capex_per_share_ttm")


class FMPStockMultiplesFetcher(
    Fetcher[
        StockMultiplesQueryParams,
        StockMultiplesData,
        FMPStockMultiplesQueryParams,
        FMPStockMultiplesData,
    ]
):
    @staticmethod
    def transform_query(
        query: StockMultiplesQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPStockMultiplesQueryParams:
        return FMPStockMultiplesQueryParams(
            symbol=query.symbol, limit=query.limit, **extra_params or {}
        )

    @staticmethod
    def extract_data(
        query: FMPStockMultiplesQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPStockMultiplesData]:
        if credentials:
            api_key = credentials.get("fmp_api_key")

        url = create_url(
            3, f"key-metrics-ttm/{query.symbol}", api_key, query, exclude=["symbol"]
        )
        return get_data_one(url, FMPStockMultiplesData)

    @staticmethod
    def transform_data(data: List[FMPStockMultiplesData]) -> List[StockMultiplesData]:
        return data_transformer(data, StockMultiplesData)
