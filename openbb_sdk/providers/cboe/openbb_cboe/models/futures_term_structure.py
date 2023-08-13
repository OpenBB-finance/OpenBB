"""CBOE Futures Term Structure fetcher."""

# IMPORT STANDARD
from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.futures_term_structure import (
    FuturesTermStructureData,
    FuturesTermStructureQueryParams,
)
from pydantic import Field, validator

from openbb_cboe.utils.helpers import get_term_structure


class CboeFuturesTermStructureQueryParams(FuturesTermStructureQueryParams):
    """CBOE Futures Term Structure Query.

    Source: https://www.cboe.com/
    """


class CboeFuturesTermStructureData(FuturesTermStructureData):
    """CBOE Futures Term Structure Data."""

    symbol: str = Field(description="The trading symbol for the tenor of future.")

    @validator("expiration", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d")


class CboeFuturesTermStructureFetcher(
    Fetcher[
        CboeFuturesTermStructureQueryParams,
        List[CboeFuturesTermStructureData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeFuturesTermStructureQueryParams:
        return CboeFuturesTermStructureQueryParams(**params)

    @staticmethod
    def extract_data(
        query: CboeFuturesTermStructureQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[CboeFuturesTermStructureData]:
        data = (
            get_term_structure(query.symbol, query.date)
            .reset_index()
            .to_dict("records")
        )

        return [CboeFuturesTermStructureData.parse_obj(d) for d in data]

    @staticmethod
    def transform_data(
        data: List[CboeFuturesTermStructureData],
    ) -> List[CboeFuturesTermStructureData]:
        return data
