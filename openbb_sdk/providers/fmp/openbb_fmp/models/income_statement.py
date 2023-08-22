"""FMP Income Statement Fetcher."""


from typing import Any, Dict, List, Literal, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from pydantic import Field, root_validator

from openbb_fmp.utils.helpers import get_data_many

PeriodType = Literal["annual", "quarter"]


class FMPIncomeStatementQueryParams(IncomeStatementQueryParams):
    """FMP Income Statement QueryParams.

    Source: https://financialmodelingprep.com/developer/docs/#Income-Statement

    Either a Symbol or CIK is required. Symbol is preferred over CIK.
    """

    cik: Optional[str] = Field(
        description="The CIK of the company if no symbol is provided."
    )

    @root_validator()
    def check_symbol_or_cik(cls, values):  # pylint: disable=no-self-argument
        """Validate that either a symbol or CIK is provided."""
        if values.get("symbol") is None and values.get("cik") is None:
            raise ValueError("symbol or cik must be provided")
        return values


class FMPIncomeStatementData(IncomeStatementData):
    """FMP Income Statement Data."""

    class Config:
        """Pydantic alias config using fields dict."""

        fields = {
            "currency": "reportedCurrency",
            "ebitda_ratio": "ebitdaratio",
            "eps_diluted": "epsdiluted",
            "weighted_average_shares_outstanding": "weightedAverageShsOut",
            "weighted_average_shares_outstanding_dil": "weightedAverageShsOutDil",
        }


class FMPIncomeStatementFetcher(
    Fetcher[
        FMPIncomeStatementQueryParams,
        List[FMPIncomeStatementData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPIncomeStatementQueryParams:
        """Transform the query params."""
        return FMPIncomeStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPIncomeStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        symbol = query.symbol or query.cik
        base_url = "https://financialmodelingprep.com/api/v3"

        url = (
            f"{base_url}/income-statement/{symbol}?"
            f"period={query.period}&limit={query.limit}&apikey={api_key}"
        )

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPIncomeStatementData]:
        """Return the transformed data."""
        return [FMPIncomeStatementData(**d) for d in data]
