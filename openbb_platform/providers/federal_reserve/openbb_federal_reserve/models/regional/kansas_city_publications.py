"""Federal Reserve Bank of Kansas City Publications Index Model."""

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


class FederalReserveKansasCityPublicationsQueryParams(QueryParams):
    """Kansas City Fed Publications Index Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveKansasCityPublicationsData(Data):
    """Kansas City Fed Publications Index Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.type": "multi_file_viewer",
                "$.name": "KC Fed Agricultural Bulletins",
                "$.description": "Kansas City Fed quarterly Tenth District Agricultural"
                " Bulletins. Select one or more PDFs to view.",
                "$.category": "Federal Reserve",
                "$.subCategory": "Publications & Reports",
                "$.source": ["Federal Reserve Bank of Kansas City"],
                "$.gridData": {"w": 30, "h": 27},
                "$.refetchInterval": False,
                "$.endpoint": f"{api_prefix}/federal_reserve/regional_publications_download",
                "$.params": [
                    {
                        "type": "endpoint",
                        "paramName": "url",
                        "optionsEndpoint": f"{api_prefix}/federal_reserve/regional_publications_choices",
                        "optionsParams": {"district": "kc"},
                        "show": False,
                        "multiSelect": True,
                        "roles": ["fileSelector"],
                    },
                ],
                "$.data": {},
            }
        }
    )

    date: dateType = Field(description="The bulletin quarter, dated to its first day.")
    year: int = Field(description="The bulletin calendar year.")
    quarter: int = Field(description="The bulletin quarter, 1 through 4.")
    title: str = Field(description="The human-readable bulletin title.")
    url: str = Field(description="The direct URL to the PDF document.")


class FederalReserveKansasCityPublicationsFetcher(
    Fetcher[
        FederalReserveKansasCityPublicationsQueryParams,
        list[FederalReserveKansasCityPublicationsData],
    ]
):
    """Kansas City Fed Publications Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveKansasCityPublicationsQueryParams:
        """Transform the query params."""
        return FederalReserveKansasCityPublicationsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveKansasCityPublicationsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Index the Kansas City Fed Agricultural Bulletin PDF archive."""
        from openbb_federal_reserve.utils.kansas_city_publications import (
            list_ag_bulletins,
        )

        catalog = list_ag_bulletins()
        if not catalog:
            raise EmptyDataError("The request was returned empty.")
        return catalog

    @staticmethod
    def transform_data(
        query: FederalReserveKansasCityPublicationsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveKansasCityPublicationsData]:
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
            FederalReserveKansasCityPublicationsData.model_validate(record)
            for record in records
        ]
