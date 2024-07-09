"""FRED Euro Short Term Rate Standard Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.euro_short_term_rate import (
    EuroShortTermRateData,
    EuroShortTermRateQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_fred.models.series import FredSeriesFetcher
from pydantic import Field, field_validator


class FredEuroShortTermRateQueryParams(EuroShortTermRateQueryParams):
    """FRED Euro Short Term Rate Query."""

    frequency: Optional[
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
    ] = Field(
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
        return float(v) / 100 if v else None


class FredEuroShortTermRateFetcher(
    Fetcher[FredEuroShortTermRateQueryParams, List[FredEuroShortTermRateData]]
):
    """FRED Euro Short Term Rate Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FredEuroShortTermRateQueryParams:
        """Transform query"""
        return FredEuroShortTermRateQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FredEuroShortTermRateQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
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
        query: FredEuroShortTermRateQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> AnnotatedResult[List[FredEuroShortTermRateData]]:
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
