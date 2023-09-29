"""FRED US Yield Curve."""


from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from openbb_fred.utils.fred_base import Fred
from openbb_fred.utils.fred_helpers import (
    YIELD_CURVE_NOMINAL_RATES,
    YIELD_CURVE_REAL_RATES,
    YIELD_CURVE_SERIES_NOMINAL,
    YIELD_CURVE_SERIES_REAL,
)
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.us_yield_curve import (
    USYieldCurveData,
    USYieldCurveQueryParams,
)


class FREDYieldCurveQueryParams(USYieldCurveQueryParams):
    """Fred Yield Curve query."""


class FREDYieldCurveData(USYieldCurveData):
    """Fred Yield Curve data."""


class FREDYieldCurveFetcher(
    Fetcher[FREDYieldCurveQueryParams, List[Dict[str, List[FREDYieldCurveData]]]]
):
    """FRED Yield Curve Fetcher."""

    data_type = FREDYieldCurveData

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FREDYieldCurveQueryParams:
        return FREDYieldCurveQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FREDYieldCurveQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> List[Dict]:
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
        for series in fred_series.values():
            data = fred.get_series(series, start_date=start_date, **kwargs)

            if date:
                # if date is not empty, loop through the data and find the closest value
                value = sorted(
                    data,
                    key=lambda x: abs(
                        datetime.strptime(x["date"], "%Y-%m-%d").date() - date
                    ),
                )[0]["value"]
            else:
                # if date is empty, find the most recent date's value
                sorted_data = sorted(data, key=lambda x: x["date"], reverse=True)
                value = sorted_data[0]["value"] if sorted_data else None

            vals.append(value)
        yield_curve_data = []
        for maturity, rate in zip(years, vals):
            yield_curve_data.append({"maturity": maturity, "rate": rate})

        return yield_curve_data

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FREDYieldCurveData]:
        return [FREDYieldCurveData(**x) for x in data]
