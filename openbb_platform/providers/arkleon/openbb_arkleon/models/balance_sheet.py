"""Arkleon BalanceSheet models and as-filed fetcher."""

from datetime import date
from typing import Any

from openbb_arkleon.utils.client import fetch_facts, resolve_api_key
from openbb_arkleon.utils.statements import build_records, order_and_limit, validate_cik
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.balance_sheet import (
    BalanceSheetData,
    BalanceSheetQueryParams,
)
from pydantic import Field

BALANCE_SHEET_TAGS: dict[str, list[str]] = {
    "total_assets": [
        "Assets",
    ],
    "total_current_assets": [
        "AssetsCurrent",
    ],
    "cash_and_cash_equivalents": [
        "CashAndCashEquivalentsAtCarryingValue",
    ],
    "total_liabilities": [
        "Liabilities",
    ],
    "total_current_liabilities": [
        "LiabilitiesCurrent",
    ],
    "long_term_debt": [
        "LongTermDebtNoncurrent",
    ],
    "total_equity": [
        "StockholdersEquity",
    ],
    "total_liabilities_and_equity": [
        "LiabilitiesAndStockholdersEquity",
    ],
}


class ArkleonBalanceSheetQueryParams(BalanceSheetQueryParams):
    """Request facts knowable on an explicit filing-date cutoff."""

    symbol: str = Field(
        description="SEC CIK of the company, digits only. Tickers are not served by Arkleon /v1."
    )
    as_of: date = Field(
        description="Point-in-time date. Only facts from filings filed on or before this date are returned."
    )


class ArkleonBalanceSheetData(BalanceSheetData):
    """Reported values and their original filing lineage."""

    accession_id: str = Field(description="SEC filing accession identifier.")
    form: str | None = Field(description="SEC filing form.")
    filed: date = Field(description="Date the filing was filed with the SEC.")
    source_url: str | None = Field(description="Source filing in the SEC EDGAR archive.")
    duration_quarters: int = Field(description="As-filed duration in quarters; 0 is instantaneous.")
    total_assets: float | None = Field(
        default=None,
        description="As filed, using us-gaap:Assets.",
    )
    total_current_assets: float | None = Field(
        default=None,
        description="As filed, using us-gaap:AssetsCurrent.",
    )
    cash_and_cash_equivalents: float | None = Field(
        default=None,
        description="As filed, using us-gaap:CashAndCashEquivalentsAtCarryingValue.",
    )
    total_liabilities: float | None = Field(
        default=None,
        description="As filed, using us-gaap:Liabilities.",
    )
    total_current_liabilities: float | None = Field(
        default=None,
        description="As filed, using us-gaap:LiabilitiesCurrent.",
    )
    long_term_debt: float | None = Field(
        default=None,
        description="As filed, using us-gaap:LongTermDebtNoncurrent.",
    )
    total_equity: float | None = Field(
        default=None,
        description="As filed, using us-gaap:StockholdersEquity.",
    )
    total_liabilities_and_equity: float | None = Field(
        default=None,
        description="As filed, using us-gaap:LiabilitiesAndStockholdersEquity.",
    )


class ArkleonBalanceSheetFetcher(Fetcher[ArkleonBalanceSheetQueryParams, list[ArkleonBalanceSheetData]]):
    """Fetch and assemble facts without deriving unreported values."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ArkleonBalanceSheetQueryParams:
        """Validate provider query parameters."""
        return ArkleonBalanceSheetQueryParams(**params)

    @staticmethod
    def extract_data(
        query: ArkleonBalanceSheetQueryParams, credentials: dict | None, **kwargs: Any
    ) -> dict:
        """Fetch all tags, preserving pagination and filing lineage."""
        api_key = resolve_api_key(credentials)
        cik = validate_cik(query.symbol)
        duration_quarters = 0
        facts_by_field = {}
        for field, tags in BALANCE_SHEET_TAGS.items():
            facts_by_field[field] = []
            unit = "USD"
            for tag in tags:
                facts_by_field[field].extend(
                    fetch_facts(
                        api_key, cik, query.as_of.isoformat(), tag, duration_quarters, unit
                    )
                )
        return {"facts_by_field": facts_by_field}

    @staticmethod
    def transform_data(
        query: ArkleonBalanceSheetQueryParams, data: dict, **kwargs: Any
    ) -> list[ArkleonBalanceSheetData]:
        """Keep all filings within the selected distinct reporting periods."""
        records = build_records(data["facts_by_field"], BALANCE_SHEET_TAGS)
        records = order_and_limit(records, query.limit)
        return [ArkleonBalanceSheetData.model_validate(record) for record in records]
