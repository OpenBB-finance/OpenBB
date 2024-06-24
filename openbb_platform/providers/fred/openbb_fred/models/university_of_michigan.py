"""FRED University of Michigan Survey Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.university_of_michigan import (
    UofMichiganData,
    UofMichiganQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_fred.models.series import FredSeriesFetcher
from pydantic import Field


class FredUofMichiganQueryParams(UofMichiganQueryParams):
    """FRED University of Michigan Survey Query. Data from FRED is delayed by 1 month."""

    frequency: Optional[Literal["annual", "quarter"]] = Field(
        default=None,
        description="Frequency aggregation to convert monthly data to lower frequency. None is monthly.",
        json_schema_extra={
            "choices": [
                "annual",
                "quarter",
            ]
        },
    )
    aggregation_method: Optional[Literal["avg", "sum", "eop"]] = Field(
        default=None,
        description="""A key that indicates the aggregation method used for frequency aggregation.
        \n    avg = Average
        \n    sum = Sum
        \n    eop = End of Period
        """,
        json_schema_extra={"choices": ["avg", "sum", "eop"]},
    )
    transform: Optional[
        Literal["chg", "ch1", "pch", "pc1", "pca", "cch", "cca", "log"]
    ] = Field(
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


class FredUofMichiganFetcher(
    Fetcher[FredUofMichiganQueryParams, List[FredUofMichiganData]]
):
    """FRED University of Michigan Survey Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FredUofMichiganQueryParams:
        """Transform query."""
        return FredUofMichiganQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FredUofMichiganQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> Dict:
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
                ),
                credentials,
            )
        except Exception as e:
            raise e from e

        return {
            "metadata": response.metadata,
            "data": [d.model_dump() for d in response.result],
        }

    @staticmethod
    def transform_data(
        query: FredUofMichiganQueryParams, data: Dict, **kwargs: Any
    ) -> List[FredUofMichiganData]:
        """Transform data."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame

        df = DataFrame(data.get("data", []))
        if df.empty:
            raise EmptyDataError(
                "There was an error with the request and was returned empty."
            )
        metadata = data.get("metadata", {})
        # Combine the legacy series with the new one.
        if "UMCSENT1" in df.columns:
            df["UMCSENT"] = df["UMCSENT"].fillna(df["UMCSENT1"])
            df = df.drop(columns=["UMCSENT1"])
            metadata.pop("UMCSENT1", None)

        # Normalize the percent values.
        df["MICH"] = df["MICH"] / 100
        if query.transform and query.transform not in ["chg", "ch1", "log"]:
            df["UMCSENT"] = df["UMCSENT"] / 100

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
