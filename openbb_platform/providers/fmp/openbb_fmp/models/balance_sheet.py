"""FMP Balance Sheet Model."""


from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.data import ForceInt
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.balance_sheet import (
    BalanceSheetData,
    BalanceSheetQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_fmp.utils.helpers import create_url, get_data_many
from pydantic import Field, model_validator


class FMPBalanceSheetQueryParams(BalanceSheetQueryParams):
    """FMP Balance Sheet Query.

    Source: https://financialmodelingprep.com/developer/docs/#Balance-Sheet
    """

    period: Optional[Literal["annual", "quarter"]] = Field(
        default="quarter",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )
    cik: Optional[str] = Field(
        default=None,
        description="Central Index Key (CIK) of the company.",
    )

    @model_validator(mode="before")
    @classmethod
    def check_symbol_or_cik(cls, values):  # pylint: disable=no-self-argument
        """Check if symbol or cik is provided."""
        if values.get("symbol") is None and values.get("cik") is None:
            raise ValueError("symbol or cik must be provided")
        return values


class FMPBalanceSheetData(BalanceSheetData):
    """FMP Balance Sheet Data."""

    __alias_dict__ = {
        "currency": "reportedCurrency",
        "current_assets": "totalCurrentAssets",
        "non_current_assets": "totalNonCurrentAssets",
        "assets": "totalAssets",
        "current_liabilities": "totalCurrentLiabilities",
        "non_current_liabilities": "totalNonCurrentLiabilities",
        "liabilities": "totalLiabilities",
        "other_stockholder_equity": "othertotalStockholdersEquity",
        "filing_date": "fillingDate",
    }

    # Leftovers below
    calendar_year: Optional[ForceInt] = Field(default=None, description="Calendar Year")

    cash_and_short_term_investments: Optional[ForceInt] = Field(
        default=None, description="Cash and Short Term Investments"
    )
    goodwill_and_intangible_assets: Optional[ForceInt] = Field(
        default=None, description="Goodwill and Intangible Assets"
    )
    deferred_revenue_non_current: Optional[ForceInt] = Field(
        default=None, description="Deferred Revenue Non Current"
    )
    total_investments: Optional[ForceInt] = Field(
        default=None, description="Total Investments"
    )

    capital_lease_obligations: Optional[ForceInt] = Field(
        default=None, description="Capital Lease Obligations"
    )
    deferred_tax_liabilities_non_current: Optional[ForceInt] = Field(
        default=None, description="Deferred Tax Liabilities Non Current"
    )
    capital_lease_obligations: Optional[ForceInt] = Field(
        default=None, description="Capital lease obligations"
    )
    total_investments: Optional[ForceInt] = Field(
        default=None, description="Total investments"
    )
    total_debt: Optional[ForceInt] = Field(default=None, description="Total debt")
    net_debt: Optional[ForceInt] = Field(default=None, description="Net debt")

    total_debt: Optional[ForceInt] = Field(default=None, description="Total Debt")
    net_debt: Optional[ForceInt] = Field(default=None, description="Net Debt")

    link: Optional[str] = Field(default=None, description="Link to the statement.")
    final_link: Optional[str] = Field(
        default=None, description="Link to the final statement."
    )

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):  # pylint: disable=no-self-argument
        """Check for zero values and replace with None."""
        return {k: None if v == 0 else v for k, v in values.items()}


class FMPBalanceSheetFetcher(
    Fetcher[
        FMPBalanceSheetQueryParams,
        List[FMPBalanceSheetData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPBalanceSheetQueryParams:
        """Transform the query params."""
        return FMPBalanceSheetQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPBalanceSheetQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            3, f"balance-sheet-statement/{query.symbol}", api_key, query, ["symbol"]
        )

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPBalanceSheetQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPBalanceSheetData]:
        """Return the transformed data."""
        return [FMPBalanceSheetData.model_validate(d) for d in data]
