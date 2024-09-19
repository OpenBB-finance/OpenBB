"""FMP Institutional Ownership Model."""

from datetime import date as dateType
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.institutional_ownership import (
    InstitutionalOwnershipData,
    InstitutionalOwnershipQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_fmp.utils.helpers import create_url, get_data_many
from pydantic import Field


class FMPInstitutionalOwnershipQueryParams(InstitutionalOwnershipQueryParams):
    """FMP Institutional Ownership Query.

    Source: https://site.financialmodelingprep.com/developer/docs/institutional-stock-ownership-api/
    """

    include_current_quarter: Optional[bool] = Field(
        default=False, description="Include current quarter data."
    )
    date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("date", "")
    )


class FMPInstitutionalOwnershipData(InstitutionalOwnershipData):
    """FMP Institutional Ownership Data."""

    __alias_dict__ = {
        "number_of_13f_shares": "numberOf13Fshares",
        "last_number_of_13f_shares": "lastNumberOf13Fshares",
        "number_of_13f_shares_change": "numberOf13FsharesChange",
    }

    investors_holding: int = Field(description="Number of investors holding the stock.")
    last_investors_holding: int = Field(
        description="Number of investors holding the stock in the last quarter."
    )
    investors_holding_change: int = Field(
        description="Change in the number of investors holding the stock."
    )
    number_of_13f_shares: int = Field(
        default=None,
        description="Number of 13F shares.",
    )
    last_number_of_13f_shares: int = Field(
        default=None,
        description="Number of 13F shares in the last quarter.",
    )
    number_of_13f_shares_change: int = Field(
        default=None,
        description="Change in the number of 13F shares.",
    )
    total_invested: float = Field(description="Total amount invested.")
    last_total_invested: float = Field(
        description="Total amount invested in the last quarter."
    )
    total_invested_change: float = Field(
        description="Change in the total amount invested."
    )
    ownership_percent: float = Field(description="Ownership percent.")
    last_ownership_percent: float = Field(
        description="Ownership percent in the last quarter."
    )
    ownership_percent_change: float = Field(
        description="Change in the ownership percent."
    )
    new_positions: int = Field(description="Number of new positions.")
    last_new_positions: int = Field(
        description="Number of new positions in the last quarter."
    )
    new_positions_change: int = Field(
        description="Change in the number of new positions."
    )
    increased_positions: int = Field(description="Number of increased positions.")
    last_increased_positions: int = Field(
        description="Number of increased positions in the last quarter."
    )
    increased_positions_change: int = Field(
        description="Change in the number of increased positions."
    )
    closed_positions: int = Field(description="Number of closed positions.")
    last_closed_positions: int = Field(
        description="Number of closed positions in the last quarter."
    )
    closed_positions_change: int = Field(
        description="Change in the number of closed positions."
    )
    reduced_positions: int = Field(description="Number of reduced positions.")
    last_reduced_positions: int = Field(
        description="Number of reduced positions in the last quarter."
    )
    reduced_positions_change: int = Field(
        description="Change in the number of reduced positions."
    )
    total_calls: int = Field(
        description="Total number of call options contracts traded for Apple Inc. on the specified date."
    )
    last_total_calls: int = Field(
        description="Total number of call options contracts traded for Apple Inc. on the previous reporting date."
    )
    total_calls_change: int = Field(
        description="Change in the total number of call options contracts traded between "
        "the current and previous reporting dates."
    )
    total_puts: int = Field(
        description="Total number of put options contracts traded for Apple Inc. on the specified date."
    )
    last_total_puts: int = Field(
        description="Total number of put options contracts traded for Apple Inc. on the previous reporting date."
    )
    total_puts_change: int = Field(
        description="Change in the total number of put "
        "options contracts traded between the current and previous reporting dates."
    )
    put_call_ratio: float = Field(
        description="Put-call ratio, which is the ratio of the total number of "
        "put options to call options traded on the specified date."
    )
    last_put_call_ratio: float = Field(
        description="Put-call ratio on the previous reporting date."
    )
    put_call_ratio_change: float = Field(
        description="Change in the put-call ratio between the current and previous reporting dates."
    )


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
    async def aextract_data(
        query: FMPInstitutionalOwnershipQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(4, "institutional-ownership/symbol-ownership", api_key, query)

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPInstitutionalOwnershipQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPInstitutionalOwnershipData]:
        """Return the transformed data."""
        return [FMPInstitutionalOwnershipData.model_validate(d) for d in data]
