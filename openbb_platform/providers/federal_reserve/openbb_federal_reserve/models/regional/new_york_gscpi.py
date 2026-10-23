"""Federal Reserve Bank of New York Global Supply Chain Pressure Index Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = (
    "https://www.newyorkfed.org/medialibrary/research/interactives"
    "/gscpi/downloads/gscpi_data.xlsx"
)


class FederalReserveNewYorkSupplyChainQueryParams(QueryParams):
    """New York Fed Global Supply Chain Pressure Index Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveNewYorkSupplyChainData(Data):
    """New York Fed Global Supply Chain Pressure Index Data."""

    date: dateType = Field(description="The observation month.")
    gscpi: float | None = Field(
        default=None, description="The Global Supply Chain Pressure Index value."
    )


class FederalReserveNewYorkSupplyChainFetcher(
    Fetcher[
        FederalReserveNewYorkSupplyChainQueryParams,
        list[FederalReserveNewYorkSupplyChainData],
    ]
):
    """New York Fed Global Supply Chain Pressure Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveNewYorkSupplyChainQueryParams:
        """Transform the query params."""
        return FederalReserveNewYorkSupplyChainQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveNewYorkSupplyChainQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the GSCPI workbook from the New York Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> bytes:
            """Fetch the raw GSCPI workbook bytes."""
            response = make_request(URL)
            response.raise_for_status()
            return response.content

        content = cached(
            "new_york_gscpi", lambda: seconds_until_next_release("monthly"), _producer
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveNewYorkSupplyChainQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveNewYorkSupplyChainData]:
        """Parse the GSCPI monthly sheet and apply the date filters."""
        from io import BytesIO

        from pandas import isna, read_excel, to_datetime

        frame = read_excel(BytesIO(data[0]["_raw"]), sheet_name="GSCPI Monthly Data")
        frame = frame[["Date", "GSCPI"]].rename(
            columns={"Date": "date", "GSCPI": "gscpi"}
        )
        frame["date"] = to_datetime(frame["date"], format="%d-%b-%Y", errors="coerce")
        frame = frame.dropna(subset=["date"])
        frame["date"] = frame["date"].dt.date

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveNewYorkSupplyChainData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
