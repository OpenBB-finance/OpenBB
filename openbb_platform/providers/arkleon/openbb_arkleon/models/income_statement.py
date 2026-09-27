"""Arkleon IncomeStatement models and as-filed fetcher."""

from datetime import date
from typing import Any, Literal

from openbb_arkleon.utils.client import fetch_facts, resolve_api_key
from openbb_arkleon.utils.statements import build_records, order_and_limit, validate_cik
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from pydantic import Field

INCOME_STATEMENT_TAGS: dict[str, list[str]] = {
    "revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
    ],
    "cost_of_revenue": [
        "CostOfGoodsAndServicesSold",
        "CostOfRevenue",
    ],
    "gross_profit": [
        "GrossProfit",
    ],
    "operating_income": [
        "OperatingIncomeLoss",
    ],
    "net_income": [
        "NetIncomeLoss",
    ],
    "eps_basic": [
        "EarningsPerShareBasic",
    ],
    "eps_diluted": [
        "EarningsPerShareDiluted",
    ],
}


class ArkleonIncomeStatementQueryParams(IncomeStatementQueryParams):
    """Request facts knowable on an explicit filing-date cutoff."""

    symbol: str = Field(
        description="SEC CIK of the company, digits only. Tickers are not served by Arkleon /v1."
    )
    as_of: date = Field(
        description="Point-in-time date. Only facts from filings filed on or before this date are returned."
    )
    period: Literal["annual", "quarter"] = Field(
        default="annual",
        description=(
            "annual requests 4-quarter durations, quarter requests 1-quarter durations, exactly as filed. "
            "Year-to-date values are not converted."
        ),
    )


class ArkleonIncomeStatementData(IncomeStatementData):
    """Reported values and their original filing lineage."""

    accession_id: str = Field(description="SEC filing accession identifier.")
    form: str | None = Field(description="SEC filing form.")
    filed: date = Field(description="Date the filing was filed with the SEC.")
    source_url: str | None = Field(description="Source filing in the SEC EDGAR archive.")
    duration_quarters: int = Field(description="As-filed duration in quarters; 0 is instantaneous.")
    revenue: float | None = Field(
        default=None,
        description="As filed, using us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax, then us-gaap:Revenues.",
    )
    cost_of_revenue: float | None = Field(
        default=None,
        description="As filed, using us-gaap:CostOfGoodsAndServicesSold, then us-gaap:CostOfRevenue.",
    )
    gross_profit: float | None = Field(
        default=None,
        description="As filed, using us-gaap:GrossProfit.",
    )
    operating_income: float | None = Field(
        default=None,
        description="As filed, using us-gaap:OperatingIncomeLoss.",
    )
    net_income: float | None = Field(
        default=None,
        description="As filed, using us-gaap:NetIncomeLoss.",
    )
    eps_basic: float | None = Field(
        default=None,
        description="As filed, using us-gaap:EarningsPerShareBasic.",
    )
    eps_diluted: float | None = Field(
        default=None,
        description="As filed, using us-gaap:EarningsPerShareDiluted.",
    )


class ArkleonIncomeStatementFetcher(Fetcher[ArkleonIncomeStatementQueryParams, list[ArkleonIncomeStatementData]]):
    """Fetch and assemble facts without deriving unreported values."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ArkleonIncomeStatementQueryParams:
        """Validate provider query parameters."""
        return ArkleonIncomeStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: ArkleonIncomeStatementQueryParams, credentials: dict | None, **kwargs: Any
    ) -> dict:
        """Fetch all tags, preserving pagination and filing lineage."""
        api_key = resolve_api_key(credentials)
        cik = validate_cik(query.symbol)
        duration_quarters = 4 if query.period == "annual" else 1
        facts_by_field = {}
        for field, tags in INCOME_STATEMENT_TAGS.items():
            facts_by_field[field] = []
            unit = "USD/shares" if field in ("eps_basic", "eps_diluted") else "USD"
            for tag in tags:
                facts_by_field[field].extend(
                    fetch_facts(
                        api_key, cik, query.as_of.isoformat(), tag, duration_quarters, unit
                    )
                )
        return {"facts_by_field": facts_by_field}

    @staticmethod
    def transform_data(
        query: ArkleonIncomeStatementQueryParams, data: dict, **kwargs: Any
    ) -> list[ArkleonIncomeStatementData]:
        """Keep all filings within the selected distinct reporting periods."""
        records = build_records(data["facts_by_field"], INCOME_STATEMENT_TAGS)
        records = order_and_limit(records, query.limit)
        return [ArkleonIncomeStatementData.model_validate(record) for record in records]
