"""Federal Reserve Bank of Atlanta Publications Index Model."""

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


class FederalReserveAtlantaPublicationsQueryParams(QueryParams):
    """Atlanta Fed Publications Index Query Parameters."""

    __json_schema_extra__ = {
        "series": {
            "x-widget_config": {
                "options": [
                    {"label": "BIE Monthly Chart Pack", "value": "bie_chart_pack"},
                    {"label": "SBU Monthly Report", "value": "sbu_monthly_report"},
                    {"label": "Working Paper", "value": "working_paper"},
                ]
            }
        }
    }

    series: Literal["bie_chart_pack", "sbu_monthly_report", "working_paper"] | None = (
        Field(
            default=None,
            description="Filter the catalog by publication series.",
        )
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveAtlantaPublicationsData(Data):
    """Atlanta Fed Publications Index Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.type": "multi_file_viewer",
                "$.name": "Atlanta Fed Publications",
                "$.description": "Atlanta Fed BIE Monthly Chart Packs, SBU Monthly"
                " Reports, and Working Papers. Select one or more PDFs to view.",
                "$.category": "Federal Reserve",
                "$.subCategory": "Publications & Reports",
                "$.source": ["Federal Reserve Bank of Atlanta"],
                "$.gridData": {"w": 30, "h": 27},
                "$.refetchInterval": False,
                "$.endpoint": f"{api_prefix}/federal_reserve/regional_publications_download",
                "$.params": [
                    {
                        "type": "endpoint",
                        "paramName": "url",
                        "optionsEndpoint": f"{api_prefix}/federal_reserve/regional_publications_choices",
                        "optionsParams": {"district": "atlanta"},
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
    url: str = Field(description="The direct URL to the publication.")
    authors: str | None = Field(
        default=None, description="The authors, for Working Papers."
    )


class FederalReserveAtlantaPublicationsFetcher(
    Fetcher[
        FederalReserveAtlantaPublicationsQueryParams,
        list[FederalReserveAtlantaPublicationsData],
    ]
):
    """Atlanta Fed Publications Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveAtlantaPublicationsQueryParams:
        """Transform the query params."""
        return FederalReserveAtlantaPublicationsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveAtlantaPublicationsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Index the Atlanta Fed publication PDF archives."""
        from openbb_federal_reserve.utils.atlanta_publications import list_publications

        catalog = list_publications(query.series)
        if not catalog:
            raise EmptyDataError("The request was returned empty.")
        return catalog

    @staticmethod
    def transform_data(
        query: FederalReserveAtlantaPublicationsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveAtlantaPublicationsData]:
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
            FederalReserveAtlantaPublicationsData.model_validate(
                {k: v for k, v in record.items() if k != "id"}
            )
            for record in records
        ]
