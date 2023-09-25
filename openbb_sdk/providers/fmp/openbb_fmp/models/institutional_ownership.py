"""FMP Institutional Ownership Fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import create_url, get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.institutional_ownership import (
    InstitutionalOwnershipData,
    InstitutionalOwnershipQueryParams,
)
from pydantic import validator


class FMPInstitutionalOwnershipQueryParams(InstitutionalOwnershipQueryParams):
    """FMP Institutional Ownership Query.

    Source: https://site.financialmodelingprep.com/developer/docs/institutional-stock-ownership-api/
    """


class FMPInstitutionalOwnershipData(InstitutionalOwnershipData):
    """FMP Institutional Ownership Data."""

    class Config:
        """Pydantic alias config using fields dict."""

        fields = {
            "number_of_13f_shares": "numberOf13Fshares",
            "last_number_of_13f_shares": "lastNumberOf13Fshares",
            "number_of_13f_shares_change": "numberOf13FsharesChange",
        }

    @validator("date", pre=True, check_fields=False)
    def time_validate(cls, v):  # pylint: disable=no-self-argument
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d")


class FMPInstitutionalOwnershipFetcher(
    Fetcher[
        FMPInstitutionalOwnershipQueryParams,
        List[FMPInstitutionalOwnershipData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPInstitutionalOwnershipQueryParams:
        """Transform the query params."""
        return FMPInstitutionalOwnershipQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPInstitutionalOwnershipQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(4, "institutional-ownership/symbol-ownership", api_key, query)

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPInstitutionalOwnershipData]:
        """Return the transformed data."""
        return [FMPInstitutionalOwnershipData.parse_obj(d) for d in data]
