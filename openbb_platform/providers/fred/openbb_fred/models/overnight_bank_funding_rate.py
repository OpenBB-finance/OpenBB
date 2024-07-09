"""FRED Overnight Bank Funding Rate Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional, Union

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.overnight_bank_funding_rate import (
    OvernightBankFundingRateData,
    OvernightBankFundingRateQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_fred.models.series import FredSeriesFetcher
from pydantic import Field, field_validator

OBFR_ID_TO_FIELD = {
    "OBFR": "rate",
    "OBFR1": "percentile_1",
    "OBFR25": "percentile_25",
    "OBFR75": "percentile_75",
    "OBFR99": "percentile_99",
    "OBFRVOL": "volume",
}
ALL_IDS = list(OBFR_ID_TO_FIELD)


class FredOvernightBankFundingRateQueryParams(OvernightBankFundingRateQueryParams):
    """FRED Overnight Bank Funding Rate Query Params."""

    frequency: Union[
        None,
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
        ],
    ] = Field(
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
    aggregation_method: Union[None, Literal["avg", "sum", "eop"]] = Field(
        default=None,
        description="""
        A key that indicates the aggregation method used for frequency aggregation.
            avg = Average
            sum = Sum
            eop = End of Period
        """,
        json_schema_extra={"choices": ["avg", "sum", "eop"]},
    )
    transform: Union[
        None, Literal["chg", "ch1", "pch", "pc1", "pca", "cch", "cca", "log"]
    ] = Field(
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


class FredOvernightBankFundingRateData(OvernightBankFundingRateData):
    """Fred Overnight Bank Funding Rate Data."""

    __alias_dict__ = {
        "rate": "OBFR",
        "percentile_1": "OBFR1",
        "percentile_25": "OBFR25",
        "percentile_75": "OBFR75",
        "percentile_99": "OBFR99",
        "volume": "OBFRVOL",
    }

    @field_validator(
        "rate",
        "percentile_1",
        "percentile_25",
        "percentile_75",
        "percentile_99",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def normalize_percent(cls, v):
        """Normalize percent."""
        return float(v) / 100 if v else None


class FredOvernightBankFundingRateFetcher(
    Fetcher[
        FredOvernightBankFundingRateQueryParams, List[FredOvernightBankFundingRateData]
    ]
):
    """Fred Overnight Bank Funding Rate Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> FredOvernightBankFundingRateQueryParams:
        """Transform query."""
        return FredOvernightBankFundingRateQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FredOvernightBankFundingRateQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> Dict:
        """Extract data."""
        try:
            response = await FredSeriesFetcher.fetch_data(
                dict(
                    symbol=",".join(ALL_IDS),
                    start_date=query.start_date,
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
        query: FredOvernightBankFundingRateQueryParams, data: Dict, **kwargs: Any
    ) -> AnnotatedResult[List[FredOvernightBankFundingRateData]]:
        """Transform data"""
        if not data:
            raise EmptyDataError("The request was returned empty.")
        return AnnotatedResult(
            result=[
                FredOvernightBankFundingRateData.model_validate(d)
                for d in data.get("data", [])
                if d.get("OBFR")
            ],
            metadata=data.get("metadata", {}),
        )
