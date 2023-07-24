"""FMP Institutional Ownership Fetcher."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import Dict, List, Optional

from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer
from openbb_provider.models.base import BaseSymbol
from openbb_provider.models.institutional_ownership import (
    InstitutionalOwnershipData,
    InstitutionalOwnershipQueryParams,
)

# IMPORT THIRD-PARTY
from pydantic import Field, validator

from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPInstitutionalOwnershipQueryParams(QueryParams, BaseSymbol):
    """FMP Institutional Ownership QueryParams.

    Source: https://site.financialmodelingprep.com/developer/docs/institutional-stock-ownership-api/

    Parameter
    ---------
    symbol : str
        The symbol of the company if cik is not provided.
    include_current_quarter : bool
        Whether to include the current quarter. Default is False.
    date : Optional[dateType]
        A specific date to get data for.
    """

    includeCurrentQuarter: bool = Field(default=False, alias="include_current_quarter")
    date: Optional[dateType]


class FMPInstitutionalOwnershipData(Data):
    symbol: str = Field(min_length=1)
    cik: str = Field(min_length=1)
    date: dateType
    investorsHolding: int
    lastInvestorsHolding: int
    investorsHoldingChange: int
    numberOf13Fshares: int
    lastNumberOf13Fshares: int
    numberOf13FsharesChange: int
    totalInvested: float
    lastTotalInvested: float
    totalInvestedChange: float
    ownershipPercent: float
    lastOwnershipPercent: float
    ownershipPercentChange: float
    newPositions: int
    lastNewPositions: int
    newPositionsChange: int
    increasedPositions: int
    lastIncreasedPositions: int
    increasedPositionsChange: int
    closedPositions: int
    lastClosedPositions: int
    closedPositionsChange: int
    reducedPositions: int
    lastReducedPositions: int
    reducedPositionsChange: int
    totalCalls: int
    lastTotalCalls: int
    totalCallsChange: int
    totalPuts: int
    lastTotalPuts: int
    totalPutsChange: int
    putCallRatio: float
    lastPutCallRatio: float
    putCallRatioChange: float

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
    def transform_query(
        query: InstitutionalOwnershipQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPInstitutionalOwnershipQueryParams:
        return FMPInstitutionalOwnershipQueryParams(
            symbol=query.symbol,
            date=query.date,
            include_current_quarter=query.include_current_quarter,
            **extra_params if extra_params else {}
        )

    @staticmethod
    def extract_data(
        query: FMPInstitutionalOwnershipQueryParams,
        credentials: Optional[Dict[str, str]],
    ) -> List[FMPInstitutionalOwnershipData]:
        if credentials:
            api_key = credentials.get("fmp_api_key")

        url = create_url(4, "institutional-ownership/symbol-ownership", api_key, query)
        return get_data_many(url, FMPInstitutionalOwnershipData)

    @staticmethod
    def transform_data(
        data: List[FMPInstitutionalOwnershipData],
    ) -> List[InstitutionalOwnershipData]:
        return data_transformer(data, InstitutionalOwnershipData)
