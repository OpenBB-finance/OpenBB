"""CBOE Futures Curve Fetcher."""

# IMPORT STANDARD
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.futures_curve import (
    FuturesCurveData,
    FuturesCurveQueryParams,
)
from pydantic import Field

from openbb_cboe.utils.helpers import get_curve


class CboeFuturesCurveQueryParams(FuturesCurveQueryParams):
    """CBOE Futures Curve Query.

    Source: https://www.cboe.com/
    """


class CboeFuturesCurveData(FuturesCurveData):
    """CBOE Futures Curve Data."""

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
    ) -> dict:
        """Return the raw data from the CBOE endpoint."""

        data = get_curve(query.symbol, query.date).reset_index().to_dict("records")

        return data

    @staticmethod
    def transform_data(
        data: dict,
    ) -> List[CboeFuturesCurveData]:
        return [CboeFuturesCurveData.parse_obj(d) for d in data]
