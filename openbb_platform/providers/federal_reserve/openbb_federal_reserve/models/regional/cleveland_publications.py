"""Federal Reserve Bank of Cleveland Publications Index Model."""

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


class FederalReserveClevelandPublicationsQueryParams(QueryParams):
    """Cleveland Fed Publications Index Query Parameters."""

    __json_schema_extra__ = {
        "series": {
            "x-widget_config": {
                "options": [
                    {"label": "Economic Commentary", "value": "economic_commentary"},
                    {"label": "Working Paper", "value": "working_paper"},
                    {
                        "label": "Policy Discussion Paper",
                        "value": "policy_discussion_papers",
                    },
                    {
                        "label": "Cleveland Fed District Data Brief",
                        "value": "district_data_brief",
                    },
                    {"label": "Annual Report", "value": "annual_report"},
                    {
                        "label": "Regional Policy Report",
                        "value": "regional_policy_report",
                    },
                    {"label": "Economic Review", "value": "economic_review"},
                ]
            }
        }
    }

    series: (
        Literal[
            "economic_commentary",
            "working_paper",
            "policy_discussion_papers",
            "district_data_brief",
            "annual_report",
            "regional_policy_report",
            "economic_review",
        ]
        | None
    ) = Field(
        default=None,
        description="Filter the catalog by publication series.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveClevelandPublicationsData(Data):
    """Cleveland Fed Publications Index Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.type": "multi_file_viewer",
                "$.name": "Cleveland Fed Publications",
                "$.description": "Cleveland Fed Economic Commentary, Working Papers,"
                " Policy Discussion Papers, District Data Briefs, Annual Reports,"
                " Regional Policy Reports, and Economic Review. Select one or more"
                " PDFs to view.",
                "$.category": "Federal Reserve",
                "$.subCategory": "Publications & Reports",
                "$.source": ["Federal Reserve Bank of Cleveland"],
                "$.gridData": {"w": 30, "h": 27},
                "$.refetchInterval": False,
                "$.endpoint": f"{api_prefix}/federal_reserve/regional_publications_download",
                "$.params": [
                    {
                        "type": "endpoint",
                        "paramName": "url",
                        "optionsEndpoint": f"{api_prefix}/federal_reserve/regional_publications_choices",
                        "optionsParams": {"district": "cleveland"},
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
    series: str = Field(description="The publication series.")
    title: str = Field(description="The human-readable publication title.")
    url: str = Field(description="The direct URL to the PDF document.")
    authors: str | None = Field(
        default=None, description="The authors of the publication."
    )


class FederalReserveClevelandPublicationsFetcher(
    Fetcher[
        FederalReserveClevelandPublicationsQueryParams,
        list[FederalReserveClevelandPublicationsData],
    ]
):
    """Cleveland Fed Publications Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveClevelandPublicationsQueryParams:
        """Transform the query params."""
        return FederalReserveClevelandPublicationsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveClevelandPublicationsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Index the Cleveland Fed publication PDF archives."""
        from openbb_federal_reserve.utils.cleveland_publications import (
            list_publications,
        )

        catalog = list_publications(query.series)
        if not catalog:
            raise EmptyDataError("The request was returned empty.")
        return catalog

    @staticmethod
    def transform_data(
        query: FederalReserveClevelandPublicationsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveClevelandPublicationsData]:
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
            FederalReserveClevelandPublicationsData.model_validate(
                {k: v for k, v in record.items() if k != "id"}
            )
            for record in records
        ]
