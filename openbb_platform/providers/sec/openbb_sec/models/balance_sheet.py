"""SEC Balance Sheet Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.balance_sheet import (
    BalanceSheetData,
    BalanceSheetQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


class SecBalanceSheetQueryParams(BalanceSheetQueryParams):
    """SEC Balance Sheet Query.

    Source: https://data.sec.gov/api/xbrl/companyfacts/

    Uses the SEC EDGAR Company Facts API to extract balance sheet data
    from XBRL filings (10-K and 10-Q). A hierarchical taxonomy mapping
    resolves standardized line items from XBRL concepts using a try_order
    fallback approach.

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


class SecBalanceSheetData(BalanceSheetData):
    """SEC Balance Sheet Data."""

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
    # Assets
    cash_and_cash_equivalents: float | None = Field(
        default=None,
        description="Cash and cash equivalents.",
    )
    short_term_investments: float | None = Field(
        default=None,
        description="Short term investments.",
    )
    cash_and_short_term_investments: float | None = Field(
        default=None,
        description="Cash and short term investments.",
    )
    accounts_receivable: float | None = Field(
        default=None,
        description="Accounts receivable, net.",
    )
    inventory: float | None = Field(
        default=None,
        description="Inventory, net.",
    )
    prepaid_expenses: float | None = Field(
        default=None,
        description="Prepaid expenses and other current assets.",
    )
    other_current_assets: float | None = Field(
        default=None,
        description="Other current assets.",
    )
    total_current_assets: float | None = Field(
        default=None,
        description="Total current assets.",
    )
    property_plant_equipment_net: float | None = Field(
        default=None,
        description="Property, plant, and equipment, net.",
    )
    property_plant_equipment_gross: float | None = Field(
        default=None,
        description="Property, plant, and equipment, gross.",
    )
    accumulated_depreciation: float | None = Field(
        default=None,
        description="Accumulated depreciation, depletion, and amortization.",
    )
    goodwill: float | None = Field(
        default=None,
        description="Goodwill.",
    )
    intangible_assets: float | None = Field(
        default=None,
        description="Intangible assets, net.",
    )
    goodwill_and_intangible_assets: float | None = Field(
        default=None,
        description="Goodwill and intangible assets.",
    )
    long_term_investments: float | None = Field(
        default=None,
        description="Long term investments.",
    )
    tax_assets: float | None = Field(
        default=None,
        description="Deferred tax assets.",
    )
    other_non_current_assets: float | None = Field(
        default=None,
        description="Other non-current assets.",
    )
    total_non_current_assets: float | None = Field(
        default=None,
        description="Total non-current assets.",
    )
    total_assets: float | None = Field(
        default=None,
        description="Total assets.",
    )
    operating_lease_right_of_use_asset: float | None = Field(
        default=None,
        description="Operating lease right-of-use asset.",
    )
    # Liabilities
    accounts_payable: float | None = Field(
        default=None,
        description="Accounts payable.",
    )
    short_term_debt: float | None = Field(
        default=None,
        description="Short term borrowings.",
    )
    current_portion_of_long_term_debt: float | None = Field(
        default=None,
        description="Current portion of long term debt.",
    )
    tax_payables: float | None = Field(
        default=None,
        description="Tax payables.",
    )
    deferred_revenue_current: float | None = Field(
        default=None,
        description="Deferred revenue, current.",
    )
    accrued_liabilities: float | None = Field(
        default=None,
        description="Accrued liabilities.",
    )
    other_current_liabilities: float | None = Field(
        default=None,
        description="Other current liabilities.",
    )
    total_current_liabilities: float | None = Field(
        default=None,
        description="Total current liabilities.",
    )
    long_term_debt: float | None = Field(
        default=None,
        description="Long term debt, non-current.",
    )
    deferred_revenue_non_current: float | None = Field(
        default=None,
        description="Deferred revenue, non-current.",
    )
    deferred_tax_liabilities: float | None = Field(
        default=None,
        description="Deferred tax liabilities.",
    )
    operating_lease_liability_current: float | None = Field(
        default=None,
        description="Operating lease liability, current.",
    )
    operating_lease_liability_non_current: float | None = Field(
        default=None,
        description="Operating lease liability, non-current.",
    )
    other_non_current_liabilities: float | None = Field(
        default=None,
        description="Other non-current liabilities.",
    )
    total_non_current_liabilities: float | None = Field(
        default=None,
        description="Total non-current liabilities.",
    )
    total_liabilities: float | None = Field(
        default=None,
        description="Total liabilities.",
    )
    # Equity
    common_stock: float | None = Field(
        default=None,
        description="Common stock, including additional paid-in capital.",
    )
    preferred_stock: float | None = Field(
        default=None,
        description="Preferred stock value.",
    )
    retained_earnings: float | None = Field(
        default=None,
        description="Retained earnings (accumulated deficit).",
    )
    accumulated_other_comprehensive_income: float | None = Field(
        default=None,
        description="Accumulated other comprehensive income (loss), net of tax.",
    )
    treasury_stock: float | None = Field(
        default=None,
        description="Treasury stock value.",
    )
    minority_interest: float | None = Field(
        default=None,
        description="Minority (non-controlling) interest.",
    )
    total_stockholders_equity: float | None = Field(
        default=None,
        description="Total stockholders' equity.",
    )
    total_equity: float | None = Field(
        default=None,
        description="Total equity, including non-controlling interest.",
    )
    total_liabilities_and_equity: float | None = Field(
        default=None,
        description="Total liabilities and stockholders' equity.",
    )
    # Derived
    total_debt: float | None = Field(
        default=None,
        description="Total debt (short term + current LTD + long term).",
    )
    net_debt: float | None = Field(
        default=None,
        description="Net debt (total debt minus cash and equivalents).",
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


class SecBalanceSheetFetcher(
    Fetcher[SecBalanceSheetQueryParams, list[SecBalanceSheetData]]
):
    """SEC Balance Sheet Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecBalanceSheetQueryParams:
        """Transform the query."""
        return SecBalanceSheetQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecBalanceSheetQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the SEC company facts endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_sec.utils.company_facts import (
            extract_balance_sheet_data,
            get_company_facts,
            load_taxonomy,
        )

        taxonomy_map = load_taxonomy("balance_sheet")
        company_facts = await get_company_facts(
            symbol=query.symbol,
            use_cache=query.use_cache,
        )
        if not company_facts:
            raise EmptyDataError(f"No company facts found for symbol: {query.symbol}")

        results = extract_balance_sheet_data(
            company_facts, taxonomy_map, period=query.period
        )
        if not results:
            raise EmptyDataError(
                f"No balance sheet data could be extracted for symbol: {query.symbol}"
            )

        return results

    @staticmethod
    def transform_data(
        query: SecBalanceSheetQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[SecBalanceSheetData]:
        """Transform the data and validate the model."""
        if not data:
            raise EmptyDataError("The request was returned empty.")

        if query.limit is not None:
            data = data[: query.limit]

        return [SecBalanceSheetData.model_validate(d) for d in data]
