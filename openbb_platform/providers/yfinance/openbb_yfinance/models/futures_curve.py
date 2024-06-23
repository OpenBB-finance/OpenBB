"""Yahoo Finance Futures Curve Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.futures_curve import (
    FuturesCurveData,
    FuturesCurveQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError


class YFinanceFuturesCurveQueryParams(FuturesCurveQueryParams):
    """Yahoo Finance Futures Curve Query.

    Source: https://finance.yahoo.com/crypto/
    """


class YFinanceFuturesCurveData(FuturesCurveData):
    """Yahoo Finance Futures Curve Data."""

    __alias_dict__ = {"price": "Last Price"}


class YFinanceFuturesCurveFetcher(
    Fetcher[
        YFinanceFuturesCurveQueryParams,
        List[YFinanceFuturesCurveData],
    ]
):
    """Transform the query, extract and transform the data from the Yahoo Finance endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceFuturesCurveQueryParams:
        """Transform the query."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("date") is None:
            transformed_params["date"] = now

        return YFinanceFuturesCurveQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: YFinanceFuturesCurveQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Yahoo Finance endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_yfinance.utils.helpers import get_futures_curve

        data = get_futures_curve(query.symbol, query.date).to_dict(orient="records")

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
        return [
            YFinanceFuturesCurveData(
                expiration=curve["expiration"],
                price=curve["Last Price"],
            )
            for curve in data
        ]
