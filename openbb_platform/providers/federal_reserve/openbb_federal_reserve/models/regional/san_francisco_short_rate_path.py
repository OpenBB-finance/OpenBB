"""Federal Reserve Bank of San Francisco Estimated Short-Rate Path Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = "https://www.frbsf.org/wp-content/uploads/FRBSF_Term_Web_Chart_Data.xlsx"

_SCENARIOS = {
    "MOSTRECENT": "Most Recent",
    "FOMC": "FOMC Summary of Economic Projections",
}


class FederalReserveSanFranciscoShortRatePathQueryParams(QueryParams):
    """San Francisco Fed Estimated Short-Rate Path Query Parameters."""


class FederalReserveSanFranciscoShortRatePathData(Data):
    """San Francisco Fed Estimated Short-Rate Path Data."""

    maturity: float = Field(description="The horizon ahead, in years.")


class FederalReserveSanFranciscoShortRatePathFetcher(
    Fetcher[
        FederalReserveSanFranciscoShortRatePathQueryParams,
        list[FederalReserveSanFranciscoShortRatePathData],
    ]
):
    """San Francisco Fed Estimated Short-Rate Path Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveSanFranciscoShortRatePathQueryParams:
        """Transform the query params."""
        return FederalReserveSanFranciscoShortRatePathQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveSanFranciscoShortRatePathQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the Term Premium web-chart workbook from the SF Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> bytes:
            """Fetch the raw Term Premium workbook bytes."""
            response = make_request(URL)
            response.raise_for_status()
            return response.content

        content = cached(
            "san_francisco_term_premium",
            lambda: seconds_until_next_release("daily"),
            _producer,
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveSanFranciscoShortRatePathQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveSanFranciscoShortRatePathData]:
        """Decode the scenarios into one wide row per horizon."""
        from io import BytesIO

        from pandas import isna, read_excel, to_numeric

        frame = read_excel(
            BytesIO(data[0]["_raw"]),
            engine="openpyxl",
            sheet_name="Estimated_Short_Rate_Path",
        )
        frame = frame.rename(columns={"MATURITY": "maturity"})
        scenarios = [c for c in _SCENARIOS if c in frame.columns]
        frame["maturity"] = to_numeric(frame["maturity"], errors="coerce")
        for column in scenarios:
            frame[column] = to_numeric(frame[column], errors="coerce")
        frame = frame.dropna(subset=["maturity"])

        return [
            FederalReserveSanFranciscoShortRatePathData.model_validate(
                {
                    "maturity": float(row["maturity"]),
                    **{
                        _SCENARIOS[column]: (
                            None
                            if isinstance(row[column], float) and isna(row[column])
                            else float(row[column])
                        )
                        for column in scenarios
                    },
                }
            )
            for row in frame.sort_values("maturity").to_dict(orient="records")
        ]
