"""FMP Company Overview Model."""

from typing import Any, Dict, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_overview import (
    CompanyOverviewData,
    CompanyOverviewQueryParams,
)
from pydantic import field_validator


class FMPCompanyOverviewQueryParams(CompanyOverviewQueryParams):
    """FMP Company Overview Query.

    Source: https://site.financialmodelingprep.com/developer/docs/companies-key-stats-free-api/
    """


class FMPCompanyOverviewData(CompanyOverviewData):
    """FMP Company Overview Data."""

    @field_validator("ipo_date", mode="before", check_fields=False)
    @classmethod
    def ipoDate_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        from datetime import date  # pylint: disable=import-outside-toplevel

        if isinstance(v, date) or v is None:
            return v
        return date.fromisoformat(v) if v else None


class FMPCompanyOverviewFetcher(
    Fetcher[
        FMPCompanyOverviewQueryParams,
        FMPCompanyOverviewData,
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPCompanyOverviewQueryParams:
        """Transform the query params."""
        return FMPCompanyOverviewQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPCompanyOverviewQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import get_data_one

        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        url = f"{base_url}/profile/{query.symbol}?apikey={api_key}"

        return await get_data_one(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPCompanyOverviewQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> FMPCompanyOverviewData:
        """Return the transformed data."""
        return FMPCompanyOverviewData.model_validate(data)
