"""FMP Institutional Ownership Fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.institutional_ownership import (
    InstitutionalOwnershipData,
    InstitutionalOwnershipQueryParams,
)
from pydantic import validator

from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPInstitutionalOwnershipQueryParams(InstitutionalOwnershipQueryParams):
    """FMP Institutional Ownership Query.

    Source: https://site.financialmodelingprep.com/developer/docs/institutional-stock-ownership-api/
    """


class FMPInstitutionalOwnershipData(InstitutionalOwnershipData):
    """FMP Institutional Ownership Data."""

    class Config:
        fields = {
            "investors_holding": "investorsHolding",
            "last_investors_holding": "lastInvestorsHolding",
            "investors_holding_change": "investorsHoldingChange",
            "number_of_13f_shares": "numberOf13Fshares",
            "last_number_of_13f_shares": "lastNumberOf13Fshares",
            "number_of_13f_shares_change": "numberOf13FsharesChange",
            "total_invested": "totalInvested",
            "last_total_invested": "lastTotalInvested",
            "total_invested_change": "totalInvestedChange",
            "ownership_percent": "ownershipPercent",
            "last_ownership_percent": "lastOwnershipPercent",
            "ownership_percent_change": "ownershipPercentChange",
            "new_positions": "newPositions",
            "last_new_positions": "lastNewPositions",
            "new_positions_change": "newPositionsChange",
            "increased_positions": "increasedPositions",
            "last_increased_positions": "lastIncreasedPositions",
            "increased_positions_change": "increasedPositionsChange",
            "closed_positions": "closedPositions",
            "last_closed_positions": "lastClosedPositions",
            "closed_positions_change": "closedPositionsChange",
            "reduced_positions": "reducedPositions",
            "last_reduced_positions": "lastReducedPositions",
            "reduced_positions_change": "reducedPositionsChange",
            "total_calls": "totalCalls",
            "last_total_calls": "lastTotalCalls",
            "total_calls_change": "totalCallsChange",
            "total_puts": "totalPuts",
            "last_total_puts": "lastTotalPuts",
            "total_puts_change": "totalPutsChange",
            "put_call_ratio": "putCallRatio",
            "last_put_call_ratio": "lastPutCallRatio",
            "put_call_ratio_change": "putCallRatioChange",
        }

    @validator("date", pre=True)
    def time_validate(cls, v):  # pylint: disable=no-self-argument
        return datetime.strptime(v, "%Y-%m-%d")


class FMPInstitutionalOwnershipFetcher(
    Fetcher[
        InstitutionalOwnershipQueryParams,
        InstitutionalOwnershipData,
        FMPInstitutionalOwnershipQueryParams,
        FMPInstitutionalOwnershipData,
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPInstitutionalOwnershipQueryParams:
        return FMPInstitutionalOwnershipQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPInstitutionalOwnershipQueryParams,
        credentials: Optional[Dict[str, str]],
    ) -> List[FMPInstitutionalOwnershipData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(4, "institutional-ownership/symbol-ownership", api_key, query)
        return get_data_many(url, FMPInstitutionalOwnershipData)

    @staticmethod
    def transform_data(
        data: List[FMPInstitutionalOwnershipData],
    ) -> List[FMPInstitutionalOwnershipData]:
        return data
