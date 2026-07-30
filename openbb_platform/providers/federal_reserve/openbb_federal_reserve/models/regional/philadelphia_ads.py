"""Federal Reserve Bank of Philadelphia ADS Business Conditions Index Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = (
    "https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data"
    "/ads/ads_index_most_current_vintage.xlsx"
)


class FederalReservePhiladelphiaAdsQueryParams(QueryParams):
    """Philadelphia Fed ADS Business Conditions Index Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReservePhiladelphiaAdsData(Data):
    """Philadelphia Fed ADS Business Conditions Index Data."""

    date: dateType = Field(description="The observation date.")
    ads_index: float | None = Field(
        default=None, description="The ADS Business Conditions Index value."
    )
    recession: float | None = Field(
        default=None,
        description="The NBER recession indicator for the date, 1 in recession.",
    )


class FederalReservePhiladelphiaAdsFetcher(
    Fetcher[
        FederalReservePhiladelphiaAdsQueryParams,
        list[FederalReservePhiladelphiaAdsData],
    ]
):
    """Philadelphia Fed ADS Business Conditions Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReservePhiladelphiaAdsQueryParams:
        """Transform the query params."""
        return FederalReservePhiladelphiaAdsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReservePhiladelphiaAdsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the ADS index workbook from the Philadelphia Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> bytes:
            """Fetch the raw ADS workbook bytes."""
            response = make_request(URL)
            response.raise_for_status()
            return response.content

        content = cached(
            "philadelphia_ads", lambda: seconds_until_next_release("daily"), _producer
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReservePhiladelphiaAdsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReservePhiladelphiaAdsData]:
        """Parse the workbook and apply the date filters."""
        from io import BytesIO

        from pandas import isna, read_excel, to_datetime

        frame = read_excel(BytesIO(data[0]["_raw"]), engine="openpyxl")
        names = ["date", "ads_index"]
        if len(frame.columns) > 2:
            names.append("recession")
        frame.columns = [*names, *list(frame.columns[len(names) :])]
        frame = frame[names]
        frame["date"] = to_datetime(frame["date"], format="%Y:%m:%d").dt.date

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReservePhiladelphiaAdsData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
