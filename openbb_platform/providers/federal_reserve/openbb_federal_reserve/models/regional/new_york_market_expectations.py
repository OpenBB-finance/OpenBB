"""Federal Reserve Bank of New York Survey of Market Expectations Data Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FederalReserveNewYorkMarketExpectationsQueryParams(QueryParams):
    """New York Fed Survey of Market Expectations Data Query Parameters."""

    __json_schema_extra__ = {
        "panel_type": {
            "x-widget_config": {
                "options": [
                    {"label": "Combined", "value": "Combined"},
                    {"label": "Primary Dealers", "value": "Dealer"},
                    {"label": "Market Participants", "value": "Participant"},
                ]
            }
        }
    }

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )
    panel_type: Literal["Combined", "Dealer", "Participant"] | None = Field(
        default=None,
        description="Filter to a single respondent panel.",
    )


class FederalReserveNewYorkMarketExpectationsData(Data):
    """New York Fed Survey of Market Expectations Data."""

    date: dateType = Field(description="The survey release date.")
    survey_due_date: dateType | None = Field(
        default=None, description="The date responses were due."
    )
    panel_type: str | None = Field(
        default=None,
        description="The respondent panel: 'Combined', 'Dealer', or 'Participant'.",
    )
    question_number: str | None = Field(
        default=None, description="The survey question number."
    )
    theme: str | None = Field(default=None, description="The question theme.")
    subject_group: str | None = Field(
        default=None, description="The question subject group."
    )
    subject: str | None = Field(default=None, description="The question subject.")
    question_type: str | None = Field(
        default=None, description="The question type, e.g. 'probability' or 'point'."
    )
    question_mode: str | None = Field(
        default=None, description="The question mode, e.g. 'levels' or 'change'."
    )
    question_text: str | None = Field(
        default=None, description="The full question text."
    )
    question_tag: str | None = Field(
        default=None, description="The machine-readable question identifier."
    )
    value_tag: str | None = Field(
        default=None, description="The machine-readable value identifier."
    )
    top_header_value: str | None = Field(
        default=None, description="The top header label for a matrix question cell."
    )
    left_header_value: str | None = Field(
        default=None, description="The left header label for a matrix question cell."
    )
    horizon: str | None = Field(
        default=None, description="The forecast horizon, e.g. '6months'."
    )
    horizon_date: dateType | None = Field(
        default=None, description="The date the horizon resolves to."
    )
    bucket_range: str | None = Field(
        default=None, description="The response bucket range label."
    )
    bucket_low: float | None = Field(
        default=None, description="The lower bound of the response bucket."
    )
    bucket_high: float | None = Field(
        default=None, description="The upper bound of the response bucket."
    )
    aggregation: str | None = Field(
        default=None,
        description="The aggregation statistic, e.g. 'avg', 'count', or 'pctl50'.",
    )
    aggregation_value: float | None = Field(
        default=None, description="The aggregated response value."
    )


class FederalReserveNewYorkMarketExpectationsFetcher(
    Fetcher[
        FederalReserveNewYorkMarketExpectationsQueryParams,
        list[FederalReserveNewYorkMarketExpectationsData],
    ]
):
    """New York Fed Survey of Market Expectations Data Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveNewYorkMarketExpectationsQueryParams:
        """Transform the query params."""
        return FederalReserveNewYorkMarketExpectationsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveNewYorkMarketExpectationsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download and combine the Survey of Market Expectations results."""
        from openbb_federal_reserve.utils.ny_surveys import fetch_sme_data

        data = fetch_sme_data()
        if not data:
            raise EmptyDataError("The request was returned empty.")
        return data

    @staticmethod
    def transform_data(
        query: FederalReserveNewYorkMarketExpectationsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveNewYorkMarketExpectationsData]:
        """Apply the panel and date filters."""
        records = data
        if query.panel_type:
            records = [r for r in records if r.get("panel_type") == query.panel_type]
        if query.start_date:
            records = [
                r for r in records if r["date"] and r["date"] >= query.start_date
            ]
        if query.end_date:
            records = [r for r in records if r["date"] and r["date"] <= query.end_date]
        if not records:
            raise EmptyDataError("The request was returned empty.")
        return [
            FederalReserveNewYorkMarketExpectationsData.model_validate(record)
            for record in records
        ]
