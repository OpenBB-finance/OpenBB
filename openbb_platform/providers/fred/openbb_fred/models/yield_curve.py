"""FRED Yield Curve Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.yield_curve import (
    YieldCurveData,
    YieldCurveQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, computed_field

from openbb_fred.models.series import FredSeriesFetcher
from openbb_fred.utils.api import unwrap_series
from openbb_fred.utils.fred_helpers import YIELD_CURVES
from openbb_fred.utils.query import UseCacheQueryParams

CATEGORY_COLUMN: dict[str, Any] = {"x-widget_config": {"chartDataType": "category"}}
SERIES_PERCENT_COLUMN: dict[str, Any] = {
    "x-unit_measurement": "percent",
    "x-widget_config": {"chartDataType": "series"},
}
EXCLUDED_COLUMN: dict[str, Any] = {"x-widget_config": {"chartDataType": "excluded"}}


class FREDYieldCurveQueryParams(UseCacheQueryParams, YieldCurveQueryParams):
    """FRED Yield Curve Query."""

    __json_schema_extra__ = {"date": {"multiple_items_allowed": True}}

    yield_curve_type: Literal[
        "nominal",
        "real",
        "breakeven",
        "treasury_minus_fed_funds",
        "corporate_spot",
        "corporate_par",
    ] = Field(
        default="nominal",
        description="Yield curve type."
        + " Nominal and Real Rates are available daily, others are monthly."
        + " The closest date to the requested date will be returned.",
        json_schema_extra={
            "choices": [
                "nominal",
                "real",
                "breakeven",
                "treasury_minus_fed_funds",
                "corporate_spot",
                "corporate_par",
            ]
        },
    )


class FREDYieldCurveData(YieldCurveData):
    """FRED Yield Curve Data."""

    date: dateType | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("date", ""),
        json_schema_extra=EXCLUDED_COLUMN,
    )
    maturity: str = Field(
        description="Maturity length of the security.",
        json_schema_extra=CATEGORY_COLUMN,
    )
    rate: float | None = Field(
        default=None,
        description="The yield of the security at the given maturity,"
        + " as published by FRED.",
        json_schema_extra=SERIES_PERCENT_COLUMN,
    )

    @computed_field(
        description="Maturity length, in years, as a decimal.",
        return_type=float | None,
        json_schema_extra=EXCLUDED_COLUMN,
    )
    @property
    def maturity_years(self) -> float | None:
        """Get the maturity in years as a decimal."""
        return YieldCurveData.maturity_years.fget(self)


class FREDYieldCurveFetcher(
    Fetcher[FREDYieldCurveQueryParams, list[FREDYieldCurveData]]
):
    """Transform the query, extract and transform the data from the FRED endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FREDYieldCurveQueryParams:
        """Transform query."""
        return FREDYieldCurveQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FREDYieldCurveQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract data."""
        api_key = (credentials or {}).get("fred_api_key") or ""
        series_ids = ",".join(list(YIELD_CURVES[query.yield_curve_type]))
        fetcher = FredSeriesFetcher()
        data = await fetcher.fetch_data(
            {"symbol": series_ids, "use_cache": query.use_cache},
            {"fred_api_key": api_key},
        )

        rows, _ = unwrap_series(data)

        if not rows:
            raise EmptyDataError("The request was returned empty.")

        return [d.model_dump() for d in rows]

    @staticmethod
    def transform_data(
        query: FREDYieldCurveQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FREDYieldCurveData]:
        """Transform data."""
        from pandas import Categorical, DataFrame, DatetimeIndex

        df = DataFrame(data).set_index("date").sort_index()
        df.index = df.index.astype(str)
        dates = str(query.date).split(",") if query.date else [df.index.max()]
        df.index = DatetimeIndex(df.index)
        dates_list = DatetimeIndex(dates)
        maturity_dict = YIELD_CURVES[query.yield_curve_type]
        df = df.rename(columns=maturity_dict)
        df.columns.name = "maturity"

        nearest_dates = [df.index.asof(date) for date in dates_list]

        df = df[df.index.isin(nearest_dates)]

        df = df.fillna("N/A").replace("N/A", None)

        flattened_data = df.reset_index().melt(
            id_vars="date", var_name="maturity", value_name="rate"
        )
        flattened_data = flattened_data.sort_values("date")
        flattened_data["maturity"] = Categorical(
            flattened_data["maturity"],
            categories=list(maturity_dict.values()),
            ordered=True,
        )
        flattened_data["rate"] = flattened_data["rate"].astype(float)
        flattened_data = flattened_data.sort_values(
            by=["date", "maturity"]
        ).reset_index(drop=True)
        flattened_data["date"] = flattened_data["date"].dt.strftime("%Y-%m-%d")
        records = flattened_data.to_dict(orient="records")

        return [FREDYieldCurveData.model_validate(d) for d in records]
