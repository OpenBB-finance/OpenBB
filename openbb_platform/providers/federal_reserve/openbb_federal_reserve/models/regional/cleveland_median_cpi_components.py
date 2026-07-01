"""Federal Reserve Bank of Cleveland Median CPI Components Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = (
    "https://www.clevelandfed.org/-/media/files/webcharts"
    "/mediancpi/mediancpi_component_table.csv"
)

_COLUMN_MAP = {
    "Component": "component",
    "1-Month Annualized Percent Change": "change",
    "Relative Importance (Normalized)": "relative_importance",
    "Cumulative Relative Importance": "cumulative_relative_importance",
}


class FederalReserveClevelandMedianCpiComponentsQueryParams(QueryParams):
    """Cleveland Fed Median CPI Components Query Parameters."""


class FederalReserveClevelandMedianCpiComponentsData(Data):
    """Cleveland Fed Median CPI Components Data."""

    component: str = Field(description="The CPI expenditure category.")
    change: float | None = Field(
        default=None,
        description="The category's 1-month annualized percent change.",
    )
    relative_importance: float | None = Field(
        default=None,
        description="The category's normalized relative importance, in percent.",
    )
    cumulative_relative_importance: float | None = Field(
        default=None,
        description="The cumulative relative importance through this category,"
        " sorted by price change, in percent.",
    )


class FederalReserveClevelandMedianCpiComponentsFetcher(
    Fetcher[
        FederalReserveClevelandMedianCpiComponentsQueryParams,
        list[FederalReserveClevelandMedianCpiComponentsData],
    ]
):
    """Cleveland Fed Median CPI Components Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveClevelandMedianCpiComponentsQueryParams:
        """Transform the query params."""
        return FederalReserveClevelandMedianCpiComponentsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveClevelandMedianCpiComponentsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the latest Median CPI component table from the Cleveland Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> str:
            """Fetch the component table CSV text."""
            response = make_request(URL)
            response.raise_for_status()
            return response.text

        text = cached(
            "cleveland_median_cpi_components",
            lambda: seconds_until_next_release("monthly"),
            _producer,
        )
        if not text:
            raise EmptyDataError("The request was returned empty.")
        return [{"_text": text}]

    @staticmethod
    def transform_data(
        query: FederalReserveClevelandMedianCpiComponentsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveClevelandMedianCpiComponentsData]:
        """Parse the component table, preserving the price-change ordering."""
        from io import StringIO

        from pandas import isna, read_csv

        frame = read_csv(StringIO(data[0]["_text"]))
        frame.columns = [str(column).strip() for column in frame.columns]
        frame = frame.rename(columns=_COLUMN_MAP)

        return [
            FederalReserveClevelandMedianCpiComponentsData.model_validate(
                {
                    key: (None if isinstance(value, float) and isna(value) else value)
                    for key, value in row.items()
                    if key in _COLUMN_MAP.values()
                }
            )
            for row in frame.to_dict(orient="records")
        ]
