"""SEC Income Statement Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


class SecIncomeStatementQueryParams(IncomeStatementQueryParams):
    """SEC Income Statement Query.

    Source: https://data.sec.gov/api/xbrl/companyfacts/

    Uses the SEC EDGAR Company Facts API to extract income statement data
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


class SecIncomeStatementData(IncomeStatementData):
    """SEC Income Statement Data."""

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
    # Revenue
    revenue: float | None = Field(
        default=None,
        description="Total revenue.",
    )
    cost_of_revenue: float | None = Field(
        default=None,
        description="Cost of goods and services sold.",
    )
    gross_profit: float | None = Field(
        default=None,
        description="Gross profit.",
    )
    # Operating expenses
    research_and_development: float | None = Field(
        default=None,
        description="Research and development expenses.",
    )
    selling_general_and_administrative: float | None = Field(
        default=None,
        description="Selling, general, and administrative expenses.",
    )
    operating_expenses: float | None = Field(
        default=None,
        description="Total operating expenses.",
    )
    operating_income: float | None = Field(
        default=None,
        description="Operating income (loss).",
    )
    # Non-operating
    interest_expense: float | None = Field(
        default=None,
        description="Interest expense.",
    )
    interest_income: float | None = Field(
        default=None,
        description="Interest and investment income.",
    )
    other_non_operating_income: float | None = Field(
        default=None,
        description="Other non-operating income (expense).",
    )
    # Income
    pretax_income: float | None = Field(
        default=None,
        description="Income before income taxes.",
    )
    income_tax_expense: float | None = Field(
        default=None,
        description="Income tax expense (benefit).",
    )
    consolidated_net_income: float | None = Field(
        default=None,
        description="Consolidated net income, including non-controlling interest.",
    )
    net_income: float | None = Field(
        default=None,
        description="Net income attributable to common stockholders.",
    )
    # Per share
    basic_earnings_per_share: float | None = Field(
        default=None,
        description="Basic earnings per share.",
    )
    diluted_earnings_per_share: float | None = Field(
        default=None,
        description="Diluted earnings per share.",
    )
    weighted_average_shares_outstanding: float | None = Field(
        default=None,
        description="Weighted average shares outstanding, basic.",
    )
    weighted_average_shares_diluted: float | None = Field(
        default=None,
        description="Weighted average shares outstanding, diluted.",
    )
    # Other
    depreciation_and_amortization: float | None = Field(
        default=None,
        description="Depreciation and amortization.",
    )
    ebitda: float | None = Field(
        default=None,
        description="Earnings before interest, taxes, depreciation, and amortization.",
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


class SecIncomeStatementFetcher(
    Fetcher[SecIncomeStatementQueryParams, list[SecIncomeStatementData]]
):
    """SEC Income Statement Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecIncomeStatementQueryParams:
        """Transform the query."""
        return SecIncomeStatementQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecIncomeStatementQueryParams,
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

        taxonomy_map = load_taxonomy("income_statement")
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
                f"No income statement data could be extracted for symbol: {query.symbol}"
            )

        return results

    @staticmethod
    def transform_data(
        query: SecIncomeStatementQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[SecIncomeStatementData]:
        """Transform the data and validate the model."""
        if not data:
            raise EmptyDataError("The request was returned empty.")

        if query.limit is not None:
            data = data[: query.limit]

        return [SecIncomeStatementData.model_validate(d) for d in data]
