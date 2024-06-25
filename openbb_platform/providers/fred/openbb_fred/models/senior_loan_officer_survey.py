"""FRED Senior Loan Officer Opinion Survey Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional, Union

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.senior_loan_officer_survey import (
    SeniorLoanOfficerSurveyData,
    SeniorLoanOfficerSurveyQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_fred.models.series import FredSeriesFetcher
from pydantic import Field

SLOOS_CATEGORIES = {
    "spreads": "DRISCFLM,DRISCFS,SUBLPDCLCTSNQ",
    "consumer": "DRIWCIL,STDSOTHCONS,SUBLPDCLHSNQ",
    "auto": "DEMAUTO,STDSAUTO",
    "credit_card": "DEMCC,DRTSCLCC,SUBLPDCLCTSNQ",
    "firms": "DRISCFLM,DRISCFS,DRTSCILM,DRTSCIS",
    "mortgage": "DRTSSP,SUBLPDHMSGNQ,SUBLPDHMSENQ,SUBLPDHMSJNQ,SUBLPDHMSQNQ,SUBLPDHMSMNQ",
    "commercial_real_estate": "SUBLPDRCSN,SUBLPDRCSM,SUBLPDRCDCLGNQ,SUBLPFRCSNQ",
    "standards": "DRTSCILM,DRTSCIS,DRTSCLCC,STDSAUTO,DRTSSP,SUBLPDHMSGNQ,STDSOTHCONS,SUBLPDHMSENQ,SUBLPDHMSJNQ,SUBLPDHMSQNQ,SUBLPDHMSMNQ,SUBLPDCLHSNQ,SUBLPDRCSN,SUBLPDRCSM,SUBLPFRCSNQ,SUBLPFCISNQ,SUBLPDMBSXWBNQ",  # noqa: E501  # pylint: disable=line-too-long
    "demand": "DEMCC,DEMAUTO,SUBLPDMODXWBNQ,SUBLPDMBDXWBNQ,SUBLPDRCDCLGNQ",
    "foreign_banks": "SUBLPFRCSNQ,SUBLPFCISNQ",
}


class FredSeniorLoanOfficerSurveyQueryParams(SeniorLoanOfficerSurveyQueryParams):
    """FRED Senior Loan Officer Opinion Survey Query Params."""

    category: Literal[
        "spreads",
        "consumer",
        "auto",
        "credit_card",
        "firms",
        "mortgage",
        "commercial_real_estate",
        "standards",
        "demand",
        "foreign_banks",
    ] = Field(
        default="spreads",
        description="Category of survey response.",
        json_schema_extra={"choices": list(SLOOS_CATEGORIES.keys())},
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


class FredSeniorLoanOfficerSurveyData(SeniorLoanOfficerSurveyData):
    """FRED Senior Loan Officer Opinion Survey Data."""


class FredSeniorLoanOfficerSurveyFetcher(
    Fetcher[
        FredSeniorLoanOfficerSurveyQueryParams, List[FredSeniorLoanOfficerSurveyData]
    ]
):
    """FRED Senior Loan Officer Opinion Survey Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> FredSeniorLoanOfficerSurveyQueryParams:
        """Transform query."""
        return FredSeniorLoanOfficerSurveyQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FredSeniorLoanOfficerSurveyQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Extract data."""
        ids = SLOOS_CATEGORIES[query.category]
        try:
            response = await FredSeriesFetcher.fetch_data(
                dict(
                    symbol=ids,
                    start_date=query.start_date,
                    end_date=query.end_date,
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
        query: FredSeniorLoanOfficerSurveyQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> AnnotatedResult[List[FredSeniorLoanOfficerSurveyData]]:
        """Transform data."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame

        metadata = data.get("metadata", {})
        df = DataFrame(data.get("data", [])).dropna()
        if df.empty:
            raise EmptyDataError(
                "There was an error with the request and it was returned empty."
            )
        # Flatten data
        df = df.melt(id_vars="date", var_name="symbol", value_name="value").query(
            "value.notnull()"
        )
        df["title"] = df.symbol.apply(lambda x: metadata[x].get("title", ""))
        df["value"] = df["value"].astype(float) / 100
        df = df.fillna("N/A").replace("N/A", None)
        records = df.sort_values(by="date").to_dict(orient="records")

        return AnnotatedResult(
            result=[FredSeniorLoanOfficerSurveyData.model_validate(d) for d in records],
            metadata=metadata,
        )
