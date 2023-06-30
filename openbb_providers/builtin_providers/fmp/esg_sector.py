"""FMP ESG Sector fetcher."""

# IMPORT STANDARD
from datetime import date
from typing import Dict, List, Optional

from pydantic import Field

# IMPORT THIRD-PARTY
from builtin_providers.fmp.helpers import create_url, get_data_many

# IMPORT INTERNAL
from openbb_provider.model.abstract.data import Data, QueryParams
from openbb_provider.model.data.esg_sector import ESGSectorData, ESGSectorQueryParams
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer

current_year = date.today().year


class FMPESGSectorQueryParams(QueryParams):
    """FMP ESG Sector query.

    Source: https://site.financialmodelingprep.com/developer/docs/#ESG-Benchmarking-By-Sector-and-Year

    Parameter
    ---------
    year : int
        The year of the data.
    """

    __name__ = "FMPESGSectorQueryParams"

    year: int = Field(ge=2000, le=current_year)


class FMPESGSectorData(Data):
    __name__ = "FMPESGSectorData"
    year: int
    sector: str
    environmentalScore: float
    socialScore: float
    governanceScore: float
    ESGScore: float = Field(alias="esg_score")


class FMPESGSectorFetcher(
    Fetcher[
        ESGSectorQueryParams, ESGSectorData, FMPESGSectorQueryParams, FMPESGSectorData
    ]
):
    @staticmethod
    def transform_query(
        query: ESGSectorQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPESGSectorQueryParams:
        return FMPESGSectorQueryParams(year=query.year)

    @staticmethod
    def extract_data(
        query: FMPESGSectorQueryParams, api_key: str
    ) -> List[FMPESGSectorData]:
        url = create_url(
            4, "esg-environmental-social-governance-sector-benchmark", api_key, query
        )
        return get_data_many(url, FMPESGSectorData)

    @staticmethod
    def transform_data(data: List[FMPESGSectorData]) -> List[ESGSectorData]:
        return data_transformer(data, ESGSectorData)
