"""FRED SOFR Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.sofr import SOFRData, SOFRQueryParams
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
    "x-frontend_multiply": 1e9,
    "x-widget_config": {
        "prefix": "$",
        "suffix": "B",
        "chartDataType": "excluded",
    },
}
INDEX_EXCLUDED_FROM_CHART: dict[str, Any] = {
    "x-widget_config": {"chartDataType": "excluded"}
}

SOFR_ID_TO_FIELD = {
    "SOFR": "rate",
    "SOFR1": "percentile_1",
    "SOFR25": "percentile_25",
    "SOFR75": "percentile_75",
    "SOFR99": "percentile_99",
    "SOFRVOL": "volume",
    "SOFR30DAYAVG": "average_30d",
    "SOFR90DAYAVG": "average_90d",
    "SOFR180DAYAVG": "average_180d",
    "SOFRINDEX": "index",
}


class FREDSOFRQueryParams(UseCacheQueryParams, SOFRQueryParams):
    """FRED SOFR Query."""

    frequency: (
        None
        | Literal[
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
    ) = Field(
        default=None,
        description="""
        Frequency aggregation to convert daily data to lower frequency.
            a = Annual
            q = Quarterly
            m = Monthly
            w = Weekly
            wef = Weekly, Ending Friday
            weth = Weekly, Ending Thursday
            wew = Weekly, Ending Wednesday
            wetu = Weekly, Ending Tuesday
            wem = Weekly, Ending Monday
            wesu = Weekly, Ending Sunday
            wesa = Weekly, Ending Saturday
            bwew = Biweekly, Ending Wednesday
            bwem = Biweekly, Ending Monday
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
    aggregation_method: None | Literal["avg", "sum", "eop"] = Field(
        default=None,
        description="""
        A key that indicates the aggregation method used for frequency aggregation.
            avg = Average
            sum = Sum
            eop = End of Period
        """,
        json_schema_extra={"choices": ["avg", "sum", "eop"]},
    )
    transform: (
        None | Literal["chg", "ch1", "pch", "pc1", "pca", "cch", "cca", "log"]
    ) = Field(
        default=None,
        description="""
        Transformation type
            None = No transformation
            chg = Change
            ch1 = Change from Year Ago
            pch = Percent Change
            pc1 = Percent Change from Year Ago
            pca = Compounded Annual Rate of Change
            cch = Continuously Compounded Rate of Change
            cca = Continuously Compounded Annual Rate of Change
            log = Natural Log
        """,
        json_schema_extra={
            "choices": ["chg", "ch1", "pch", "pc1", "pca", "cch", "cca", "log"]
        },
    )


class FREDSOFRData(SOFRData):
    """FRED SOFR Data."""

    __alias_dict__ = {
        "rate": "SOFR",
        "percentile_1": "SOFR1",
        "percentile_25": "SOFR25",
        "percentile_75": "SOFR75",
        "percentile_99": "SOFR99",
        "volume": "SOFRVOL",
        "average_30d": "SOFR30DAYAVG",
        "average_90d": "SOFR90DAYAVG",
        "average_180d": "SOFR180DAYAVG",
        "index": "SOFRINDEX",
    }

    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
        json_schema_extra=TIME_AXIS,
    )
    rate: float = Field(
        description="Effective federal funds rate.",
        json_schema_extra=PERCENT_SERIES,
    )
    percentile_1: float | None = Field(
        default=None,
        description="1st percentile of the distribution.",
        json_schema_extra=PERCENT_SERIES,
    )
    percentile_25: float | None = Field(
        default=None,
        description="25th percentile of the distribution.",
        json_schema_extra=PERCENT_SERIES,
    )
    percentile_75: float | None = Field(
        default=None,
        description="75th percentile of the distribution.",
        json_schema_extra=PERCENT_SERIES,
    )
    percentile_99: float | None = Field(
        default=None,
        description="99th percentile of the distribution.",
        json_schema_extra=PERCENT_SERIES,
    )
    volume: float | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("volume", "")
        + "The notional volume of transactions (Billions of $).",
        json_schema_extra=VOLUME_EXCLUDED_FROM_CHART,
    )
    average_30d: float | None = Field(
        default=None,
        description="30-Day Average SOFR",
        json_schema_extra=PERCENT_SERIES,
    )
    average_90d: float | None = Field(
        default=None,
        description="90-Day Average SOFR",
        json_schema_extra=PERCENT_SERIES,
    )
    average_180d: float | None = Field(
        default=None,
        description="180-Day Average SOFR",
        json_schema_extra=PERCENT_SERIES,
    )
    index: float | None = Field(
        default=None,
        description="SOFR index as 2018-04-02 = 1",
        json_schema_extra=INDEX_EXCLUDED_FROM_CHART,
    )

    @field_validator(
        "rate",
        "percentile_1",
        "percentile_25",
        "percentile_75",
        "percentile_99",
        "average_30d",
        "average_90d",
        "average_180d",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def normalize_percent(cls, v):
        """Normalize percent."""
        return float(v) if v else None


class FREDSOFRFetcher(Fetcher[FREDSOFRQueryParams, list[FREDSOFRData]]):
    """FRED SOFR Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FREDSOFRQueryParams:
        """Transform query."""
        return FREDSOFRQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FREDSOFRQueryParams, credentials: dict[str, str] | None, **kwargs: Any
    ) -> dict:
        """Extract data."""
        ids = list(SOFR_ID_TO_FIELD)
        try:
            response = await FredSeriesFetcher.fetch_data(
                dict(
                    symbol=",".join(ids),
                    start_date=query.start_date if query.start_date else "2018-04-02",
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
        query: FREDSOFRQueryParams, data: dict, **kwargs: Any
    ) -> AnnotatedResult[list[FREDSOFRData]]:
        """Transform data"""
        if not data:
            raise EmptyDataError("The request was returned empty.")
        return AnnotatedResult(
            result=[
                FREDSOFRData.model_validate(d)
                for d in data.get("data", [])
                if d.get("SOFR")
            ],
            metadata=data.get("metadata", {}),
        )
