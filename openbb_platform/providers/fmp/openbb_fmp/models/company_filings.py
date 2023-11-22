"""FMP Company Filings Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Union

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_filings import (
    SEC_FORM_TYPES,
    CompanyFilingsData,
    CompanyFilingsQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data_many
from pydantic import Field, field_validator


class FMPCompanyFilingsQueryParams(CompanyFilingsQueryParams):
    """FMP Copmany Filings Query.

    Source: https://site.financialmodelingprep.com/developer/docs/sec-filings-api/
    """

    type: Optional[SEC_FORM_TYPES] = Field(
        default=None, description="Type of the SEC filing form."
    )
    page: Optional[int] = Field(default=0, description="Page number of the results.")


class FMPCompanyFilingsData(CompanyFilingsData):
    """FMP Company Filings Data."""

    __alias_dict__ = {
        "date": "fillingDate",
    }

    symbol: str = Field(description="The ticker symbol of the company.")
    cik: str = Field(description="CIK of the SEC filing.")
    accepted_date: datetime = Field(description="Accepted date of the SEC filing.")
    final_link: str = Field(description="Final link of the SEC filing.")

    @field_validator("symbol", mode="before", check_fields=False)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class FMPCompanyFilingsFetcher(
    Fetcher[
        FMPCompanyFilingsQueryParams,
        List[FMPCompanyFilingsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPCompanyFilingsQueryParams:
        """Transform the query params."""
        return FMPCompanyFilingsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPCompanyFilingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            3, f"sec_filings/{query.symbol}", api_key, query, exclude=["symbol"]
        )

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPCompanyFilingsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPCompanyFilingsData]:
        """Return the transformed data."""
        return [FMPCompanyFilingsData.model_validate(d) for d in data]
