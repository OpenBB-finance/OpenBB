"""yfinance Futures end of day fetcher."""


from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.futures_curve import (
    FuturesCurveData,
    FuturesCurveQueryParams,
)

from openbb_yfinance.utils import helpers


class YFinanceFuturesCurveQueryParams(FuturesCurveQueryParams):
    """YFinance Futures Curve Query."""


class YFinanceFuturesCurveData(FuturesCurveData):
    """YFinance Futures end of day Data."""

    class Config:
        fields = {
            "expiration": "expiration",
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
        data = helpers.get_futures_curve(query.symbol, query.date).to_dict(
            orient="records"
        )
        return [YFinanceFuturesCurveData.parse_obj(d) for d in data]

    @staticmethod
    def transform_data(
        data: List[YFinanceFuturesCurveData],
    ) -> List[YFinanceFuturesCurveData]:
        return data
