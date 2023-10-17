"""FMP Index Constituents Fetcher."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Literal, Optional, Union

from openbb_fmp.utils.helpers import get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.index_constituents import (
    IndexConstituentsData,
    IndexConstituentsQueryParams,
)
from pydantic import Field, field_validator


class FMPIndexConstituentsQueryParams(IndexConstituentsQueryParams):
    """FMP Index Constituents query.

    Source: https://site.financialmodelingprep.com/developer/docs/list-of-dow-companies-api/
            https://site.financialmodelingprep.com/developer/docs/list-of-sp-500-companies-api/
            https://site.financialmodelingprep.com/developer/docs/list-of-nasdaq-companies-api/
    """

    symbol: Literal["nasdaq", "sp500", "dowjones"] = Field(
        default="dowjones",
        description="Supported indices.",
    )


class FMPIndexConstituentsData(IndexConstituentsData):
    """FMP Index Constituents data."""

    sector: Optional[str] = Field(
        description="Sector the constituent company in the index belongs to.",
        default=None,
    )
    sub_sector: Optional[str] = Field(
        default=None,
        description="Sub-sector the constituent company in the index belongs to.",
    )
    headquarter: Optional[str] = Field(
        default=None,
        description="Location of the headquarter of the constituent company in the index.",
        alias="headQuarter",
    )
    date_first_added: Optional[Union[dateType, str]] = Field(
        default=None, description="Date the constituent company was added to the index."
    )
    cik: Optional[Union[str, int]] = Field(
        description="Central Index Key of the constituent company in the index.",
        default=None,
    )
    founded: Optional[Union[dateType, str]] = Field(
        default=None,
        description="Founding year of the constituent company in the index.",
    )

    @field_validator("dateFirstAdded", mode="before", check_fields=False)
    @classmethod
    def date_first_added_validate(cls, v):  # pylint: disable=E0213
        """Return the date_first_added date as a datetime object for valid cases."""
        try:
            return datetime.strptime(v, "%Y-%m-%d") if v else None
        except Exception:
            # For returning string in case of mismatched dates
            return v

    @field_validator("founded", mode="before", check_fields=False)
    @classmethod
    def founded_validate(cls, v):  # pylint: disable=E0213
        """Return the founded date as a datetime object for valid cases."""
        try:
            return datetime.strptime(v, "%Y-%m-%d") if v else None
        except Exception:
            # For returning string in case of mismatched dates
            return v


class FMPIndexConstituentsFetcher(
    Fetcher[
        FMPIndexConstituentsQueryParams,
        List[FMPIndexConstituentsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPIndexConstituentsQueryParams:
        """Transform the query params."""
        return FMPIndexConstituentsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPIndexConstituentsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        url = f"{base_url}/{query.symbol}_constituent/?apikey={api_key}"

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict], **kwargs: Any) -> List[FMPIndexConstituentsData]:
        """Return the raw data from the FMP endpoint."""
        return [FMPIndexConstituentsData.model_validate(d) for d in data]
