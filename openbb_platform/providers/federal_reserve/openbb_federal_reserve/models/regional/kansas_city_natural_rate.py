"""Federal Reserve Bank of Kansas City Model-Based Natural Rate Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = (
    "https://kcresearch-share.kansascityfed.org/kc-mbnr/"
    "KCFed_ModelBased_Rstar_Ustar.csv"
)
_COLUMNS = [
    "date",
    "rstar",
    "rstar_lower",
    "rstar_upper",
    "ustar",
    "ustar_lower",
    "ustar_upper",
]


class FederalReserveKansasCityNaturalRateQueryParams(QueryParams):
    """Kansas City Fed Model-Based Natural Rate Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveKansasCityNaturalRateData(Data):
    """Kansas City Fed Model-Based Natural Rate Data."""

    date: dateType = Field(description="The observation month.")
    rstar: float | None = Field(
        default=None, description="The natural rate of interest (r-star) estimate."
    )
    rstar_lower: float | None = Field(
        default=None, description="The lower bound of the r-star 68% band."
    )
    rstar_upper: float | None = Field(
        default=None, description="The upper bound of the r-star 68% band."
    )
    ustar: float | None = Field(
        default=None, description="The natural rate of unemployment (u-star) estimate."
    )
    ustar_lower: float | None = Field(
        default=None, description="The lower bound of the u-star 68% band."
    )
    ustar_upper: float | None = Field(
        default=None, description="The upper bound of the u-star 68% band."
    )


class FederalReserveKansasCityNaturalRateFetcher(
    Fetcher[
        FederalReserveKansasCityNaturalRateQueryParams,
        list[FederalReserveKansasCityNaturalRateData],
    ]
):
    """Kansas City Fed Model-Based Natural Rate Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveKansasCityNaturalRateQueryParams:
        """Transform the query params."""
        return FederalReserveKansasCityNaturalRateQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveKansasCityNaturalRateQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the Model-Based r*/u* CSV from the Kansas City Fed host."""
        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )
        from openbb_federal_reserve.utils.kansas_city import fetch_kansas_city

        content = cached(
            "kansas_city_natural_rate",
            lambda: seconds_until_next_release("monthly"),
            lambda: fetch_kansas_city(URL),
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveKansasCityNaturalRateQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveKansasCityNaturalRateData]:
        """Parse the two-header-row CSV and apply the date filters."""
        from io import BytesIO

        from pandas import isna, read_csv, to_datetime

        frame = read_csv(BytesIO(data[0]["_raw"]), header=None, skiprows=2)
        frame.columns = _COLUMNS
        frame["date"] = to_datetime(frame["date"], format="%Y-%m-%d").dt.date

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveKansasCityNaturalRateData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
