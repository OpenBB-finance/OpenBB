"""Federal Reserve Bank of Philadelphia GDPplus Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_federal_reserve.utils.philadelphia import MEDIA_URL

URL = f"{MEDIA_URL}/data-visualizations/gdpplus.xlsx"


class FederalReservePhiladelphiaGdpPlusQueryParams(QueryParams):
    """Philadelphia Fed GDPplus Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReservePhiladelphiaGdpPlusData(Data):
    """Philadelphia Fed GDPplus Data."""

    date: dateType = Field(description="The quarter, as a quarter-start date.")
    gdpplus: float | None = Field(
        default=None, description="The GDPplus annualized growth rate, percent."
    )
    gdp_growth: float | None = Field(
        default=None, description="The expenditure-side GDP growth rate, percent."
    )
    gdi_growth: float | None = Field(
        default=None, description="The income-side GDI growth rate, percent."
    )
    recession: float | None = Field(
        default=None,
        description="The NBER recession indicator for the quarter, 1 in recession.",
    )


class FederalReservePhiladelphiaGdpPlusFetcher(
    Fetcher[
        FederalReservePhiladelphiaGdpPlusQueryParams,
        list[FederalReservePhiladelphiaGdpPlusData],
    ]
):
    """Philadelphia Fed GDPplus Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReservePhiladelphiaGdpPlusQueryParams:
        """Transform the query params."""
        return FederalReservePhiladelphiaGdpPlusQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReservePhiladelphiaGdpPlusQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the GDPplus workbook."""
        from openbb_federal_reserve.utils.philadelphia import fetch_philadelphia

        content = fetch_philadelphia(URL, "gdpplus", "quarterly")
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReservePhiladelphiaGdpPlusQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReservePhiladelphiaGdpPlusData]:
        """Parse the GDPplus sheet into quarterly growth records."""
        from pandas import isna

        from openbb_federal_reserve.utils.philadelphia import (
            quarter_start,
            read_workbook,
        )

        frame = read_workbook(data[0]["_raw"], "Sheet1")
        frame = frame.rename(
            columns={
                "OBS_YEAR": "year",
                "OBS_QUARTER": "quarter",
                "GDPPLUS_DATA": "gdpplus",
                "GRGDP_DATA": "gdp_growth",
                "GRGDI_DATA": "gdi_growth",
                "RECBARS": "recession",
            }
        )
        frame = frame.dropna(subset=["year", "quarter"])
        frame["date"] = quarter_start(frame["year"], frame["quarter"])
        columns = ["date", "gdpplus", "gdp_growth", "gdi_growth"]
        if "recession" in frame:
            columns.append("recession")
        frame = frame[columns]

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReservePhiladelphiaGdpPlusData.model_validate(
                {
                    key: (None if isinstance(value, float) and isna(value) else value)
                    for key, value in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
