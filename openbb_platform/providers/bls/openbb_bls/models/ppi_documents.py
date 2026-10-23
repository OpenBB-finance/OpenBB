"""BLS PPI document archive."""

from __future__ import annotations

import calendar
import re
from datetime import (
    date as dateType,
    datetime,
)
from functools import lru_cache
from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field

from openbb_bls.utils.constants import BLS_USER_AGENT

_API_PREFIX = (
    SystemService()
    .system_settings.python_settings.model_dump()
    .get("api_settings", {})
    .get("prefix", "")
    or "/api/v1"
)

_DETAILED_REPORT_EARLIEST = dateType(2005, 6, 1)


class BlsPpiDocumentsQueryParams(QueryParams):
    """BLS PPI Documents Query Parameters."""

    __json_schema_extra__ = {
        "year": {
            "x-widget_config": {
                "options": [
                    {"label": "All Years", "value": None},
                    *[
                        {"label": str(y), "value": y}
                        for y in range(
                            datetime.now().year,
                            _DETAILED_REPORT_EARLIEST.year - 1,
                            -1,
                        )
                    ],
                ],
            }
        },
    }
    category: Literal["detailed_report"] = Field(
        default="detailed_report",
        description="PPI document family. Only the monthly Detailed Report archive is published.",
    )
    year: int | None = Field(
        default=None,
        description="Filter the monthly Detailed Report archive to a single calendar year.",
    )


class BlsPpiDocumentsData(Data):
    """BLS PPI Document Reference."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.type": "multi_file_viewer",
                "$.name": "BLS PPI Detailed PDF Reports Viewer",
                "$.description": ("Producer Price Index detailed report PDF archive."),
                "$.gridData": {"w": 30, "h": 27},
                "$.refetchInterval": False,
                "$.endpoint": f"{_API_PREFIX}/bls/ppi/document_download",
                "$.params": [
                    {
                        "type": "endpoint",
                        "paramName": "url",
                        "optionsEndpoint": f"{_API_PREFIX}/bls/ppi/document_choices",
                        "optionsParams": {
                            "category": "$category",
                            "year": "$year",
                        },
                        "show": False,
                        "multiSelect": True,
                        "roles": ["fileSelector"],
                    },
                ],
                "$.data": {},
                "$.source": ["BLS"],
                "$.category": "Economy",
                "$.subCategory": "PPI",
            }
        }
    )

    name: str = Field(
        description="Human-readable document title for display in the file picker.",
    )
    url: str = Field(
        description="Absolute HTTPS URL to the PDF on bls.gov.",
    )
    category: str = Field(
        description="Document family, matching the category query parameter.",
    )
    date: dateType | None = Field(
        default=None,
        description="Reporting month for the monthly Detailed Report.",
    )
    format: str = Field(
        default="pdf",
        description="File format suffix.",
    )


class BlsPpiDocumentsFetcher(
    Fetcher[BlsPpiDocumentsQueryParams, list[BlsPpiDocumentsData]]
):
    """BLS PPI Documents Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> BlsPpiDocumentsQueryParams:
        """Validate and coerce the query."""
        return BlsPpiDocumentsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BlsPpiDocumentsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Read the BLS detailed-report index page and emit one entry per PDF."""
        return _list_detailed_reports(query.year)

    @staticmethod
    def transform_data(
        query: BlsPpiDocumentsQueryParams,
        data: list[dict[str, Any]],
        **kwargs: Any,
    ) -> list[BlsPpiDocumentsData]:
        """Coerce parsed rows into ``BlsPpiDocumentsData``."""
        if not data:
            raise EmptyDataError("No BLS PPI documents matched the requested filter.")
        return [BlsPpiDocumentsData.model_validate(d) for d in data]


_INDEX_URL = "https://www.bls.gov/ppi/detailed-report/"
_INDEX_HEADERS = {
    "User-Agent": BLS_USER_AGENT,
    "Accept": "text/html,*/*",
}
_PDF_RE = re.compile(
    r"/ppi/detailed-report/ppi-(?:detailed-report|tables)-"
    r"(?P<month>[a-z]+)-(?P<year>\d{4})\.pdf$",
    re.IGNORECASE,
)
_MONTH_NAME_TO_NUM = {calendar.month_name[_m].lower(): _m for _m in range(1, 13)}


@lru_cache(maxsize=1)
def _scrape_detailed_report_index() -> tuple[dict[str, Any], ...]:
    """Scrape the BLS detailed-report index page for every published PDF."""
    from bs4 import BeautifulSoup
    from openbb_core.provider.utils.helpers import get_requests_session

    session = get_requests_session()
    resp = session.get(_INDEX_URL, headers=_INDEX_HEADERS, timeout=30)

    if resp.status_code != 200:
        raise OpenBBError(
            f"BLS returned HTTP {resp.status_code} fetching {_INDEX_URL}."
        )
    soup = BeautifulSoup(resp.text, "lxml")
    seen: set[str] = set()
    docs: list[dict[str, Any]] = []

    for anchor in soup.find_all("a", href=True):
        href = str(anchor["href"]).strip()
        match = _PDF_RE.search(href)

        if not match:
            continue

        month_name = match.group("month").lower()
        year = int(match.group("year"))
        month = _MONTH_NAME_TO_NUM.get(month_name)

        if month is None:
            continue

        url = href if href.startswith("http") else f"https://www.bls.gov{href}"

        if url in seen:
            continue

        seen.add(url)
        docs.append(
            {
                "name": f"PPI Detailed Report — {calendar.month_name[month]} {year}",
                "url": url,
                "category": "detailed_report",
                "date": dateType(year, month, 1),
                "format": "pdf",
            }
        )

    docs.sort(key=lambda d: d["date"], reverse=True)

    return tuple(docs)


def _list_detailed_reports(year_filter: int | None) -> list[dict[str, Any]]:
    """Return every monthly PPI Detailed Report PDF, optionally filtered by year."""
    docs = _scrape_detailed_report_index()
    if year_filter is None:
        return [dict(d) for d in docs]
    return [dict(d) for d in docs if d["date"].year == year_filter]
