"""FRED Euro Short Term Rate Standard Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.euro_short_term_rate import (
    EuroShortTermRateData,
    EuroShortTermRateQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_fred.models.series import FredSeriesFetcher
from openbb_fred.utils.api import unwrap_series
from openbb_fred.utils.query import UseCacheQueryParams

TIME_AXIS: dict[str, Any] = {"x-widget_config": {"chartDataType": "time"}}
PERCENT_SERIES: dict[str, Any] = {
    "x-unit_measurement": "percent",
    "x-widget_config": {"chartDataType": "series"},
}
VOLUME_EXCLUDED_FROM_CHART: dict[str, Any] = {
    "x-unit_measurement": "currency",
    "x-frontend_multiply": 1e6,
    "x-widget_config": {"chartDataType": "excluded"},
}
COUNT_EXCLUDED_FROM_CHART: dict[str, Any] = {
    "x-widget_config": {"chartDataType": "excluded"}
}
VOLUME_SHARE_EXCLUDED_FROM_CHART: dict[str, Any] = {
    "x-unit_measurement": "percent",
    "x-widget_config": {"chartDataType": "excluded"},
}


class FredEuroShortTermRateQueryParams(
    UseCacheQueryParams, EuroShortTermRateQueryParams
):
    """FRED Euro Short Term Rate Query."""

    frequency: (
        Literal[
            "a",
            "q",
            "m",
            "w",
            "wef",
            "weth",
            "wew",
            "wetu",
            "wem",
            "wesu",
            "wesa",
            "bwew",
            "bwem",
        ]
        | None
    ) = Field(
        default=None,
        description="""Frequency aggregation to convert daily data to lower frequency.
        \n    a = Annual
        \n    q = Quarterly
        \n    m = Monthly
        \n    w = Weekly
        \n    d = Daily
        \n    wef = Weekly, Ending Friday
        \n    weth = Weekly, Ending Thursday
        \n    wew = Weekly, Ending Wednesday
        \n    wetu = Weekly, Ending Tuesday
        \n    wem = Weekly, Ending Monday
        \n    wesu = Weekly, Ending Sunday
        \n    wesa = Weekly, Ending Saturday
        \n    bwew = Biweekly, Ending Wednesday
        \n    bwem = Biweekly, Ending Monday
        """,
        json_schema_extra={
            "choices": [
                "a",
                "q",
                "m",
                "w",
                "wef",
                "weth",
                "wew",
                "wetu",
                "wem",
                "wesu",
                "wesa",
                "bwew",
                "bwem",
            ]
        },
    )
    aggregation_method: Literal["avg", "sum", "eop"] | None = Field(
        default=None,
        description="""A key that indicates the aggregation method used for frequency aggregation.
        \n    avg = Average
        \n    sum = Sum
        \n    eop = End of Period
        """,
        json_schema_extra={"choices": ["avg", "sum", "eop"]},
    )
    transform: (
        Literal["chg", "ch1", "pch", "pc1", "pca", "cch", "cca", "log"] | None
    ) = Field(
        default=None,
        description="""Transformation type
        \n    None = No transformation
        \n    chg = Change
        \n    ch1 = Change from Year Ago
        \n    pch = Percent Change
        \n    pc1 = Percent Change from Year Ago
        \n    pca = Compounded Annual Rate of Change
        \n    cch = Continuously Compounded Rate of Change
        \n    cca = Continuously Compounded Annual Rate of Change
        \n    log = Natural Log
        """,
        json_schema_extra={
            "choices": ["chg", "ch1", "pch", "pc1", "pca", "cch", "cca", "log"]
        },
    )


class FredEuroShortTermRateData(EuroShortTermRateData):
    """FRED Euro Short Term Rate Data."""

    __alias_dict__ = {
        "rate": "ECBESTRVOLWGTTRMDMNRT",
        "transactions": "ECBESTRNUMTRANS",
        "number_of_banks": "ECBESTRNUMACTBANKS",
        "volume": "ECBESTRTOTVOL",
        "large_bank_share_of_volume": "ECBESTRSHRVOL5LRGACTBNK",
        "percentile_75": "ECBESTRRT75THPCTVOL",
        "percentile_25": "ECBESTRRT25THPCTVOL",
    }

    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
        json_schema_extra=TIME_AXIS,
    )
    rate: float = Field(
        description="Volume-weighted trimmed mean rate.",
        json_schema_extra=PERCENT_SERIES,
    )
    percentile_25: float | None = Field(
        default=None,
        description="Rate at 25th percentile of volume.",
        json_schema_extra=PERCENT_SERIES,
    )
    percentile_75: float | None = Field(
        default=None,
        description="Rate at 75th percentile of volume.",
        json_schema_extra=PERCENT_SERIES,
    )
    volume: float | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("volume", "") + " (Millions of €EUR).",
        json_schema_extra=VOLUME_EXCLUDED_FROM_CHART,
    )
    transactions: int | None = Field(
        default=None,
        description="Number of transactions.",
        json_schema_extra=COUNT_EXCLUDED_FROM_CHART,
    )
    number_of_banks: int | None = Field(
        default=None,
        description="Number of active banks.",
        json_schema_extra=COUNT_EXCLUDED_FROM_CHART,
    )
    large_bank_share_of_volume: float | None = Field(
        default=None,
        description="The percent of volume attributable to the 5 largest active banks.",
        json_schema_extra=VOLUME_SHARE_EXCLUDED_FROM_CHART,
    )

    @field_validator(
        "rate",
        "percentile_25",
        "percentile_75",
        "large_bank_share_of_volume",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def normalize_percent(cls, v):
        """Normalize percent."""
        return float(v) if v else None


class FredEuroShortTermRateFetcher(
    Fetcher[FredEuroShortTermRateQueryParams, list[FredEuroShortTermRateData]]
):
    """FRED Euro Short Term Rate Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FredEuroShortTermRateQueryParams:
        """Transform query"""
        return FredEuroShortTermRateQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FredEuroShortTermRateQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract data"""

        ids = [
            "ECBESTRVOLWGTTRMDMNRT",
            "ECBESTRNUMTRANS",
            "ECBESTRNUMACTBANKS",
            "ECBESTRTOTVOL",
            "ECBESTRSHRVOL5LRGACTBNK",
            "ECBESTRRT75THPCTVOL",
            "ECBESTRRT25THPCTVOL",
        ]
        try:
            response = await FredSeriesFetcher.fetch_data(
                dict(
                    symbol=",".join(ids),
                    start_date=query.start_date if query.start_date else "2019-10-02",
                    end_date=query.end_date,
                    frequency=query.frequency,
                    aggregation_method=query.aggregation_method,
                    transform=query.transform,
                    use_cache=query.use_cache,
                ),
                credentials,
            )
        except Exception as e:
            raise e from e

        rows, metadata = unwrap_series(response)

        return {
            "metadata": metadata,
            "data": [d.model_dump() for d in rows],
        }

    @staticmethod
    def transform_data(
        query: FredEuroShortTermRateQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> AnnotatedResult[list[FredEuroShortTermRateData]]:
        """Transform data"""
        if not data:
            raise EmptyDataError("The request was returned empty.")
        return AnnotatedResult(
            result=[
                FredEuroShortTermRateData.model_validate(d)
                for d in data.get("data", [])
                if d.get("ECBESTRVOLWGTTRMDMNRT")
            ],
            metadata=data.get("metadata", {}),
        )
