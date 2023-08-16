"""CBOE Futures Curve fetcher."""

# IMPORT STANDARD
from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.futures_curve import (
    FuturesCurveData,
    FuturesCurveQueryParams,
)
from pydantic import Field, validator

from openbb_cboe.utils.helpers import get_curve


class CboeFuturesCurveQueryParams(FuturesCurveQueryParams):
    """CBOE Futures Curve Query.

    Source: https://www.cboe.com/
    """


class CboeFuturesCurveData(FuturesCurveData):
    """CBOE Futures Term Structure Data."""

    symbol: str = Field(description="The trading symbol for the tenor of future.")


class CboeFuturesCurveFetcher(
    Fetcher[
        CboeFuturesCurveQueryParams,
        List[CboeFuturesCurveData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeFuturesCurveQueryParams:
        return CboeFuturesCurveQueryParams(**params)

    @staticmethod
    def extract_data(
        query: CboeFuturesCurveQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[CboeFuturesCurveData]:
        data = get_curve(query.symbol, query.date).reset_index().to_dict("records")

        return [CboeFuturesCurveData.parse_obj(d) for d in data]

    @staticmethod
    def transform_data(
        data: List[CboeFuturesCurveData],
    ) -> List[CboeFuturesCurveData]:
        return data
