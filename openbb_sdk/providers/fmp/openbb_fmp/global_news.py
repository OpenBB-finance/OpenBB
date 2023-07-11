"""FMP Global News fetcher."""

# IMPORT STANDARD
from datetime import datetime
from typing import Dict, List, Optional

from builtin_providers.fmp.helpers import create_url, get_data_many

# IMPORT INTERNAL
from openbb_provider.model.abstract.data import Data, QueryParams
from openbb_provider.model.data.global_news import GlobalNewsData, GlobalNewsQueryParams
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer

# IMPORT THIRD-PARTY
from pydantic import Field


class FMPGlobalNewsQueryParams(QueryParams):
    """FMP Global News query.

    Source: https://site.financialmodelingprep.com/developer/docs/general-news-api/

    Parameter
    ---------
    page : int (default: 0)
        The page of the data to retrieve.
    """

    page: int = Field(default=0)


class FMPGlobalNewsData(Data):
    publishedDate: datetime = Field(alias="date")
    title: str
    image: str
    text: str
    url: str
    site: str


class FMPGlobalNewsFetcher(
    Fetcher[
        GlobalNewsQueryParams,
        GlobalNewsData,
        FMPGlobalNewsQueryParams,
        FMPGlobalNewsData,
    ]
):
    @staticmethod
    def transform_query(
        query: GlobalNewsQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPGlobalNewsQueryParams:
        return FMPGlobalNewsQueryParams(page=query.page)

    @staticmethod
    def extract_data(
        query: FMPGlobalNewsQueryParams, api_key: str
    ) -> List[FMPGlobalNewsData]:
        url = create_url(4, "general_news", api_key, query)
        return get_data_many(url, FMPGlobalNewsData)

    @staticmethod
    def transform_data(data: List[FMPGlobalNewsData]) -> List[GlobalNewsData]:
        return data_transformer(data, GlobalNewsData)
