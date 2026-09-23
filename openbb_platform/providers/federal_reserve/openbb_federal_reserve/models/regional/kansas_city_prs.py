"""Federal Reserve Bank of Kansas City Policy Rate Uncertainty Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = "https://kcresearch-share.kansascityfed.org/kc-prs/KCPRU_KCPRS.csv"


class FederalReserveKansasCityPolicyRateUncertaintyQueryParams(QueryParams):
    """Kansas City Fed Policy Rate Uncertainty Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveKansasCityPolicyRateUncertaintyData(Data):
    """Kansas City Fed Policy Rate Uncertainty Data."""

    date: dateType = Field(description="The observation date.")
    kcpru: float | None = Field(
        default=None, description="The Policy Rate Uncertainty index level (KCPRU)."
    )
    kcprs: float | None = Field(
        default=None, description="The Policy Rate Uncertainty skew (KCPRS)."
    )


class FederalReserveKansasCityPolicyRateUncertaintyFetcher(
    Fetcher[
        FederalReserveKansasCityPolicyRateUncertaintyQueryParams,
        list[FederalReserveKansasCityPolicyRateUncertaintyData],
    ]
):
    """Kansas City Fed Policy Rate Uncertainty Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveKansasCityPolicyRateUncertaintyQueryParams:
        """Transform the query params."""
        return FederalReserveKansasCityPolicyRateUncertaintyQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveKansasCityPolicyRateUncertaintyQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the KCPRU/KCPRS CSV from the Kansas City Fed research host."""
        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )
        from openbb_federal_reserve.utils.kansas_city import fetch_kansas_city

        content = cached(
            "kansas_city_prs",
            lambda: seconds_until_next_release("daily"),
            lambda: fetch_kansas_city(URL),
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveKansasCityPolicyRateUncertaintyQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveKansasCityPolicyRateUncertaintyData]:
        """Build dates from the Year/Month/Day columns and apply date filters."""
        from io import BytesIO

        from pandas import isna, read_csv, to_datetime

        frame = read_csv(BytesIO(data[0]["_raw"]))
        frame["date"] = to_datetime(frame[["Year", "Month", "Day"]]).dt.date
        frame = frame.rename(columns={"KCPRU": "kcpru", "KCPRS": "kcprs"})
        frame = frame[["date", "kcpru", "kcprs"]]

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveKansasCityPolicyRateUncertaintyData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
