"""FMP ESG Sector fetcher."""


from datetime import date
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.models.esg_sector import ESGSectorData, ESGSectorQueryParams
from pydantic import Field

from openbb_fmp.utils.helpers import create_url, get_data_many

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
    def transform_query(params: Dict[str, Any]) -> FMPESGSectorQueryParams:
        return FMPESGSectorQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPESGSectorQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> List[FMPESGSectorData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            4, "esg-environmental-social-governance-sector-benchmark", api_key, query
        )
        return get_data_many(url, FMPESGSectorData)

    @staticmethod
    def transform_data(data: List[FMPESGSectorData]) -> List[FMPESGSectorData]:
        return data
