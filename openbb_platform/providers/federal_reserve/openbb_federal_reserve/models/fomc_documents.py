"""Federal Reserve FOMC documents model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any

from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_federal_reserve.utils.fomc_documents import FomcDocumentType
from pydantic import ConfigDict, Field, field_validator

api_prefix = (
    SystemService()
    .system_settings.python_settings.model_dump()
    .get("api_settings", {})
    .get("prefix", "")
    or "/api/v1"
)

choice_types = list(FomcDocumentType.__args__)
choices = [
    {
        "label": (
            "All Documents" if choice == "all" else choice.replace("_", " ").title()
        ),
        "value": choice if choice != "all" else None,
    }
    for choice in choice_types
]


class FederalReserveFomcDocumentsQueryParams(QueryParams):
    """Federal Reserve FOMC Documents Query."""

    __json_schema_extra__ = {
        "year": {
            "x-widget_config": {
                "type": "number",
                "value": None,
                "options": [
                    {"label": "All Years", "value": None},
                    *[
                        {"label": str(year), "value": year}
                        for year in sorted(
                            range(1959, datetime.now().year + 1), reverse=True
                        )
                    ],
                ],
            }
        },
        "document_type": {
            "x-widget_config": {
                "options": choices,
                "description": "Filter by document type. Default is all.",
            }
        },
    }

    year: int | None = Field(
        default=None,
        description="The year of FOMC documents to retrieve. If None, all years since 1959 are returned.",
    )
    document_type: str | None = Field(
        default=None,
        description=f"Filter by document type. Default is all. Choose from: {', '.join(choice_types)}",
    )

    @field_validator("document_type", mode="before", check_fields=False)
    @classmethod
    def _validate_doc_type(cls, v):
        """Validate document type."""
        if v and v not in choice_types:
            raise ValueError(
                f"Invalid document type. Must be one of: {', '.join(choice_types)}"
            )
        return v


class FederalReserveFomcDocumentsData(Data):
    """Federal Reserve FOMC Documents Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.type": "multi_file_viewer",
                "$.name": "FOMC PDF Document Viewer",
                "$.description": "Current and historical FOMC PDF materials.",
                "$.gridData": {
                    "w": 30,
                    "h": 27,
                },
                "$.refetchInterval": False,
                "$.endpoint": f"{api_prefix}/federal_reserve/fomc_documents_download",
                "$.params": [
                    {
                        "type": "endpoint",
                        "paramName": "url",
                        "optionsEndpoint": f"{api_prefix}/federal_reserve/fomc_documents_choices",
                        "optionsParams": {
                            "document_type": "$document_type",
                            "year": "$year",
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

    date: dateType = Field(
        description="The date of the document, formatted as YYYY-MM-DD.",
    )
    doc_type: str = Field(
        description="The type of the FOMC document.",
    )
    doc_format: str = Field(
        description="The format of the document (e.g., pdf, htm).",
    )
    url: str = Field(
        description="The URL of the document.",
    )


class FederalReserveFomcDocumentsFetcher(
    Fetcher[
        FederalReserveFomcDocumentsQueryParams,
        list[FederalReserveFomcDocumentsData],
    ]
):
    """Federal Reserve FOMC Documents Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveFomcDocumentsQueryParams:
        """Transform query."""
        return FederalReserveFomcDocumentsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FederalReserveFomcDocumentsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the raw data."""
        # pylint: disable=import-outside-toplevel
        from openbb_federal_reserve.utils.fomc_documents import (
            get_fomc_documents_by_year,
        )

        return get_fomc_documents_by_year(query.year, query.document_type)

    @staticmethod
    def transform_data(
        query: FederalReserveFomcDocumentsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveFomcDocumentsData]:
        """Transform data."""
        if not data:
            raise EmptyDataError("No FOMC documents found.")
        return [FederalReserveFomcDocumentsData.model_validate(d) for d in data]
