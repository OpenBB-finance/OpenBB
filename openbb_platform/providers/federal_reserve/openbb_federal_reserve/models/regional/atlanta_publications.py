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

from openbb_federal_reserve.utils.fedinprint import series_choices

api_prefix = SystemService().system_settings.api_settings.prefix or "/api/v1"


class FederalReserveAtlantaPublicationsQueryParams(QueryParams):
    """Atlanta Fed Publications Index Query Parameters."""

    __json_schema_extra__ = {
        "series": {"x-widget_config": {"options": series_choices("atlanta")}}
    }

    series: (
        Literal[
            "frb_atlanta_working_paper",
            "economic_review",
            "policy_hub",
            "frb_atlanta_community_and_economic_development_discussion_paper",
            "consumer_payments_research_data_reports",
            "workforce_currents",
            "frb_atlanta_cqer_working_paper",
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
    limit: int = Field(
        default=20, description="The maximum number of documents to return."
    )
    offset: int = Field(
        default=0, description="The result offset to begin from, for pagination."
    )


class FederalReserveAtlantaPublicationsData(Data):
    """Atlanta Fed Publications Index Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.type": "multi_file_viewer",
                "$.name": "Atlanta Fed Publications",
                "$.description": "Atlanta Fed publications indexed on Fed in Print."
                " Select one or more documents to view.",
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
                        "optionsParams": {
                            "district": "atlanta",
                            "series": "$series",
                            "start_date": "$start_date",
                            "end_date": "$end_date",
                            "limit": "$limit",
                            "offset": "$offset",
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

    date: dateType | None = Field(default=None, description="The publication date.")
    series: str = Field(description="The publication series.")
    title: str = Field(description="The human-readable publication title.")
    url: str = Field(description="The direct URL to the publication document.")


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
        """Index Atlanta Fed publications via the Fed in Print search."""
        from openbb_federal_reserve.utils import fedinprint

        catalog = fedinprint.list_publications(
            "atlanta",
            series=query.series,
            start_date=query.start_date,
            start=query.offset,
            limit=query.limit,
        )
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
                if record["date"]
                and date_cls.fromisoformat(record["date"]) >= query.start_date
            ]
        if query.end_date:
            records = [
                record
                for record in records
                if record["date"]
                and date_cls.fromisoformat(record["date"]) <= query.end_date
            ]
        return [
            FederalReserveAtlantaPublicationsData.model_validate(
                {
                    "date": record["date"] or None,
                    "series": record["series"],
                    "title": record["title"],
                    "url": record["url"],
                }
            )
            for record in records
        ]
