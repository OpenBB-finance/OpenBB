"""FMP ESG Sector fetcher."""

# IMPORT STANDARD
from datetime import date
from typing import Dict, List, Optional

# IMPORT INTERNAL
from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer
from openbb_provider.models.esg_sector import ESGSectorData, ESGSectorQueryParams
from pydantic import Field

# IMPORT THIRD-PARTY
from .helpers import create_url, get_data_many

current_year = date.today().year


class FMPESGSectorQueryParams(QueryParams):
    """FMP ESG Sector query.

    Source: https://site.financialmodelingprep.com/developer/docs/#ESG-Benchmarking-By-Sector-and-Year

    Parameter
    ---------
    year : int
        The year of the data.
    """

    year: int = Field(ge=2000, le=current_year)


class FMPESGSectorData(Data):
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
        query: FMPESGSectorQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPESGSectorData]:
        if credentials:
            api_key = credentials.get("fmp_api_key")

        url = create_url(
            4, "esg-environmental-social-governance-sector-benchmark", api_key, query
        )
        return get_data_many(url, FMPESGSectorData)

    @staticmethod
    def transform_data(data: List[FMPESGSectorData]) -> List[ESGSectorData]:
        return data_transformer(data, ESGSectorData)
