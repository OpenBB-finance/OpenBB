"""BLS Real Earnings (REALER) release document archive."""

from __future__ import annotations

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field

from openbb_bls.utils.helpers import apply_date_window
from openbb_bls.utils.realer_archive import current_release, scrape_archive

RealerDocumentCategory = Literal["all", "current", "archived"]

_API_PREFIX = (
    SystemService()
    .system_settings.python_settings.model_dump()
    .get("api_settings", {})
    .get("prefix", "")
    or "/api/v1"
)


class BlsRealerDocumentsQueryParams(QueryParams):
    """BLS Real Earnings Documents Query Parameters."""

    __json_schema_extra__ = {
        "category": {
            "x-widget_config": {
                "options": [
                    {"label": "All documents", "value": "all"},
                    {"label": "Current release PDF only", "value": "current"},
                    {"label": "Archived releases", "value": "archived"},
                ]
            }
        },
    }

    category: RealerDocumentCategory = Field(
        default="all",
        description="Which family of BLS Real Earnings release PDFs to enumerate.",
    )
    start_date: dateType | None = Field(
        default=None,
        description="Earliest publication date to include (inclusive). Applies to archived releases only.",
    )
    end_date: dateType | None = Field(
        default=None,
        description="Latest publication date to include (inclusive). Applies to archived releases only.",
    )


class BlsRealerDocumentsData(Data):
    """BLS Real Earnings Document Reference."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.type": "multi_file_viewer",
                "$.name": "BLS Real Earnings Documents",
                "$.description": (
                    "Real Earnings release PDFs — current edition plus monthly archive."
                ),
                "$.gridData": {"w": 30, "h": 27},
                "$.refetchInterval": False,
                "$.endpoint": f"{_API_PREFIX}/bls/real_earnings/document_download",
                "$.params": [
                    {
                        "type": "endpoint",
                        "paramName": "url",
                        "optionsEndpoint": f"{_API_PREFIX}/bls/real_earnings/document_choices",
                        "optionsParams": {
                            "category": "$category",
                            "start_date": "$start_date",
                            "end_date": "$end_date",
                        },
                        "show": False,
                        "multiSelect": True,
                        "roles": ["fileSelector"],
                    },
                ],
                "$.data": {},
                "$.source": ["BLS"],
                "$.category": "Economy",
                "$.subCategory": "Real Earnings",
            }
        }
    )

    name: str = Field(
        description="Human-readable document title.",
    )
    url: str = Field(
        description="Absolute HTTPS URL to the PDF on bls.gov.",
    )
    category: str = Field(
        description="Document family (current or archived).",
    )
    date: dateType | None = Field(
        default=None,
        description="Release publication date.",
    )
    format: str = Field(
        default="pdf",
        description="File format of the document.",
    )


class BlsRealerDocumentsFetcher(
    Fetcher[BlsRealerDocumentsQueryParams, list[BlsRealerDocumentsData]]
):
    """BLS Real Earnings Documents Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> BlsRealerDocumentsQueryParams:
        """Validate and coerce the query."""
        return BlsRealerDocumentsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BlsRealerDocumentsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Enumerate the current + archived Real Earnings release PDFs per the filter."""
        archive = scrape_archive()
        latest_date = archive[0]["date"] if archive else None

        out: list[dict[str, Any]] = []
        include_current = query.category in ("all", "current")
        include_archived = query.category in ("all", "archived")

        if include_current:
            cur = current_release()
            out.append(
                {
                    "name": cur["title"],
                    "url": cur["url"],
                    "category": "current",
                    "date": latest_date,
                    "is_current": True,
                    "format": "pdf",
                }
            )

        if include_archived:
            for entry in archive:
                out.append(
                    {
                        "name": entry["title"],
                        "url": entry["url"],
                        "category": "archived",
                        "date": entry["date"],
                        "is_current": False,
                        "format": "pdf",
                    }
                )

        out = apply_date_window(out, query.start_date, query.end_date)

        out.sort(
            key=lambda d: (
                1 if d.get("is_current") else 0,
                d.get("date") or dateType.min,
                d.get("name") or "",
            ),
            reverse=True,
        )
        for entry in out:
            entry.pop("is_current", None)
        return out

    @staticmethod
    def transform_data(
        query: BlsRealerDocumentsQueryParams,
        data: list[dict[str, Any]],
        **kwargs: Any,
    ) -> list[BlsRealerDocumentsData]:
        """Coerce entries into BlsRealerDocumentsData."""
        if not data:
            raise EmptyDataError(
                "No BLS Real Earnings documents matched the requested filter."
            )
        return [BlsRealerDocumentsData.model_validate(d) for d in data]
