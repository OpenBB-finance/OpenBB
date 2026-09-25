"""FRED University of Michigan Survey Model."""

from datetime import datetime
from typing import Any, Literal

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.university_of_michigan import (
    UofMichiganData,
    UofMichiganQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_fred.models.series import FredSeriesFetcher
from openbb_fred.utils.api import unwrap_series
from openbb_fred.utils.query import UseCacheQueryParams

PERCENT_COLUMN: dict[str, Any] = {"x-unit_measurement": "percent"}


class FredUofMichiganQueryParams(UseCacheQueryParams, UofMichiganQueryParams):
    """FRED University of Michigan Survey Query. Data from FRED is delayed by 1 month."""

    frequency: Literal["annual", "quarter"] | None = Field(
        default=None,
        description="Frequency aggregation to convert monthly data to lower frequency. None is monthly.",
        json_schema_extra={
            "choices": [
                "annual",
                "quarter",
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


class FredUofMichiganData(UofMichiganData):
    """FRED University of Michigan Survey Data."""

    inflation_expectation: float | None = Field(
        default=None,
        description="Median expected price change next 12 months, Surveys of Consumers.",
        json_schema_extra=PERCENT_COLUMN,
    )


class FredUofMichiganFetcher(
    Fetcher[FredUofMichiganQueryParams, list[FredUofMichiganData]]
):
    """FRED University of Michigan Survey Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FredUofMichiganQueryParams:
        """Transform query."""
        return FredUofMichiganQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FredUofMichiganQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract data."""
        ids = ["UMCSENT", "MICH"]
        frequency = query.frequency[:1].lower() if query.frequency else None
        if (
            query.start_date and query.start_date < datetime(1978, 1, 1).date()
        ) or not query.start_date:
            ids = ids + ["UMCSENT1"]
        try:
            response = await FredSeriesFetcher.fetch_data(
                dict(
                    symbol=",".join(ids),
                    start_date=query.start_date,
                    end_date=query.end_date,
                    transform=query.transform,
                    frequency=frequency,
                    aggregation_method=query.aggregation_method,
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
        query: FredUofMichiganQueryParams, data: dict, **kwargs: Any
    ) -> AnnotatedResult[list[FredUofMichiganData]]:
        """Transform data."""
        from pandas import DataFrame

        df = DataFrame(data.get("data", []))
        if df.empty:
            raise EmptyDataError(
                "There was an error with the request and was returned empty."
            )
        metadata = data.get("metadata", {})
        if "UMCSENT1" in df.columns:
            df["UMCSENT"] = df["UMCSENT"].fillna(df["UMCSENT1"])
            df = df.drop(columns=["UMCSENT1"])
            metadata.pop("UMCSENT1", None)

        df = df.rename(
            columns={"UMCSENT": "consumer_sentiment", "MICH": "inflation_expectation"}
        )
        records = (
            df.sort_values(by="date")
            .fillna("N/A")
            .replace("N/A", None)
            .to_dict(orient="records")
        )
        return AnnotatedResult(
            result=[FredUofMichiganData.model_validate(r) for r in records],
            metadata=metadata,
        )
