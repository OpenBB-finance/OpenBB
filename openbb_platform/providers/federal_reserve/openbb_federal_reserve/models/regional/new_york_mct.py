"""Federal Reserve Bank of New York Multivariate Core Trend Inflation Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = (
    "https://www.newyorkfed.org/medialibrary/Research/Interactives"
    "/Data/mct/mct-chart-data.csv"
)

_COLUMNS = {
    1: "date",
    2: "mct",
    3: "mct_upper",
    4: "mct_upper_2",
    5: "mct_lower",
    6: "headline_pce",
    7: "core_pce",
    8: "goods",
    9: "services_ex_housing",
    10: "housing",
    11: "goods_common",
    12: "goods_sector_specific",
    13: "services_ex_housing_common",
    14: "services_ex_housing_sector_specific",
    15: "housing_common",
    16: "housing_sector_specific",
}


class FederalReserveNewYorkCoreTrendInflationQueryParams(QueryParams):
    """New York Fed Multivariate Core Trend Inflation Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveNewYorkCoreTrendInflationData(Data):
    """New York Fed Multivariate Core Trend Inflation Data."""

    date: dateType = Field(description="The reference month, as the month-start date.")
    mct: float | None = Field(
        default=None, description="The Multivariate Core Trend inflation estimate."
    )
    mct_upper: float | None = Field(
        default=None, description="The upper uncertainty band of the MCT estimate."
    )
    mct_upper_2: float | None = Field(
        default=None,
        description="The outer upper uncertainty band of the MCT estimate.",
    )
    mct_lower: float | None = Field(
        default=None, description="The lower uncertainty band of the MCT estimate."
    )
    headline_pce: float | None = Field(
        default=None, description="Year-over-year headline PCE inflation."
    )
    core_pce: float | None = Field(
        default=None, description="Year-over-year core PCE inflation."
    )
    goods: float | None = Field(
        default=None, description="The goods sector contribution to trend inflation."
    )
    services_ex_housing: float | None = Field(
        default=None,
        description="The services-ex-housing contribution to trend inflation.",
    )
    housing: float | None = Field(
        default=None, description="The housing contribution to trend inflation."
    )
    goods_common: float | None = Field(
        default=None,
        description="The common component of the goods sector contribution.",
    )
    goods_sector_specific: float | None = Field(
        default=None,
        description="The sector-specific component of the goods sector contribution.",
    )
    services_ex_housing_common: float | None = Field(
        default=None,
        description="The common component of the services-ex-housing contribution.",
    )
    services_ex_housing_sector_specific: float | None = Field(
        default=None,
        description="The sector-specific component of the"
        " services-ex-housing contribution.",
    )
    housing_common: float | None = Field(
        default=None,
        description="The common component of the housing contribution.",
    )
    housing_sector_specific: float | None = Field(
        default=None,
        description="The sector-specific component of the housing contribution.",
    )


class FederalReserveNewYorkCoreTrendInflationFetcher(
    Fetcher[
        FederalReserveNewYorkCoreTrendInflationQueryParams,
        list[FederalReserveNewYorkCoreTrendInflationData],
    ]
):
    """New York Fed Multivariate Core Trend Inflation Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveNewYorkCoreTrendInflationQueryParams:
        """Transform the query params."""
        return FederalReserveNewYorkCoreTrendInflationQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveNewYorkCoreTrendInflationQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the MCT chart data CSV from the New York Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> str:
            """Fetch the raw MCT CSV text, decoding the UTF-8 BOM."""
            response = make_request(URL)
            response.raise_for_status()
            return response.content.decode("utf-8-sig")

        text = cached(
            "new_york_mct", lambda: seconds_until_next_release("monthly"), _producer
        )
        if not text:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": text}]

    @staticmethod
    def transform_data(
        query: FederalReserveNewYorkCoreTrendInflationQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveNewYorkCoreTrendInflationData]:
        """Parse the MCT CSV by column position and apply the date filters."""
        from io import StringIO

        from pandas import isna, read_csv, to_datetime

        frame = read_csv(StringIO(data[0]["_raw"]), skiprows=[0, 1, 2])
        frame = frame.iloc[:, list(_COLUMNS)]
        frame.columns = list(_COLUMNS.values())
        frame["date"] = to_datetime(frame["date"], format="%m/%d/%Y", errors="coerce")
        frame = frame.dropna(subset=["date"])
        frame["date"] = frame["date"].dt.date

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveNewYorkCoreTrendInflationData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
