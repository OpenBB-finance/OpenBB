"""FMP Income Statement Growth Fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import create_url, get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.income_statement_growth import (
    IncomeStatementGrowthData,
    IncomeStatementGrowthQueryParams,
)
from pydantic import validator


class FMPIncomeStatementGrowthQueryParams(IncomeStatementGrowthQueryParams):
    """FMP Income Statement Growth QueryParams.

    Source: https://site.financialmodelingprep.com/developer/docs/financial-statements-growth-api/
    """


class FMPIncomeStatementGrowthData(IncomeStatementGrowthData):
    """FMP Income Statement Growth Data."""

    class Config:
        """Pydantic alias config using fields dict."""

        fields = {
            "growth_ebitda": "growthEBITDA",
            "growth_ebitda_ratio": "growthEBITDARatio",
            "growth_eps": "growthEPS",
            "growth_eps_diluted": "growthEPSDiluted",
        }

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d")


class FMPIncomeStatementGrowthFetcher(
    Fetcher[
        FMPIncomeStatementGrowthQueryParams,
        List[FMPIncomeStatementGrowthData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPIncomeStatementGrowthQueryParams:
        """Transform the query params."""
        return FMPIncomeStatementGrowthQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPIncomeStatementGrowthQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            3, f"income-statement-growth/{query.symbol}", api_key, query, ["symbol"]
        )

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPIncomeStatementGrowthData]:
        """Return the transformed data."""
        return [FMPIncomeStatementGrowthData.parse_obj(d) for d in data]
