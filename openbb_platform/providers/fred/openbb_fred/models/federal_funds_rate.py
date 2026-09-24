"""FRED Federal Funds Rate Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Literal

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.federal_funds_rate import (
    FederalFundsRateData,
    FederalFundsRateQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

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

EFFR_SERIES_IDS = {
    "rate": "DFF",
    "target_range_upper": "DFEDTARU",
    "target_range_lower": "DFEDTARL",
    "percentile_1": "EFFR1",
    "percentile_25": "EFFR25",
    "percentile_75": "EFFR75",
    "percentile_99": "EFFR99",
    "volume": "EFFRVOL",
}


class FredFederalFundsRateQueryParams(UseCacheQueryParams, FederalFundsRateQueryParams):
    """FRED Federal Funds Rate Query."""

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
    effr_only: bool = Field(
        default=False,
        description="Return data without quantiles, target ranges, and volume.",
    )


class FredFederalFundsRateData(FederalFundsRateData):
    """FRED Federal Funds Rate Data."""

    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
        json_schema_extra=TIME_AXIS,
    )
    rate: float = Field(
        description="Effective federal funds rate.",
        json_schema_extra=PERCENT_SERIES,
    )
    target_range_upper: float | None = Field(
        default=None,
        description="Upper bound of the target range.",
        json_schema_extra=PERCENT_SERIES,
    )
    target_range_lower: float | None = Field(
        default=None,
        description="Lower bound of the target range.",
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


class FredFederalFundsRateFetcher(
    Fetcher[FredFederalFundsRateQueryParams, list[FredFederalFundsRateData]]
):
    """FRED Federal Funds Rate Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FredFederalFundsRateQueryParams:
        """Transform query."""
        transformed_params = params.copy()
        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = (
                None if params.get("effr_only") else datetime(2016, 1, 1).date()
            )
        if params.get("end_date") is None:
            transformed_params["end_date"] = now
        return FredFederalFundsRateQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: FredFederalFundsRateQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the raw data."""
        ids = (
            "DFF"
            if query.effr_only is True
            else ",".join(list(EFFR_SERIES_IDS.values()))
        )
        try:
            response = await FredSeriesFetcher.fetch_data(
                dict(
                    symbol=ids,
                    start_date=query.start_date,
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
        query: FredFederalFundsRateQueryParams, data: dict, **kwargs: Any
    ) -> AnnotatedResult[list[FredFederalFundsRateData]]:
        """Transform and validate the data."""
        from pandas import DataFrame, to_datetime

        metadata = data.get("metadata", {})
        df = DataFrame(data.get("data", [])).dropna()
        if df.empty:
            raise EmptyDataError(
                "There was an error with the request and it was returned empty."
            )
        col_map = {v: k for k, v in EFFR_SERIES_IDS.items()}
        df.date = df.date.apply(to_datetime)
        df = df.set_index("date")
        df = df.rename(columns=col_map)
        for col in df.columns:
            df[col] = df[col].astype(float)
        records = df.reset_index().to_dict(orient="records")

        return AnnotatedResult(
            result=[FredFederalFundsRateData.model_validate(d) for d in records],
            metadata={col_map[k]: v for k, v in metadata.items()},
        )
