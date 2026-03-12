"""SEC Cash Flow Statement Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cash_flow import (
    CashFlowStatementData,
    CashFlowStatementQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


class SecCashFlowQueryParams(CashFlowStatementQueryParams):
    """SEC Cash Flow Statement Query.

    Source: https://data.sec.gov/api/xbrl/companyfacts/

    Uses the SEC EDGAR Company Facts API to extract cash flow data
    from XBRL filings (10-K and 10-Q). Quarterly values are derived from
    cumulative YTD figures reported in 10-Q filings.

    Note: Optimized for commercial/industrial US-GAAP filers. Financial sector
    companies (banks, insurance) use different XBRL concepts and may return
    sparse results.
    """

    period: Literal["annual", "quarter"] = Field(
        default="annual",
        description="Time period of the data to return. 'annual' for 10-K filings, 'quarter' for 10-Q filings.",
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use cache for the SEC API request. Defaults to True.",
    )


class SecCashFlowData(CashFlowStatementData):
    """SEC Cash Flow Statement Data."""

    __alias_dict__: dict[str, str] = {}

    filing_date: dateType | None = Field(
        default=None,
        description="The date the filing was submitted to the SEC.",
    )
    cik: str | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("cik", ""),
    )
    entity_name: str | None = Field(
        default=None,
        description="The entity name associated with the CIK.",
    )
    # Operating activities
    net_income: float | None = Field(
        default=None,
        description="Net income.",
    )
    depreciation_and_amortization: float | None = Field(
        default=None,
        description="Depreciation and amortization.",
    )
    stock_based_compensation: float | None = Field(
        default=None,
        description="Stock-based compensation expense.",
    )
    deferred_income_tax: float | None = Field(
        default=None,
        description="Deferred income tax expense (benefit).",
    )
    change_in_working_capital: float | None = Field(
        default=None,
        description="Change in operating capital.",
    )
    change_in_accounts_receivable: float | None = Field(
        default=None,
        description="Change in accounts receivable.",
    )
    change_in_inventory: float | None = Field(
        default=None,
        description="Change in inventory.",
    )
    change_in_accounts_payable: float | None = Field(
        default=None,
        description="Change in accounts payable.",
    )
    other_operating_activities: float | None = Field(
        default=None,
        description="Other operating activities.",
    )
    operating_cash_flow: float | None = Field(
        default=None,
        description="Net cash from operating activities.",
    )
    # Investing activities
    capital_expenditure: float | None = Field(
        default=None,
        description="Capital expenditure (payments for property, plant, and equipment).",
    )
    acquisitions: float | None = Field(
        default=None,
        description="Payments for acquisitions, net of cash acquired.",
    )
    purchase_of_investments: float | None = Field(
        default=None,
        description="Purchases of investments and marketable securities.",
    )
    sale_of_investments: float | None = Field(
        default=None,
        description="Proceeds from sales and maturities of investments.",
    )
    other_investing_activities: float | None = Field(
        default=None,
        description="Other investing activities.",
    )
    investing_cash_flow: float | None = Field(
        default=None,
        description="Net cash from investing activities.",
    )
    # Financing activities
    debt_issuance: float | None = Field(
        default=None,
        description="Proceeds from issuance of debt.",
    )
    debt_repayment: float | None = Field(
        default=None,
        description="Repayments of debt.",
    )
    dividends_paid: float | None = Field(
        default=None,
        description="Dividends paid to common stockholders.",
    )
    share_repurchases: float | None = Field(
        default=None,
        description="Payments for repurchase of common stock.",
    )
    other_financing_activities: float | None = Field(
        default=None,
        description="Other financing activities.",
    )
    financing_cash_flow: float | None = Field(
        default=None,
        description="Net cash from financing activities.",
    )
    # Other
    effect_of_exchange_rate: float | None = Field(
        default=None,
        description="Effect of exchange rate changes on cash.",
    )
    net_change_in_cash: float | None = Field(
        default=None,
        description="Net change in cash and cash equivalents.",
    )
    free_cash_flow: float | None = Field(
        default=None,
        description="Free cash flow (operating cash flow minus capital expenditure).",
    )

    @field_validator("period_ending", mode="before", check_fields=False)
    @classmethod
    def parse_period_ending(cls, v: Any) -> dateType:
        """Parse period_ending to date."""
        if isinstance(v, str):
            return dateType.fromisoformat(v)
        return v

    @field_validator("filing_date", mode="before", check_fields=False)
    @classmethod
    def parse_filing_date(cls, v: Any) -> dateType | None:
        """Parse filing_date to date."""
        if isinstance(v, str):
            return dateType.fromisoformat(v)
        return v

    @field_validator("cik", mode="before", check_fields=False)
    @classmethod
    def parse_cik(cls, v: Any) -> str | None:
        """Ensure CIK is a string."""
        if v is not None:
            return str(v)
        return v


class SecCashFlowFetcher(Fetcher[SecCashFlowQueryParams, list[SecCashFlowData]]):
    """SEC Cash Flow Statement Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecCashFlowQueryParams:
        """Transform the query."""
        return SecCashFlowQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecCashFlowQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the SEC company facts endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_sec.utils.company_facts import (
            extract_duration_data,
            get_company_facts,
            load_taxonomy,
        )

        taxonomy_map = load_taxonomy("cash_flow")
        company_facts = await get_company_facts(
            symbol=query.symbol,
            use_cache=query.use_cache,
        )
        if not company_facts:
            raise EmptyDataError(f"No company facts found for symbol: {query.symbol}")

        results = extract_duration_data(
            company_facts, taxonomy_map, period=query.period
        )
        if not results:
            raise EmptyDataError(
                f"No cash flow data could be extracted for symbol: {query.symbol}"
            )

        return results

    @staticmethod
    def transform_data(
        query: SecCashFlowQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[SecCashFlowData]:
        """Transform the data and validate the model."""
        if not data:
            raise EmptyDataError("The request was returned empty.")

        if query.limit is not None:
            data = data[: query.limit]

        return [SecCashFlowData.model_validate(d) for d in data]
