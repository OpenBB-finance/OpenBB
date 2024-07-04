"""Yahoo Finance Futures Curve Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.futures_curve import (
    FuturesCurveData,
    FuturesCurveQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError


class YFinanceFuturesCurveQueryParams(FuturesCurveQueryParams):
    """Yahoo Finance Futures Curve Query.

    Source: https://finance.yahoo.com/
    """

    __json_schema_extra__ = {
        "date": {"multiple_items_allowed": True},
    }


class YFinanceFuturesCurveData(FuturesCurveData):
    """Yahoo Finance Futures Curve Data."""


class YFinanceFuturesCurveFetcher(
    Fetcher[
        YFinanceFuturesCurveQueryParams,
        List[YFinanceFuturesCurveData],
    ]
):
    """YFiannce Futures Curve Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceFuturesCurveQueryParams:
        """Transform the query."""
        return YFinanceFuturesCurveQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: YFinanceFuturesCurveQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the data from Yahoo."""
        # pylint: disable=import-outside-toplevel
        from openbb_yfinance.utils.helpers import get_futures_curve

        # TODO: Find a better way to do this.
        data = await get_futures_curve(query.symbol, query.date)  # type: ignore
        data = data.to_dict(orient="records")

        if not data:
            raise EmptyDataError()

        return data

    @staticmethod
    def transform_data(
        query: YFinanceFuturesCurveQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinanceFuturesCurveData]:
        """Transform the data to the standard format."""
        return [YFinanceFuturesCurveData.model_validate(d) for d in data]
