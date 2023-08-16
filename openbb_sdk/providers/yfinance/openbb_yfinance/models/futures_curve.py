"""yfinance Futures End of Day fetcher."""


from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.futures_curve import (
    FuturesCurveData,
    FuturesCurveQueryParams,
)

from openbb_yfinance.utils.helpers import get_futures_curve


class YFinanceFuturesCurveQueryParams(FuturesCurveQueryParams):
    """YFinance Futures Curve Query."""


class YFinanceFuturesCurveData(FuturesCurveData):
    """YFinance Futures End of Day Data."""

    class Config:
        fields = {
            "price": "Last Price",
        }


class YFinanceFuturesCurveFetcher(
    Fetcher[
        YFinanceFuturesCurveQueryParams,
        List[YFinanceFuturesCurveData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceFuturesCurveQueryParams:
        return YFinanceFuturesCurveQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceFuturesCurveQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[YFinanceFuturesCurveData]:
        return get_futures_curve(query.symbol, query.date).to_dict(orient="records")

    @staticmethod
    def transform_data(
        data: List[YFinanceFuturesCurveData],
    ) -> List[YFinanceFuturesCurveData]:
        return [YFinanceFuturesCurveData.parse_obj(d) for d in data]
