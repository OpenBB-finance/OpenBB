"""FRED US Yield Curve Model."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.us_yield_curve import (
    USYieldCurveData,
    USYieldCurveQueryParams,
)
from openbb_fred.utils.fred_base import Fred
from openbb_fred.utils.fred_helpers import (
    YIELD_CURVE_NOMINAL_RATES,
    YIELD_CURVE_REAL_RATES,
    YIELD_CURVE_SERIES_NOMINAL,
    YIELD_CURVE_SERIES_REAL,
)


class FREDYieldCurveQueryParams(USYieldCurveQueryParams):
    """FRED US Yield Curve Query."""


class FREDYieldCurveData(USYieldCurveData):
    """FRED US Yield Curve Data."""


class FREDYieldCurveFetcher(
    Fetcher[FREDYieldCurveQueryParams, List[Dict[str, List[FREDYieldCurveData]]]]
):
    """Transform the query, extract and transform the data from the FRED endpoints."""

    data_type = FREDYieldCurveData

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FREDYieldCurveQueryParams:
        """Transform query."""
        return FREDYieldCurveQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FREDYieldCurveQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> List[Dict]:
        """Extract data."""
        api_key = credentials.get("fred_api_key") if credentials else ""
        date = query.date
        if query.inflation_adjusted:
            fred_series = YIELD_CURVE_SERIES_REAL
            years = YIELD_CURVE_REAL_RATES
        else:
            fred_series = YIELD_CURVE_SERIES_NOMINAL
            years = YIELD_CURVE_NOMINAL_RATES

        start_date = (
            date - timedelta(days=30) if date else datetime.now() - timedelta(days=30)
        )

        fred = Fred(api_key)
        vals = []
        value = None

        for series in fred_series.values():
            data = fred.get_series(series, start_date=start_date, **kwargs)

            if date:
                # if date is not empty, loop through the data and find the closest value
                sorted_data = sorted(
                    data,
                    key=lambda item: abs(
                        (date - datetime.strptime(item["date"], "%Y-%m-%d").date()).days
                    ),
                )
                for item in sorted_data:
                    if item.get("value") and item["value"] != ".":
                        value = float(item["value"])
                        break

            else:
                # if date is empty, find the most recent date's value
                sorted_data = sorted(data, key=lambda x: x["date"], reverse=True)
                value = float(sorted_data[0]["value"]) if sorted_data else None

            if isinstance(value, (float, int)):
                vals.append(value)

        yield_curve_data = []
        for maturity, rate in zip(years, vals):
            yield_curve_data.append({"maturity": maturity, "rate": rate})

        return yield_curve_data

    @staticmethod
    def transform_data(
        query: FREDYieldCurveQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FREDYieldCurveData]:
        """Transform data."""
        return [FREDYieldCurveData(**x) for x in data]
