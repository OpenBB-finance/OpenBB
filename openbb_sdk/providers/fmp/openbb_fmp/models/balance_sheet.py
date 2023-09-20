"""FMP Balance Sheet Fetcher."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import create_url, get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.balance_sheet import (
    BalanceSheetData,
    BalanceSheetQueryParams,
)
from pydantic import Field, validator


class FMPBalanceSheetQueryParams(BalanceSheetQueryParams):
    """FMP Balance Sheet QueryParams.

    Source: https://financialmodelingprep.com/developer/docs/#Balance-Sheet
    """

    symbol: str = Field(description="Symbol/CIK of the company.")


class FMPBalanceSheetData(BalanceSheetData):
    """FMP Balance Sheet Data."""

    class Config:
        """Pydantic alias config using fields Dict."""

        fields = {
            "marketable_securities": "longTermInvestments",
            "other_shareholder_equity": "othertotalStockholdersEquity",
            "total_shareholder_equity": "totalStockholdersEquity",
            "total_liabilities_and_shareholders_equity": "totalLiabilitiesAndStockholdersEquity",
        }

    reported_currency: str = Field(description="Reported currency in the statement.")

    filling_date: dateType = Field(description="Filling date.")
    accepted_date: datetime = Field(description="Accepted date.")
    calendar_year: int = Field(description="Calendar year.")

    cash_and_short_term_investments: Optional[int] = Field(
        description="Cash and short term investments"
    )
    goodwill_and_intangible_assets: Optional[int] = Field(
        description="Goodwill and Intangible Assets"
    )
    capital_lease_obligations: Optional[int] = Field(
        description="Capital lease obligations"
    )
    total_investments: Optional[int] = Field(description="Total investments")
    total_debt: Optional[int] = Field(description="Total debt")
    net_debt: Optional[int] = Field(description="Net debt")

    link: Optional[str] = Field(description="Link to the statement.")
    final_link: Optional[str] = Field(description="Link to the final statement.")

    @validator("filing_date", pre=True, check_fields=False)
    def filing_date_validate(cls, v):  # pylint: disable=no-self-argument
        """Validate the filing date."""
        return datetime.strptime(v, "%Y-%m-%d").date()

    @validator("accepted_date", pre=True, check_fields=False)
    def accepted_date_validate(cls, v):  # pylint: disable=no-self-argument
        """Validate the accepted date."""
        return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")


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
    def transform_data(data: List[Dict]) -> List[FMPBalanceSheetData]:
        """Return the transformed data."""
        return [FMPBalanceSheetData.parse_obj(d) for d in data]
