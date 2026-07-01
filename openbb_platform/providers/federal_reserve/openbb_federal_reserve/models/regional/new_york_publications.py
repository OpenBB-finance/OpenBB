"""Federal Reserve Bank of New York Publications Index Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field

api_prefix = (
    SystemService()
    .system_settings.python_settings.model_dump()
    .get("api_settings", {})
    .get("prefix", "")
    or "/api/v1"
)

_SERIES = (
    "empire_state_report",
    "business_leaders_report",
    "business_leaders_supplemental_report",
    "household_debt_report",
    "market_expectations_report",
)


class FederalReserveNewYorkPublicationsQueryParams(QueryParams):
    """New York Fed Publications Index Query Parameters."""

    __json_schema_extra__ = {
        "series": {
            "x-widget_config": {
                "options": [
                    {
                        "label": "Empire State Manufacturing Survey",
                        "value": "empire_state_report",
                    },
                    {
                        "label": "Business Leaders Survey",
                        "value": "business_leaders_report",
                    },
                    {
                        "label": "Business Leaders Survey (Supplemental)",
                        "value": "business_leaders_supplemental_report",
                    },
                    {
                        "label": "Household Debt & Credit Report",
                        "value": "household_debt_report",
                    },
                    {
                        "label": "Survey of Market Expectations",
                        "value": "market_expectations_report",
                    },
                ]
            }
        }
    }

    series: (
        Literal[
            "empire_state_report",
            "business_leaders_report",
            "business_leaders_supplemental_report",
            "household_debt_report",
            "market_expectations_report",
        ]
        | None
    ) = Field(
        default=None,
        description="Filter the catalog by report series.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveNewYorkPublicationsData(Data):
    """New York Fed Publications Index Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.type": "multi_file_viewer",
                "$.name": "New York Fed Reports",
                "$.description": "New York Fed Empire State Survey, Business Leaders"
                " Survey, Household Debt and Credit, and Survey of Market Expectations"
                " report PDFs. Select one or more PDFs to view.",
                "$.category": "Federal Reserve",
                "$.subCategory": "Publications & Reports",
                "$.source": ["Federal Reserve Bank of New York"],
                "$.gridData": {"w": 30, "h": 27},
                "$.refetchInterval": False,
                "$.endpoint": f"{api_prefix}/federal_reserve/regional_publications_download",
                "$.params": [
                    {
                        "type": "endpoint",
                        "paramName": "url",
                        "optionsEndpoint": f"{api_prefix}/federal_reserve/regional_publications_choices",
                        "optionsParams": {"district": "ny"},
                        "show": False,
                        "multiSelect": True,
                        "roles": ["fileSelector"],
                    },
                ],
                "$.data": {},
            }
        }
    )

    date: dateType = Field(description="The publication date.")
    series: str = Field(description="The report series.")
    title: str = Field(description="The human-readable report title.")
    url: str = Field(description="The direct URL to the report PDF.")


class FederalReserveNewYorkPublicationsFetcher(
    Fetcher[
        FederalReserveNewYorkPublicationsQueryParams,
        list[FederalReserveNewYorkPublicationsData],
    ]
):
    """New York Fed Publications Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveNewYorkPublicationsQueryParams:
        """Transform the query params."""
        return FederalReserveNewYorkPublicationsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveNewYorkPublicationsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Aggregate every New York Fed report archive into one catalog."""
        from openbb_federal_reserve.utils.ny_publications import list_publications

        catalog = list_publications(query.series)
        if not catalog:
            raise EmptyDataError("The request was returned empty.")
        return catalog

    @staticmethod
    def transform_data(
        query: FederalReserveNewYorkPublicationsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveNewYorkPublicationsData]:
        """Apply the catalog date filters."""
        from datetime import date as date_cls

        records = data
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
            FederalReserveNewYorkPublicationsData.model_validate(record)
            for record in records
        ]
