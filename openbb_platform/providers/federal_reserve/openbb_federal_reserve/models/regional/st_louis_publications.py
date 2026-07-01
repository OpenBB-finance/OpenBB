"""Federal Reserve Bank of St. Louis Publications Index Model."""

from datetime import date as dateType
from typing import Any

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


class FederalReserveStLouisPublicationsQueryParams(QueryParams):
    """St. Louis Fed Publications Index Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveStLouisPublicationsData(Data):
    """St. Louis Fed Publications Index Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.type": "multi_file_viewer",
                "$.name": "St. Louis Fed Publications",
                "$.description": "St. Louis Fed Economic Synopses articles. Select"
                " one or more PDFs to view.",
                "$.category": "Federal Reserve",
                "$.subCategory": "Publications & Reports",
                "$.source": ["Federal Reserve Bank of St. Louis"],
                "$.gridData": {"w": 30, "h": 27},
                "$.refetchInterval": False,
                "$.endpoint": f"{api_prefix}/federal_reserve/regional_publications_download",
                "$.params": [
                    {
                        "type": "endpoint",
                        "paramName": "url",
                        "optionsEndpoint": f"{api_prefix}/federal_reserve/regional_publications_choices",
                        "optionsParams": {"district": "stl"},
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
    url: str = Field(description="The direct URL to the publication PDF.")


class FederalReserveStLouisPublicationsFetcher(
    Fetcher[
        FederalReserveStLouisPublicationsQueryParams,
        list[FederalReserveStLouisPublicationsData],
    ]
):
    """St. Louis Fed Publications Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveStLouisPublicationsQueryParams:
        """Transform the query params."""
        return FederalReserveStLouisPublicationsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveStLouisPublicationsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Index the St. Louis Fed publication PDF archive on FRASER."""
        from openbb_federal_reserve.utils.st_louis import list_publications

        catalog = list_publications()
        if not catalog:
            raise EmptyDataError("The request was returned empty.")
        return catalog

    @staticmethod
    def transform_data(
        query: FederalReserveStLouisPublicationsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveStLouisPublicationsData]:
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
            FederalReserveStLouisPublicationsData.model_validate(
                {k: v for k, v in record.items() if k != "id"}
            )
            for record in records
        ]
