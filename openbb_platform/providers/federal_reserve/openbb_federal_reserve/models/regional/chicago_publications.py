"""Federal Reserve Bank of Chicago Publications Index Model."""

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


class FederalReserveChicagoPublicationsQueryParams(QueryParams):
    """Chicago Fed Publications Index Query Parameters."""

    __json_schema_extra__ = {
        "series": {
            "x-widget_config": {
                "options": [
                    {"label": "AgLetter", "value": "agletter"},
                    {"label": "Chicago Fed Letter", "value": "chicago_fed_letter"},
                    {
                        "label": "Economic Perspectives",
                        "value": "economic_perspectives",
                    },
                    {"label": "Working Papers", "value": "working_papers"},
                ]
            }
        }
    }

    series: (
        Literal[
            "agletter",
            "chicago_fed_letter",
            "economic_perspectives",
            "working_papers",
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


class FederalReserveChicagoPublicationsData(Data):
    """Chicago Fed Publications Index Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.type": "multi_file_viewer",
                "$.name": "Chicago Fed Publications",
                "$.description": "Chicago Fed AgLetter, Chicago Fed Letter, Economic"
                " Perspectives, and Working Papers. Select one or more PDFs to view.",
                "$.category": "Federal Reserve",
                "$.subCategory": "Publications & Reports",
                "$.source": ["Federal Reserve Bank of Chicago"],
                "$.gridData": {"w": 30, "h": 27},
                "$.refetchInterval": False,
                "$.endpoint": f"{api_prefix}/federal_reserve/regional_publications_download",
                "$.params": [
                    {
                        "type": "endpoint",
                        "paramName": "url",
                        "optionsEndpoint": f"{api_prefix}/federal_reserve/regional_publications_choices",
                        "optionsParams": {"district": "chicago"},
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
    series: str = Field(description="The publication series key.")
    title: str = Field(description="The human-readable publication title.")
    volume: str | None = Field(default=None, description="The publication volume.")
    issue: str | None = Field(default=None, description="The publication issue.")
    landing_url: str = Field(description="The publication landing-page URL.")
    url: str = Field(description="The direct URL to the PDF document.")


class FederalReserveChicagoPublicationsFetcher(
    Fetcher[
        FederalReserveChicagoPublicationsQueryParams,
        list[FederalReserveChicagoPublicationsData],
    ]
):
    """Chicago Fed Publications Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveChicagoPublicationsQueryParams:
        """Transform the query params."""
        return FederalReserveChicagoPublicationsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveChicagoPublicationsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Index the Chicago Fed publication PDF archives."""
        from openbb_federal_reserve.utils.chicago_publications import list_publications

        catalog = list_publications(query.series)
        if not catalog:
            raise EmptyDataError("The request was returned empty.")
        return catalog

    @staticmethod
    def transform_data(
        query: FederalReserveChicagoPublicationsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveChicagoPublicationsData]:
        """Apply the catalog filters."""
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
            FederalReserveChicagoPublicationsData.model_validate(record)
            for record in records
        ]
