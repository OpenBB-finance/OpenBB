"""Euro Area Yield Curve Model."""

# pylint: disable=unused-argument

import asyncio
import warnings
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.eu_yield_curve import (
    EUYieldCurveData,
    EUYieldCurveQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from openbb_ecb.utils.yield_curve_series import get_yield_curve_ids
from pandas import DataFrame, to_datetime
from pydantic import Field, field_validator

_warn = warnings.warn


class ECBEUYieldCurveQueryParams(EUYieldCurveQueryParams):
    """ECB Yield Curve Query Params."""

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


class ECBEUYieldCurveData(EUYieldCurveData):
    """ECB Yield Curve Data."""

    @field_validator("rate", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Normalize percent."""
        return float(v) / 100 if v else None


class ECBEUYieldCurveFetcher(
    Fetcher[
        ECBEUYieldCurveQueryParams,
        List[ECBEUYieldCurveData],
    ]
):
    """ECB Yield Curve Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> ECBEUYieldCurveQueryParams:
        """Transform query."""
        if params.get("date") is None:
            params["date"] = datetime.now().date()
        return ECBEUYieldCurveQueryParams(**params)

    # pylint: disable=unused-argument
    @staticmethod
    async def aextract_data(
        query: ECBEUYieldCurveQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract data."""

        results = []

        IDS = get_yield_curve_ids(
            rating=query.rating,
            yield_curve_type=query.yield_curve_type,
        )
        YIELD_CURVE = IDS["SERIES_IDS"]
        MATURITIES = IDS["MATURITIES"]

        maturities = list(MATURITIES.keys())

        BASE_URL = "https://data.ecb.europa.eu/data-detail-api"

        async def get_one(maturity):
            """Each maturity is a separate download."""
            url = f"{BASE_URL}/{YIELD_CURVE[maturity]}"
            response = await amake_request(url=url, timeout=10)
            if isinstance(response, List):
                for item in response:
                    d = {
                        "date": item.get("PERIOD"),
                        "maturity": MATURITIES[maturity],
                        "rate": item.get("OBS_VALUE_AS_IS"),
                    }

                    results.append(d)

        tasks = [get_one(maturity) for maturity in maturities]

        await asyncio.gather(*tasks)

        return results

    # pylint: disable=unused-argument
    @staticmethod
    def transform_data(
        query: ECBEUYieldCurveQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[ECBEUYieldCurveData]:
        """Transform data."""

        if not data:
            raise EmptyDataError()

        # Find the nearest date to the requested one.
        df = DataFrame(data).set_index("date").query("`rate`.notnull()")
        df.index = to_datetime(df.index)
        dates = df.index.unique().tolist()
        date = to_datetime(query.date)
        nearest_date = min(dates, key=lambda d: abs(d - date)).strftime("%Y-%m-%d")
        df.index = df.index.astype(str)

        if nearest_date != date.strftime("%Y-%m-%d"):
            _warn(f"Using nearest date: {nearest_date}")

        df.index = df.index.astype(str)
        results = (
            df.filter(like=nearest_date, axis=0)
            .sort_values("maturity")
            .reset_index(drop=True)
        )

        return [
            ECBEUYieldCurveData.model_validate(d)
            for d in results.to_dict(orient="records")
        ]
