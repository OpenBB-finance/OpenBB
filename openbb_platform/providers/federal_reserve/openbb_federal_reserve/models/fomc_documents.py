"""Federal Reserve FOMC documents model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_federal_reserve.utils.fomc_documents import FomcDocumentType
from pydantic import Field, field_validator

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
                "type": "text",
                "value": None,
                "options": choices,
            }
        },
        "pdf_only": {
            "x-widget_config": {"value": True, "type": "boolean", "show": False}
        },
        "as_choices": {
            "x-widget_config": {"value": True, "type": "boolean", "show": False}
        },
    }

    year: Optional[int] = Field(
        default=None,
        description="The year of FOMC documents to retrieve. If None, all years since 1959 are returned.",
    )
    document_type: Optional[str] = Field(
        default=None,
        description=f"Filter by document type. Default is all. Choose from: {', '.join(choice_types)}",
    )
    pdf_only: bool = Field(
        default=False,
        description="Whether to return as a list with only the PDF documents. Default is False.",
    )
    as_choices: bool = Field(
        default=False,
        description="Whether to return cast as a list of valid Workspace parameter choices."
        + " Leave as False for typical use.",
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

    content: Any = Field(
        default=None,
        description="The content of request results."
        + " If `url` was provided, the content is a dictionary with keys `filename` and `content`."
        + " Otherwise, it is a list of dictionaries with a mapping of FOMC documents to URLs."
        + " The endpoint response will not be an OBBject.results object, but the content directly.",
    )


class FederalReserveFomcDocumentsFetcher(
    Fetcher[
        FederalReserveFomcDocumentsQueryParams,
        FederalReserveFomcDocumentsData,
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
    def extract_data(
        query: FederalReserveFomcDocumentsQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        """Extract the raw data."""
        # pylint: disable=import-outside-toplevel
        from openbb_federal_reserve.utils.fomc_documents import (
            get_fomc_documents_by_year,
        )

        docs = get_fomc_documents_by_year(
            query.year, query.document_type, query.pdf_only
        )

        if query.as_choices is True:
            choices_list: list = []
            for doc in docs:
                if query.pdf_only is True and doc.get("doc_format", "") != "pdf":
                    continue
                title = (
                    doc.get("doc_type", "").replace("_", " ").title()
                    + " - "
                    + doc.get("date", "")
                )
                value = doc.get("url", "")
                if title and value:
                    choices_list.append(
                        {
                            "label": title,
                            "value": value,
                        }
                    )

            output = {"content": choices_list}

            return output

        output = {"content": docs}

        return output

    @staticmethod
    def transform_data(
        query: FederalReserveFomcDocumentsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> FederalReserveFomcDocumentsData:
        """Transform data."""
        if not data:
            raise EmptyDataError("No FOMC documents found.")
        return FederalReserveFomcDocumentsData(content=data.get("content"))
