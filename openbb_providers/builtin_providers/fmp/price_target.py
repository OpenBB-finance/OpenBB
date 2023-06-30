"""FMP Stock Ownership fetcher."""

# IMPORT STANDARD
from datetime import datetime
from typing import Dict, List, Optional

# IMPORT THIRD-PARTY
from pydantic import Field

from builtin_providers.fmp.helpers import create_url, get_data_many
from openbb_provider.model.abstract.data import Data

# IMPORT INTERNAL
from openbb_provider.model.data.price_target import (
    PriceTargetData,
    PriceTargetQueryParams,
)
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer


class FMPPriceTargetQueryParams(PriceTargetQueryParams):
    """FMP Price Target query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Price-Target

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """

    __name__ = "FMPPriceTargetQueryParams"


class FMPPriceTargetData(Data):
    __name__ = "FMPPriceTargetData"

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
        query: FMPPriceTargetQueryParams, api_key: str
    ) -> List[FMPPriceTargetData]:
        url = create_url(4, "price-target", api_key, query)
        return get_data_many(url, FMPPriceTargetData)

    @staticmethod
    def transform_data(data: List[FMPPriceTargetData]) -> List[PriceTargetData]:
        return data_transformer(data, PriceTargetData)
