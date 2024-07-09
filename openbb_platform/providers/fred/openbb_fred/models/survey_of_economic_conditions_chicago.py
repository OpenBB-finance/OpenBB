"""FRED Survey Of Economic Conditions - Chicago - Model"""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional, Union

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.survey_of_economic_conditions_chicago import (
    SurveyOfEconomicConditionsChicagoData,
    SurveyOfEconomicConditionsChicagoQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_fred.models.series import FredSeriesFetcher
from pydantic import Field

ID_TO_FIELD = {
    "CFSBCACTIVITY": "activity_index",
    "CFSBCOUTLOOK": "one_year_outlook",
    "CFSBCACTIVITYMFG": "manufacturing_activity",
    "CFSBCACTIVITYNMFG": "non_manufacturing_activity",
    "CFSBCCAPXEXP": "capital_spending_expectations",
    "CFSBCHIRINGEXP": "hiring_expectations",
    "CFSBCHIRING": "current_hiring_index",
    "CFSBCLABORCOSTS": "labor_costs_index",
    "CFSBCNONLABORCOSTS": "non_labor_costs_index",
}


class FredSurveyOfEconomicConditionsChicagoQueryParams(
    SurveyOfEconomicConditionsChicagoQueryParams
):
    """FRED Survey Of Economic Conditions - Chicago - Query Params."""

    frequency: Union[
        None,
        Literal[
            "annual",
            "quarter",
        ],
    ] = Field(
        default=None,
        description="Frequency aggregation to convert monthly data to lower frequency. None is monthly.",
        json_schema_extra={
            "choices": [
                "annual",
                "quarter",
            ]
        },
    )
    aggregation_method: Union[None, Literal["avg", "sum", "eop"]] = Field(
        default=None,
        description="""A key that indicates the aggregation method used for frequency aggregation.
        \n    avg = Average
        \n    sum = Sum
        \n    eop = End of Period
        """,
        json_schema_extra={"choices": ["avg", "sum", "eop"]},
    )
    transform: Union[
        None, Literal["chg", "ch1", "pch", "pc1", "pca", "cch", "cca", "log"]
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


class FredSurveyOfEconomicConditionsChicagoData(SurveyOfEconomicConditionsChicagoData):
    """FRED Survey Of Economic Conditions - Chicago - Data."""


class FredSurveyOfEconomicConditionsChicagoFetcher(
    Fetcher[
        FredSurveyOfEconomicConditionsChicagoQueryParams,
        List[FredSurveyOfEconomicConditionsChicagoData],
    ]
):
    """FRED Survey Of Economic Conditions - Chicago - Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> FredSurveyOfEconomicConditionsChicagoQueryParams:
        """Transform query."""
        return FredSurveyOfEconomicConditionsChicagoQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FredSurveyOfEconomicConditionsChicagoQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> Dict:
        """Extract data."""
        ids = list(ID_TO_FIELD.keys())
        frequency = query.frequency[:1].lower() if query.frequency else None
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
        query: FredSurveyOfEconomicConditionsChicagoQueryParams,
        data: Dict,
        **kwargs: Any
    ) -> AnnotatedResult[List[FredSurveyOfEconomicConditionsChicagoData]]:
        """Transform data."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame

        df = DataFrame(data["data"])
        metadata = data.get("metadata", {})
        if df.empty:
            raise EmptyDataError(
                "There was an error with the request and was returned empty."
            )
        df = df.set_index("date").sort_index()
        df.columns = [ID_TO_FIELD.get(c, c) for c in df.columns]
        if query.transform in ["pch", "pc1", "pca", "cch", "cca"]:
            df = df / 100
        df = df.reset_index().fillna("N/A").replace("N/A", None)
        records = df.to_dict(orient="records")
        return AnnotatedResult(
            result=[
                FredSurveyOfEconomicConditionsChicagoData.model_validate(d)
                for d in records
            ],
            metadata=metadata,
        )
