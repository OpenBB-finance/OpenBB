"""ECB Yield Curve Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.yield_curve import (
    YieldCurveData,
    YieldCurveQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class ECBYieldCurveQueryParams(YieldCurveQueryParams):
    """ECB Yield Curve Query Params."""

    __json_schema_extra__ = {"date": {"multiple_items_allowed": True}}

    rating: Literal["aaa", "all_ratings"] = Field(
        default="aaa",
        description="The rating type, either 'aaa' or 'all_ratings'.",
    )
    yield_curve_type: Literal["spot_rate", "instantaneous_forward", "par_yield"] = (
        Field(
            default="spot_rate",
            description="The yield curve type.",
        )
    )
    use_cache: bool = Field(
        default=True,
        description="If true, cache parsed results on disk for the dataset TTL.",
    )


class ECBYieldCurveData(YieldCurveData):
    """ECB Yield Curve Data."""


class ECBYieldCurveFetcher(
    Fetcher[
        ECBYieldCurveQueryParams,
        list[ECBYieldCurveData],
    ]
):
    """ECB Yield Curve Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ECBYieldCurveQueryParams:
        """Transform query."""
        return ECBYieldCurveQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ECBYieldCurveQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Fetch the raw windowed yield-curve observations from the ECB data API."""
        # pylint: disable=import-outside-toplevel
        import asyncio
        from datetime import timedelta

        from openbb_ecb.utils.data_cache import cached_records, make_key
        from openbb_ecb.utils.query_builder import fetch_sdmx_data
        from openbb_ecb.utils.yield_curve_series import get_yield_curve_key

        key, _, _ = get_yield_curve_key(
            rating=query.rating,
            yield_curve_type=query.yield_curve_type,
        )
        dates = (
            str(query.date).split(",")
            if query.date
            else [datetime.now().strftime("%Y-%m-%d")]
        )

        async def get_window(date_str: str) -> list[dict]:
            """Fetch a window around a requested date."""
            target = datetime.strptime(date_str.strip(), "%Y-%m-%d")
            start = (target - timedelta(days=14)).strftime("%Y-%m-%d")
            end = (target + timedelta(days=1)).strftime("%Y-%m-%d")

            async def loader() -> list[dict]:
                return await fetch_sdmx_data(
                    "YC", key, start_date=start, end_date=end, raise_empty=False
                )

            cache_key = make_key("yield_curve", key=key, start=start, end=end)
            return await cached_records(
                "yield_curve", cache_key, loader, use_cache=query.use_cache
            )

        batches = await asyncio.gather(*[get_window(d) for d in dates])
        return [record for batch in batches for record in batch]

    @staticmethod
    def transform_data(
        query: ECBYieldCurveQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[ECBYieldCurveData]:
        """Map maturities, pick the nearest dates, scale, and validate."""
        # pylint: disable=import-outside-toplevel
        from openbb_ecb.utils.yield_curve_series import (  # noqa
            MATURITIES,
            get_yield_curve_key,
        )
        from pandas import Categorical, DataFrame, DatetimeIndex  # noqa

        _, datatype_to_maturity, _ = get_yield_curve_key(
            rating=query.rating,
            yield_curve_type=query.yield_curve_type,
        )
        seen: dict[tuple, float] = {}
        for record in data:
            maturity = datatype_to_maturity.get(record["series_key"].split(".")[-1])
            if maturity and record.get("OBS_VALUE") is not None:
                seen[(record["date"], maturity)] = record["OBS_VALUE"]
        rows = [
            {"date": date, "maturity": maturity, "rate": rate}
            for (date, maturity), rate in seen.items()
        ]

        if not rows:
            raise EmptyDataError("The request was returned empty.")
        data = rows
        dates = (
            str(query.date).split(",")
            if query.date
            else [datetime.now().strftime("%Y-%m-%d")]
        )
        dates_list = DatetimeIndex(dates)

        df = DataFrame(data).set_index("date").query("`rate`.notnull()")
        df.index = DatetimeIndex(df.index)
        df_unique_dates = df[~df.index.duplicated(keep="first")].sort_index()
        nearest_dates = [df_unique_dates.index.asof(date) for date in dates_list]
        df = df[df.index.isin(nearest_dates)]

        flattened_data = df.reset_index().sort_values("date")
        flattened_data = flattened_data.rename(columns={"index": "date"}).sort_values(
            "date"
        )
        flattened_data["maturity"] = Categorical(
            flattened_data.maturity, categories=MATURITIES, ordered=True
        )
        flattened_data = flattened_data.sort_values(
            by=["date", "maturity"]
        ).reset_index(drop=True)
        flattened_data["date"] = flattened_data.date.dt.strftime("%Y-%m-%d")
        flattened_data["rate"] = flattened_data.rate.astype(float).div(100)
        records = flattened_data.to_dict(orient="records")

        return [ECBYieldCurveData.model_validate(d) for d in records]
