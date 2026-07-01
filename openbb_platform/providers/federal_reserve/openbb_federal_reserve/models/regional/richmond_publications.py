"""Federal Reserve Bank of Richmond Survey Releases Index Model."""

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


class FederalReserveRichmondPublicationsQueryParams(QueryParams):
    """Richmond Fed Survey Releases Index Query Parameters."""

    __json_schema_extra__ = {
        "survey": {
            "x-widget_config": {
                "options": [
                    {"label": "Manufacturing", "value": "manufacturing"},
                    {"label": "Nonmanufacturing", "value": "non_manufacturing"},
                ]
            }
        }
    }

    survey: Literal["manufacturing", "non_manufacturing"] | None = Field(
        default=None,
        description="Filter the catalog by survey.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveRichmondPublicationsData(Data):
    """Richmond Fed Survey Releases Index Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.type": "multi_file_viewer",
                "$.name": "Richmond Fed Survey Releases",
                "$.description": "Richmond Fed Fifth District manufacturing and"
                " service-sector survey release PDFs. Select one or more to view.",
                "$.category": "Federal Reserve",
                "$.subCategory": "Publications & Reports",
                "$.source": ["Federal Reserve Bank of Richmond"],
                "$.gridData": {"w": 30, "h": 27},
                "$.refetchInterval": False,
                "$.endpoint": f"{api_prefix}/federal_reserve/regional_publications_download",
                "$.params": [
                    {
                        "type": "endpoint",
                        "paramName": "url",
                        "optionsEndpoint": f"{api_prefix}/federal_reserve/regional_publications_choices",
                        "optionsParams": {"district": "richmond"},
                        "show": False,
                        "multiSelect": True,
                        "roles": ["fileSelector"],
                    },
                ],
                "$.data": {},
            }
        }
    )

    date: dateType = Field(description="The survey release date.")
    survey: str = Field(
        description="The survey, 'manufacturing' or 'non_manufacturing'."
    )
    title: str = Field(description="The human-readable release title.")
    url: str = Field(description="The direct URL to the PDF document.")


class FederalReserveRichmondPublicationsFetcher(
    Fetcher[
        FederalReserveRichmondPublicationsQueryParams,
        list[FederalReserveRichmondPublicationsData],
    ]
):
    """Richmond Fed Survey Releases Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveRichmondPublicationsQueryParams:
        """Transform the query params."""
        return FederalReserveRichmondPublicationsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveRichmondPublicationsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Index the Richmond Fed survey release PDF archives."""
        from openbb_federal_reserve.utils.richmond_surveys import list_survey_releases

        catalog = list_survey_releases(query.survey)
        if not catalog:
            raise EmptyDataError("The request was returned empty.")
        return catalog

    @staticmethod
    def transform_data(
        query: FederalReserveRichmondPublicationsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveRichmondPublicationsData]:
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
            FederalReserveRichmondPublicationsData.model_validate(record)
            for record in records
        ]
