"""yfinance Futures End of Day fetcher."""
# ruff: noqa: SIM105

import warnings
from datetime import datetime
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
        """Pydantic alias config using fields dict."""

        fields = {
            "price": "Last Price",
        }


class YFinanceFuturesCurveFetcher(
    Fetcher[
        YFinanceFuturesCurveQueryParams,
        List[YFinanceFuturesCurveData],
    ]
):
    """Transform the query, extract and transform the data from the yfinance endpoints."""

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
    ) -> List[dict]:
        """Return the raw data from the yfinance endpoint."""
        data = get_futures_curve(query.symbol, query.date).to_dict(orient="records")
        if len(data) == 0:
            warnings.warn(f"Symbol {query.symbol} not found in yfinance")

        return data

    @staticmethod
    def transform_data(
        data: dict,
    ) -> List[YFinanceFuturesCurveData]:
        """Transform the data to the standard format."""
        return [
            YFinanceFuturesCurveData(
                expiration=curve["expiration"],
                price=curve["Last Price"],
            )
            for curve in data
        ]
