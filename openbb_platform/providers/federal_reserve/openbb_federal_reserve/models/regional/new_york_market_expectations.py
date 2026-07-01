"""Federal Reserve Bank of New York Survey of Market Expectations Index Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FederalReserveNewYorkMarketExpectationsQueryParams(QueryParams):
    """New York Fed Survey of Market Expectations Index Query Parameters."""

    __json_schema_extra__ = {
        "kind": {
            "x-widget_config": {
                "options": [
                    {"label": "Results", "value": "results"},
                    {"label": "Questionnaire", "value": "questionnaire"},
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
    kind: Literal["results", "questionnaire"] | None = Field(
        default=None,
        description="Filter the catalog by document kind.",
    )


class FederalReserveNewYorkMarketExpectationsData(Data):
    """New York Fed Survey of Market Expectations Index Data."""

    date: dateType = Field(description="The survey month.")
    kind: str = Field(description="The document kind, 'results' or 'questionnaire'.")
    subtype: str = Field(
        description="The respondent panel: 'combined', 'primary_dealers',"
        + " or 'market_participants'."
    )
    title: str = Field(description="The human-readable document title.")
    url: str = Field(description="The direct URL to the PDF document.")


class FederalReserveNewYorkMarketExpectationsFetcher(
    Fetcher[
        FederalReserveNewYorkMarketExpectationsQueryParams,
        list[FederalReserveNewYorkMarketExpectationsData],
    ]
):
    """New York Fed Survey of Market Expectations Index Fetcher."""

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
        """Index the Survey of Market Expectations PDF archive."""
        from openbb_federal_reserve.utils.ny_surveys import list_market_expectations

        catalog = list_market_expectations()
        if not catalog:
            raise EmptyDataError("The request was returned empty.")
        return catalog

    @staticmethod
    def transform_data(
        query: FederalReserveNewYorkMarketExpectationsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveNewYorkMarketExpectationsData]:
        """Apply the catalog filters."""
        from datetime import date as date_cls

        records = data
        if query.kind:
            records = [record for record in records if record["kind"] == query.kind]
        if query.start_date:
            records = [
                record
                for record in records
                if date_cls.fromisoformat(record["date"]) >= query.start_date
            ]
        if query.end_date:
            records = [
                record
                for record in records
                if date_cls.fromisoformat(record["date"]) <= query.end_date
            ]
        return [
            FederalReserveNewYorkMarketExpectationsData.model_validate(record)
            for record in records
        ]
