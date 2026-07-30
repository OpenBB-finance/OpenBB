"""Federal Reserve Bank of Kansas City Financial Stress Index Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = "https://kcresearch-share.kansascityfed.org/kc-fsi/kcfsi.csv"


class FederalReserveKansasCityFinancialStressQueryParams(QueryParams):
    """Kansas City Fed Financial Stress Index Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveKansasCityFinancialStressData(Data):
    """Kansas City Fed Financial Stress Index Data."""

    date: dateType = Field(description="The observation month.")
    kcfsi: float | None = Field(
        default=None, description="The Kansas City Financial Stress Index value."
    )


class FederalReserveKansasCityFinancialStressFetcher(
    Fetcher[
        FederalReserveKansasCityFinancialStressQueryParams,
        list[FederalReserveKansasCityFinancialStressData],
    ]
):
    """Kansas City Fed Financial Stress Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveKansasCityFinancialStressQueryParams:
        """Transform the query params."""
        return FederalReserveKansasCityFinancialStressQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveKansasCityFinancialStressQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the KCFSI CSV from the Kansas City Fed research host."""
        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )
        from openbb_federal_reserve.utils.kansas_city import fetch_kansas_city

        content = cached(
            "kansas_city_fsi",
            lambda: seconds_until_next_release("monthly"),
            lambda: fetch_kansas_city(URL),
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveKansasCityFinancialStressQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveKansasCityFinancialStressData]:
        """Parse the KCFSI CSV and apply the date filters."""
        from io import BytesIO

        from pandas import isna, read_csv, to_datetime

        frame = read_csv(BytesIO(data[0]["_raw"]))
        frame = frame.rename(columns={"DATE": "date", "KCFSI": "kcfsi"})
        frame["date"] = to_datetime(frame["date"], format="%Y-%m-%d").dt.date

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveKansasCityFinancialStressData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
