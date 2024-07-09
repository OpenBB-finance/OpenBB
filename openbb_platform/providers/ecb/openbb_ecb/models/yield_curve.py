"""ECB Yield Curve Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.yield_curve import (
    YieldCurveData,
    YieldCurveQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


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
        description="If true, cache the request for four hours.",
    )


class ECBYieldCurveData(YieldCurveData):
    """ECB Yield Curve Data."""

    @field_validator("rate", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Normalize percent."""
        return float(v) / 100 if v else None


class ECBYieldCurveFetcher(
    Fetcher[
        ECBYieldCurveQueryParams,
        List[ECBYieldCurveData],
    ]
):
    """ECB Yield Curve Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> ECBYieldCurveQueryParams:
        """Transform query."""
        return ECBYieldCurveQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ECBYieldCurveQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract data."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from aiohttp_client_cache import SQLiteBackend  # noqa
        from aiohttp_client_cache.session import CachedSession  # noqa
        from openbb_core.app.utils import get_user_cache_directory  # noqa
        from openbb_core.provider.utils.helpers import amake_request  # noqa
        from openbb_ecb.utils.yield_curve_series import (
            MATURITIES,
            get_yield_curve_ids,
        )  # noqa

        results: List = []

        IDS = get_yield_curve_ids(
            rating=query.rating,
            yield_curve_type=query.yield_curve_type,
        )
        YIELD_CURVE = IDS["SERIES_IDS"]

        BASE_URL = "https://data.ecb.europa.eu/data-detail-api"

        async def get_one(maturity, use_cache):
            """Each maturity is a separate download."""
            url = f"{BASE_URL}/{YIELD_CURVE[maturity]}"
            response: Union[Dict, List[Dict]] = []
            if use_cache is True:
                cache_dir = f"{get_user_cache_directory()}/http/ecb_yield_curve"
                async with CachedSession(
                    cache=SQLiteBackend(cache_dir, expire_after=3600 * 4)
                ) as session:
                    try:
                        response = await amake_request(
                            url, session=session  # type: ignore
                        )
                    finally:
                        await session.close()
            else:
                response = await amake_request(url=url)
            if not response:
                raise OpenBBError("No data was returned.")
            if isinstance(response, List):
                for item in response:
                    d = {
                        "date": item.get("PERIOD"),
                        "maturity": maturity,
                        "rate": item.get("OBS_VALUE_AS_IS"),
                    }
                    results.append(d)

        tasks = [get_one(maturity, query.use_cache) for maturity in MATURITIES]

        await asyncio.gather(*tasks)

        return results

    @staticmethod
    def transform_data(
        query: ECBYieldCurveQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[ECBYieldCurveData]:
        """Transform data."""
        # pylint: disable=import-outside-toplevel
        from openbb_ecb.utils.yield_curve_series import MATURITIES  # noqa
        from pandas import Categorical, DataFrame, DatetimeIndex  # noqa

        if not data:
            raise EmptyDataError("The request was returned empty.")
        dates = (
            query.date.split(",")
            if query.date
            else [datetime.now().strftime("%Y-%m-%d")]
        )
        dates_list = DatetimeIndex(dates)

        # Find the nearest date to the requested one.
        df = DataFrame(data).set_index("date").query("`rate`.notnull()")
        df.index = DatetimeIndex(df.index)
        df_unique_dates = df[
            ~df.index.duplicated(keep="first")
        ].sort_index()  # DataFrame with unique dates
        nearest_dates = [df_unique_dates.index.asof(date) for date in dates_list]
        # Filter for only the nearest dates
        df = df[df.index.isin(nearest_dates)]

        # Flatten the DataFrame
        flattened_data = df.reset_index().sort_values("date")
        flattened_data = flattened_data.rename(columns={"index": "date"}).sort_values(
            "date"
        )
        flattened_data["maturity"] = Categorical(
            flattened_data["maturity"], categories=MATURITIES, ordered=True
        )
        flattened_data = flattened_data.sort_values(
            by=["date", "maturity"]
        ).reset_index(drop=True)
        flattened_data.loc[:, "date"] = flattened_data["date"].dt.strftime("%Y-%m-%d")
        records = flattened_data.to_dict(orient="records")

        return [ECBYieldCurveData.model_validate(d) for d in records]
