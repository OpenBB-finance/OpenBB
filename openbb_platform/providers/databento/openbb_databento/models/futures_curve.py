"""DataBento Futures Curve Model."""

# ruff: noqa: SIM105

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.futures_curve import (
    FuturesCurveData,
    FuturesCurveQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_databento.utils.helpers import get_futures_curve, last_business_day


class DatabentoFuturesCurveQueryParams(FuturesCurveQueryParams):
    """Databento Futures Curve Query."""


class DatabentoFuturesCurveData(FuturesCurveData):
    """Databento Futures Curve Data."""


class DatabentoFuturesCurveFetcher(
    Fetcher[
        DatabentoFuturesCurveQueryParams,
        List[DatabentoFuturesCurveData],
    ]
):
    """Transform the query, extract and transform the data from the Databento endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> DatabentoFuturesCurveQueryParams:
        """Transform the query."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("date") is None:
            transformed_params["date"] = last_business_day(now)

        return DatabentoFuturesCurveQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: DatabentoFuturesCurveQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[dict]:
        """Return the raw data from the Yahoo Finance endpoint."""
        key = credentials.get("databento_api_key") if credentials else ""
        data = get_futures_curve(query.symbol, query.date, key).to_dict(
            orient="records"
        )

        if not data:
            raise EmptyDataError()

        return data

    @staticmethod
    def transform_data(
        query: DatabentoFuturesCurveQueryParams,  # pylint: disable=unused-argument
        data: dict,
        **kwargs: Any,
    ) -> List[DatabentoFuturesCurveData]:
        """Transform the data to the standard format."""
        return [
            DatabentoFuturesCurveData(
                expiration=curve["expiration"],
                price=curve["price"],
            )
            for curve in data
        ]
