"""BLS JOLTS document archive."""

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
from openbb_bls.utils.jolts_catalog import list_releases, scrape_archive

JoltsDocumentCategory = Literal[
    "national",
    "state",
    "archived",
    "all",
]

_API_PREFIX = (
    SystemService()
    .system_settings.python_settings.model_dump()
    .get("api_settings", {})
    .get("prefix", "")
    or "/api/v1"
)


class BlsJoltsDocumentsQueryParams(QueryParams):
    """BLS JOLTS Documents Query Parameters."""

    __json_schema_extra__ = {
        "category": {
            "x-widget_config": {
                "options": [
                    {"label": "All documents", "value": "all"},
                    {"label": "National (current release PDF)", "value": "national"},
                    {"label": "State (current release PDF)", "value": "state"},
                    {
                        "label": "Archived releases (historical PDFs)",
                        "value": "archived",
                    },
                ]
            }
        },
    }

    category: JoltsDocumentCategory = Field(
        default="all",
        description="Family of BLS JOLTS PDFs to enumerate.",
    )
    release_code: str | None = Field(
        default=None,
        description="Optional release code to restrict the results.",
    )
    start_date: dateType | None = Field(
        default=None,
        description="Earliest publication date to include (inclusive).",
    )
    end_date: dateType | None = Field(
        default=None,
        description="Latest publication date to include (inclusive).",
    )


class BlsJoltsDocumentsData(Data):
    """BLS JOLTS Document Reference."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.type": "multi_file_viewer",
                "$.name": "BLS JOLTS Documents",
                "$.description": (
                    "JOLTS release PDFs (national + state), supplemental "
                    "XLSX / TXT files, and the historical release archive."
                ),
                "$.gridData": {"w": 30, "h": 27},
                "$.refetchInterval": False,
                "$.endpoint": f"{_API_PREFIX}/bls/jolts/document_download",
                "$.params": [
                    {
                        "type": "endpoint",
                        "paramName": "url",
                        "optionsEndpoint": f"{_API_PREFIX}/bls/jolts/document_choices",
                        "optionsParams": {
                            "category": "$category",
                            "release_code": "$release_code",
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
                "$.subCategory": "JOLTS",
            }
        }
    )

    name: str = Field(
        description="Human-readable document title.",
    )
    url: str = Field(
        description="Absolute HTTPS URL to the file on bls.gov.",
    )
    category: str = Field(
        description="Document family.",
    )
    release_code: str | None = Field(
        default=None,
        description="Source release code.",
    )
    date: dateType | None = Field(
        default=None,
        description="Publication date of the document.",
    )
    format: str = Field(
        default="pdf",
        description="File format of the document.",
    )


class BlsJoltsDocumentsFetcher(
    Fetcher[BlsJoltsDocumentsQueryParams, list[BlsJoltsDocumentsData]]
):
    """BLS JOLTS Documents Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> BlsJoltsDocumentsQueryParams:
        """Validate and coerce the query."""
        return BlsJoltsDocumentsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BlsJoltsDocumentsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Enumerate release PDFs + supplementals + archived PDFs per the filter."""
        catalog = list_releases()
        out: list[dict[str, Any]] = []
        code_filter = (query.release_code or "").strip().lower() or None

        def _code_ok(code: str) -> bool:
            return code_filter is None or code == code_filter

        latest_dates: dict[str, dateType] = {}
        for entry in catalog:
            for archived in scrape_archive(entry["code"]):
                d = archived.get("date")
                if d is None:
                    continue
                cur = latest_dates.get(entry["code"])
                if cur is None or d > cur:
                    latest_dates[entry["code"]] = d

        include_current = query.category in ("all", "national", "state")
        include_archived = query.category in ("all", "archived")

        if include_current:
            for entry in catalog:
                if (
                    query.category in ("national", "state")
                    and entry["category"] != query.category
                ):
                    continue
                if not _code_ok(entry["code"]):
                    continue
                out.append(
                    {
                        "name": entry["title"],
                        "url": entry["pdf_url"],
                        "category": entry["category"],
                        "release_code": entry["code"],
                        "date": latest_dates.get(entry["code"]),
                        "is_current": True,
                        "format": "pdf",
                    }
                )

        if include_archived:
            codes = [code_filter] if code_filter else [e["code"] for e in catalog]
            for code in codes:
                for archived in scrape_archive(code):
                    if archived["pdf_url"] is None:
                        continue
                    title = archived["title"] or (
                        f"{code} — {archived['date'].isoformat()}"
                    )
                    out.append(
                        {
                            "name": title,
                            "url": archived["pdf_url"],
                            "category": "archived",
                            "release_code": code,
                            "date": archived["date"],
                            "is_current": False,
                            "format": "pdf",
                        }
                    )

        out = apply_date_window(out, query.start_date, query.end_date)

        out.sort(
            key=lambda d: (
                1 if d.get("is_current") else 0,
                d.get("date") or dateType.min,
                d.get("release_code") or "",
                d.get("name") or "",
            ),
            reverse=True,
        )
        for entry in out:
            entry.pop("is_current", None)
        return out

    @staticmethod
    def transform_data(
        query: BlsJoltsDocumentsQueryParams,
        data: list[dict[str, Any]],
        **kwargs: Any,
    ) -> list[BlsJoltsDocumentsData]:
        """Coerce entries into ``BlsJoltsDocumentsData``."""
        if not data:
            raise EmptyDataError("No BLS JOLTS documents matched the requested filter.")
        return [BlsJoltsDocumentsData.model_validate(d) for d in data]
