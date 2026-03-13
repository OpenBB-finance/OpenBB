"""Survey of Professional Forecasters - Inflation Expectations Data Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.lru import ttl_cache
from pydantic import AliasGenerator, ConfigDict, Field

URL = (
    "https://www.philadelphiafed.org/-/media/FRBP/Assets/Surveys-And-Data"
    "/survey-of-professional-forecasters/historical-data/Inflation.xlsx"
)


@ttl_cache(ttl=86400)
def download_inflation_excel() -> bytes:
    """Download the Inflation Expectations Excel file from the Philadelphia Fed.

    Returns:
        bytes: The Excel file content.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.utils.helpers import make_request

    response = make_request(URL)
    response.raise_for_status()

    return response.content


class FederalReserveInflationExpectationsQueryParams(QueryParams):
    """Federal Reserve Inflation Expectations Query Parameters."""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", "")
        + " Data begins from 1970-04-01 and is quarterly.",
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class FederalReserveInflationExpectationsData(Data):
    """Survey of Professional Forecasters Inflation Expectations Data.

    Contains one-year-ahead and ten-year-ahead inflation forecasts from the
    Philadelphia Fed's Survey of Professional Forecasters.

    The one-year-ahead series are expectations for average inflation over the
    four quarters following the survey quarter.

    Source: https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/inflation-forecasts
    """

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=AliasGenerator(
            validation_alias=lambda field_name: field_name,
            serialization_alias=lambda field_name: field_name,
        ),
        json_schema_extra={
            "x-widget_config": {
                "description": "One-year-ahead and ten-year-ahead inflation forecasts "
                "from the Philadelphia Fed's Survey of Professional Forecasters."
            }
        },
    )

    date: dateType = Field(
        description="The date of the survey (first day of the survey quarter).",
        title="Date",
    )
    infpgdp1yr: float | None = Field(
        default=None,
        description=(
            "One-year-ahead annual-average GDP price index inflation forecast. "
            "Computed from median forecasts of GDP price index levels (PGDP2 and PGDP6). "
            "Formula: ((PGDP6/PGDP2) - 1) * 100. Available from 1970:Q2."
        ),
        title="GDP Deflator Inflation (1-Year)",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    infcpi1yr: float | None = Field(
        default=None,
        description=(
            "One-year-ahead annual-average CPI inflation forecast. "
            "Computed as the geometric average of quarter-over-quarter median CPI forecasts "
            "(CPI3 to CPI6). Available from 1981:Q3."
        ),
        title="CPI Inflation (1-Year)",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    infcpi10yr: float | None = Field(
        default=None,
        description=(
            "Ten-year-ahead annual-average CPI inflation forecast. "
            "Expected average annual rate of CPI inflation over the next 10 years. "
            "Available from 1991:Q4."
        ),
        title="CPI Inflation (10-Year)",
        json_schema_extra={"x-unit_measurement": "percent"},
    )


class FederalReserveInflationExpectationsFetcher(
    Fetcher[
        FederalReserveInflationExpectationsQueryParams,
        list[FederalReserveInflationExpectationsData],
    ]
):
    """Federal Reserve Inflation Expectations Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveInflationExpectationsQueryParams:
        """Transform input parameters into query params."""
        return FederalReserveInflationExpectationsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveInflationExpectationsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Download the Excel data from the Philadelphia Fed."""
        try:
            return {"file": download_inflation_excel()}
        except Exception as e:  # pylint: disable=broad-except
            raise OpenBBError(e) from e

    @staticmethod
    def transform_data(
        query: FederalReserveInflationExpectationsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[FederalReserveInflationExpectationsData]:
        """Transform the Excel data into validated Pydantic models."""
        # pylint: disable=import-outside-toplevel
        from io import BytesIO  # noqa
        from openpyxl import load_workbook
        from pandas import DataFrame, to_datetime

        wb = load_workbook(
            filename=BytesIO(data["file"]),
            read_only=True,
            data_only=True,
            keep_vba=False,
        )
        ws = wb["INFLATION"]
        df = DataFrame(ws.values)
        df.columns = df.iloc[0]
        df = df.iloc[1:]
        wb.close()
        df.columns = df.columns.str.lower()
        quarter_to_month = {1: 1, 2: 4, 3: 7, 4: 10}
        df["date"] = to_datetime(
            df["year"].astype(int).astype(str)
            + "-"
            + df["quarter"].map(quarter_to_month).astype(str)
            + "-01"
        ).dt.date

        # Apply date filters
        if query.start_date:
            df = df[df["date"] >= query.start_date]

        if query.end_date:
            df = df[df["date"] <= query.end_date]

        df = (
            df[["date", "infpgdp1yr", "infcpi1yr", "infcpi10yr"]]
            .replace({"#N/A": None})
            .set_index("date")
            .sort_index()
            .dropna(how="all", axis=0)
            .reset_index()
        )

        results = [
            FederalReserveInflationExpectationsData.model_validate(row.to_dict())
            for _, row in df.iterrows()
        ]

        if not results:
            raise OpenBBError(
                "The query filters resulted in no data. "
                "Try again with different date parameters."
            )

        return results
