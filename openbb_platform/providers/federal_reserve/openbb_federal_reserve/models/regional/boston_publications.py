"""Federal Reserve Bank of Boston Publications Index Model."""

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


class FederalReserveBostonPublicationsQueryParams(QueryParams):
    """Boston Fed Publications Index Query Parameters."""

    __json_schema_extra__ = {
        "series": {
            "x-widget_config": {
                "options": [
                    {"label": "New England Economic Conditions", "value": "neec"}
                ]
            }
        }
    }

    series: Literal["neec"] = Field(
        default="neec",
        description="The publication series to index.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveBostonPublicationsData(Data):
    """Boston Fed Publications Index Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.type": "multi_file_viewer",
                "$.name": "Boston Fed Publications",
                "$.description": "Boston Fed New England Economic Conditions (NEEC)"
                " issue reports. Select one or more PDFs to view.",
                "$.category": "Federal Reserve",
                "$.subCategory": "Publications & Reports",
                "$.source": ["Federal Reserve Bank of Boston"],
                "$.gridData": {"w": 30, "h": 27},
                "$.refetchInterval": False,
                "$.endpoint": f"{api_prefix}/federal_reserve/regional_publications_download",
                "$.params": [
                    {
                        "type": "endpoint",
                        "paramName": "url",
                        "optionsEndpoint": f"{api_prefix}/federal_reserve/regional_publications_choices",
                        "optionsParams": {"district": "boston"},
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


class FederalReserveBostonPublicationsFetcher(
    Fetcher[
        FederalReserveBostonPublicationsQueryParams,
        list[FederalReserveBostonPublicationsData],
    ]
):
    """Boston Fed Publications Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveBostonPublicationsQueryParams:
        """Transform the query params."""
        return FederalReserveBostonPublicationsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveBostonPublicationsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Index the Boston Fed publication PDF archive."""
        from openbb_federal_reserve.utils.boston_publications import list_publications

        catalog = list_publications(query.series)
        if not catalog:
            raise EmptyDataError("The request was returned empty.")
        return catalog

    @staticmethod
    def transform_data(
        query: FederalReserveBostonPublicationsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveBostonPublicationsData]:
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
            FederalReserveBostonPublicationsData.model_validate(
                {k: v for k, v in record.items() if k != "id"}
            )
            for record in records
        ]
