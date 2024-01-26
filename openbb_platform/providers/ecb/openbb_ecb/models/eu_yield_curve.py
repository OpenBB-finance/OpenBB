"""Euro Area Yield Curve Model."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.eu_yield_curve import (
    EUYieldCurveData,
    EUYieldCurveQueryParams,
)
from openbb_ecb.utils.ecb_helpers import get_series_data
from pydantic import Field, field_validator


class ECBEUYieldCurveQueryParams(EUYieldCurveQueryParams):
    """Euro Area Yield Curve Query."""

    rating: Literal["A", "C"] = Field(
        default="A",
        description="The rating type.",
    )


class ECBEUYieldCurveData(EUYieldCurveData):
    """Euro Area Yield Curve Data."""

    __alias_dict__ = {
        "rate": "OBS",
    }

    @field_validator("OBS", mode="before", check_fields=False)
    @classmethod
    def value_validate(cls, v):
        """Validate rate."""
        try:
            return float(v)
        except ValueError:
            return None


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
    def extract_data(
        query: ECBEUYieldCurveQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> list:
        """Extract data."""
        # Check that the date is in the past
        today = datetime.today().date()
        if query.date and query.date >= today:
            raise ValueError("Date must be in the past")

        if not query.date:
            date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            date = query.date.strftime("%Y-%m-%d")

        yield_suffixes = {
            "spot_rate": "SR_",
            "instantaneous_forward": "IF_",
            "par_yield": "PY",
        }
        yield_type = f"YC.B.U2.EUR.4F.G_N_{query.rating}.SV_C_YM." + yield_suffixes.get(
            query.yield_curve_type, ""
        )
        # Add the maturities
        series_id = [f"{yield_type}{m}M" for m in [3, 6]]
        series_id += [f"{yield_type}{y}Y" for y in [1, 2, 3, 5, 7, 10, 20, 30]]

        data = []

        for id_ in series_id:
            d = get_series_data(id_, date)
            maturity = id_.split("_")[-1]

            for item in d:
                item["maturity"] = maturity

            data.extend(d)

        return data

    # pylint: disable=unused-argument
    @staticmethod
    def transform_data(
        query: ECBEUYieldCurveQueryParams, data: list, **kwargs: Any
    ) -> List[ECBEUYieldCurveData]:
        """Transform data."""
        return [ECBEUYieldCurveData.model_validate(d) for d in data]
