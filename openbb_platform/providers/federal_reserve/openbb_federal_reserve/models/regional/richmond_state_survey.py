"""Federal Reserve Bank of Richmond Fifth District State Survey Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

_SHEETS = {
    "carolinas": "CAR Historical Series",
    "maryland": "MD Historical Series",
    "virginia": "VA Historical Series",
}


class FederalReserveRichmondStateSurveyQueryParams(QueryParams):
    """Richmond Fed Fifth District State Survey Query Parameters."""

    __json_schema_extra__ = {
        "state": {
            "x-widget_config": {
                "options": [
                    {"label": "Carolinas", "value": "carolinas"},
                    {"label": "Maryland", "value": "maryland"},
                    {"label": "Virginia", "value": "virginia"},
                ]
            }
        }
    }

    state: Literal["carolinas", "maryland", "virginia"] = Field(
        default="virginia",
        description="The Fifth District jurisdiction survey to retrieve.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveRichmondStateSurveyData(Data):
    """Richmond Fed Fifth District State Survey Data.

    One row per (date, adjustment, horizon), with one column per survey indicator
    carrying that indicator's diffusion-index value. The indicators are pivoted to
    wide, so the indicator columns are dynamic.
    """

    date: dateType = Field(description="The survey month.")
    adjustment: str | None = Field(
        default=None, description="The seasonal adjustment (NSA or SA)."
    )
    horizon: str | None = Field(
        default=None, description="Current conditions or six-month-ahead expectations."
    )


class FederalReserveRichmondStateSurveyFetcher(
    Fetcher[
        FederalReserveRichmondStateSurveyQueryParams,
        list[FederalReserveRichmondStateSurveyData],
    ]
):
    """Richmond Fed Fifth District State Survey Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveRichmondStateSurveyQueryParams:
        """Transform the query params."""
        return FederalReserveRichmondStateSurveyQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveRichmondStateSurveyQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the requested state-survey workbook from the Richmond Fed."""
        from openbb_federal_reserve.utils.richmond_surveys import fetch_survey_workbook

        content = fetch_survey_workbook(query.state)
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveRichmondStateSurveyQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveRichmondStateSurveyData]:
        """Decode the state-survey sheet into wide indicator records."""
        from openbb_federal_reserve.utils.richmond_surveys import parse_survey_wide

        records = parse_survey_wide(
            data[0]["_raw"], _SHEETS[query.state], query.start_date, query.end_date
        )
        return [
            FederalReserveRichmondStateSurveyData.model_validate(record)
            for record in records
        ]
