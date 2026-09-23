"""Federal Reserve Bank of New York Survey of Market Expectations Reports Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field

api_prefix = SystemService().system_settings.api_settings.prefix or "/api/v1"


class FederalReserveNewYorkMarketExpectationsReportsQueryParams(QueryParams):
    """New York Fed Survey of Market Expectations Reports Query Parameters."""

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


class FederalReserveNewYorkMarketExpectationsReportsData(Data):
    """New York Fed Survey of Market Expectations Reports Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.type": "multi_file_viewer",
                "$.name": "NY Fed Survey of Market Expectations Reports",
                "$.description": "Pre-FOMC Surveys of Primary Dealers and Market"
                " Participants report PDFs. Select one or more documents to view.",
                "$.category": "Federal Reserve",
                "$.subCategory": "Rates & Markets",
                "$.source": ["Federal Reserve Bank of New York"],
                "$.gridData": {"w": 30, "h": 27},
                "$.refetchInterval": False,
                "$.endpoint": f"{api_prefix}/federal_reserve"
                "/regional_publications_download",
                "$.params": [
                    {
                        "type": "endpoint",
                        "paramName": "url",
                        "optionsEndpoint": f"{api_prefix}/federal_reserve"
                        "/regional_reports_choices",
                        "optionsParams": {
                            "report": "market_expectations",
                            "start_date": "$start_date",
                            "end_date": "$end_date",
                            "kind": "$kind",
                        },
                        "show": False,
                        "multiSelect": True,
                        "roles": ["fileSelector"],
                    },
                ],
                "$.data": {},
            }
        }
    )

    date: dateType = Field(description="The survey month.")
    kind: str = Field(description="The document kind, 'results' or 'questionnaire'.")
    subtype: str = Field(
        description="The respondent panel: 'combined', 'primary_dealers',"
        + " or 'market_participants'."
    )
    title: str = Field(description="The human-readable document title.")
    url: str = Field(description="The direct URL to the PDF document.")


class FederalReserveNewYorkMarketExpectationsReportsFetcher(
    Fetcher[
        FederalReserveNewYorkMarketExpectationsReportsQueryParams,
        list[FederalReserveNewYorkMarketExpectationsReportsData],
    ]
):
    """New York Fed Survey of Market Expectations Reports Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveNewYorkMarketExpectationsReportsQueryParams:
        """Transform the query params."""
        return FederalReserveNewYorkMarketExpectationsReportsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveNewYorkMarketExpectationsReportsQueryParams,
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
        query: FederalReserveNewYorkMarketExpectationsReportsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveNewYorkMarketExpectationsReportsData]:
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
            FederalReserveNewYorkMarketExpectationsReportsData.model_validate(record)
            for record in records
        ]
