"""FMP Stock Ownership fetcher."""

# IMPORT STANDARD
from datetime import datetime
from typing import Dict, List, Optional

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer

# IMPORT INTERNAL
from openbb_provider.models.price_target import PriceTargetData, PriceTargetQueryParams

# IMPORT THIRD-PARTY
from pydantic import Field

from .helpers import create_url, get_data_many


class FMPPriceTargetQueryParams(PriceTargetQueryParams):
    """FMP Price Target query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Price-Target

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """


class FMPPriceTargetData(Data):
    symbol: str
    publishedDate: datetime
    newsURL: str = Field(alias="news_url")
    newsTitle: Optional[str]
    analystName: Optional[str]
    priceTarget: float
    adjPriceTarget: float
    priceWhenPosted: float
    newsPublisher: str
    newsBaseURL: str = Field(alias="news_base_url")
    analystCompany: str


class FMPPriceTargetFetcher(
    Fetcher[
        PriceTargetQueryParams,
        PriceTargetData,
        FMPPriceTargetQueryParams,
        FMPPriceTargetData,
    ]
):
    @staticmethod
    def transform_query(
        query: PriceTargetQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPPriceTargetQueryParams:
        return FMPPriceTargetQueryParams.parse_obj(query)

    @staticmethod
    def extract_data(
        query: FMPPriceTargetQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPPriceTargetData]:
        if credentials:
            api_key = credentials.get("fmp_api_key")

        url = create_url(4, "price-target", api_key, query)
        return get_data_many(url, FMPPriceTargetData)

    @staticmethod
    def transform_data(data: List[FMPPriceTargetData]) -> List[PriceTargetData]:
        return data_transformer(data, PriceTargetData)
