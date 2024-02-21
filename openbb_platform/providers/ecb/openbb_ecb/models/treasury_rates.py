"""Euro Area Yield Curve Model."""

# pylint: disable=unused-argument

import asyncio
import warnings
from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.eu_yield_curve import (
    EUYieldCurveData,
    EUYieldCurveQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from openbb_ecb.utils.ecb_helpers import get_yield_curve_ids
from pandas import DataFrame
from pydantic import Field, field_validator

_warn = warnings.warn


class ECBEUYieldCurveQueryParams(EUYieldCurveQueryParams):
    """Euro Area Yield Curve Query."""

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
    """Euro Area Yield Curve Data."""


class ECBEUYieldCurveFetcher(
    Fetcher[
        ECBEUYieldCurveQueryParams,
        List[ECBEUYieldCurveData],
    ]
):
    """Transform the query, extract and transform the data from the ECB endpoints."""

    data_type = ECBEUYieldCurveData

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> ECBEUYieldCurveQueryParams:
        """Transform query."""
        return ECBEUYieldCurveQueryParams(**params)

    # pylint: disable=unused-argument
    @staticmethod
    async def aextract_data(
        query: ECBEUYieldCurveQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> list:
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

        urls = [f"{BASE_URL}/{YIELD_CURVE[maturity]}" for maturity in MATURITIES]

        async def get_one(maturity):
            """Callback for response."""
            url = f"{BASE_URL}/{YIELD_CURVE[maturity]}"
            print(url)
            response = await amake_request(url=url)
            if isinstance(response, List):
                result = []
                for item in response:
                    d = {
                        "date": item.get("PERIOD"),
                        "maturity": maturity,
                        "rate": item.get("OBS_VALUE_AS_IS"),
                    }

                    results.append(d)

        tasks = [get_one(maturity) for maturity in maturities]

        await asyncio.gather(*tasks)

        return results

    # pylint: disable=unused-argument
    @staticmethod
    def transform_data(
        query: ECBEUYieldCurveQueryParams, data: list, **kwargs: Any
    ) -> List[ECBEUYieldCurveData]:
        """Transform data."""
        return [ECBEUYieldCurveData.model_validate(d) for d in data]
