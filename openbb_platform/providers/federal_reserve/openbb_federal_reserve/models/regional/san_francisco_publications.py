"""Federal Reserve Bank of San Francisco Publications Index Model."""

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


class FederalReserveSanFranciscoPublicationsQueryParams(QueryParams):
    """San Francisco Fed Publications Index Query Parameters."""

    __json_schema_extra__ = {
        "publication_type": {
            "x-widget_config": {
                "options": [
                    {"label": "Economic Letter", "value": "economic_letter"},
                    {"label": "FedViews", "value": "fedviews"},
                ]
            }
        }
    }

    publication_type: Literal["economic_letter", "fedviews"] | None = Field(
        default=None,
        description="The publication series to index; all series when unset.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveSanFranciscoPublicationsData(Data):
    """San Francisco Fed Publications Index Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.type": "multi_file_viewer",
                "$.name": "SF Fed Publications",
                "$.description": "FRBSF Economic Letter and SF FedViews releases."
                " Select one or more PDFs to view.",
                "$.category": "Federal Reserve",
                "$.subCategory": "Publications & Reports",
                "$.source": ["Federal Reserve Bank of San Francisco"],
                "$.gridData": {"w": 30, "h": 27},
                "$.refetchInterval": False,
                "$.endpoint": f"{api_prefix}/federal_reserve/regional_publications_download",
                "$.params": [
                    {
                        "type": "endpoint",
                        "paramName": "url",
                        "optionsEndpoint": f"{api_prefix}/federal_reserve/regional_publications_choices",
                        "optionsParams": {"district": "sf"},
                        "show": False,
                        "multiSelect": True,
                        "roles": ["fileSelector"],
                    },
                ],
                "$.data": {},
            }
        }
    )

    date: dateType = Field(description="The publication release date.")
    publication_type: str = Field(description="The publication series.")
    title: str = Field(description="The publication title.")
    slug: str = Field(description="The publication slug identifier.")
    volume: str | None = Field(default=None, description="The publication volume.")
    issue: str | None = Field(default=None, description="The publication issue number.")
    link: str = Field(description="The publication landing-page URL.")
    url: str | None = Field(default=None, description="The direct PDF URL.")


class FederalReserveSanFranciscoPublicationsFetcher(
    Fetcher[
        FederalReserveSanFranciscoPublicationsQueryParams,
        list[FederalReserveSanFranciscoPublicationsData],
    ]
):
    """San Francisco Fed Publications Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveSanFranciscoPublicationsQueryParams:
        """Transform the query params."""
        return FederalReserveSanFranciscoPublicationsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveSanFranciscoPublicationsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Enumerate the San Francisco Fed publications catalog."""
        from openbb_federal_reserve.utils.san_francisco_publications import (
            list_publications,
        )

        catalog = list_publications(query.publication_type)
        if not catalog:
            raise EmptyDataError("The request was returned empty.")
        return catalog

    @staticmethod
    def transform_data(
        query: FederalReserveSanFranciscoPublicationsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveSanFranciscoPublicationsData]:
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
            FederalReserveSanFranciscoPublicationsData.model_validate(record)
            for record in records
        ]
