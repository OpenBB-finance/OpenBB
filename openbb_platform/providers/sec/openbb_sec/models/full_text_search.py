"""SEC Full-Text Search Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator


class SecFullTextSearchQueryParams(QueryParams):
    """SEC Full-Text Search Query Parameters.

    Source: https://efts.sec.gov/LATEST/search-index
    """

    __json_schema_extra__ = {
        "category": {
            "x-widget_config": {
                "label": "Filing Category",
                "type": "endpoint",
                "optionsEndpoint": "/api/v1/sec/fts_categories",
                "style": {"popupWidth": 700},
            }
        },
        "form_type": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "label": "Form Type",
                # Free-text multi-value with autocomplete: the EDGAR full-text
                # API supports exclusion (e.g. ``-4``, ``-10-K/A``) and amendment
                # codes that a strict dropdown cannot express, so values must be
                # typeable, not constrained to the suggestion list.
                "type": "text",
                "multiSelect": True,
                "optionsEndpoint": "/api/v1/sec/fts_form_types",
            },
        },
        "location": {
            "x-widget_config": {
                "label": "Located In",
                "type": "endpoint",
                "optionsEndpoint": "/api/v1/sec/fts_locations",
                "style": {"popupWidth": 400},
            }
        },
    }

    query: str | None = Field(
        default=None,
        description="Words or phrases to find in filing documents. Use quotes for an"
        + " exact phrase, OR / NOT (or -) for boolean logic, and * for a trailing"
        + " wildcard.",
    )
    entity: str | None = Field(
        default=None,
        description="Company name, ticker, CIK number, or individual's name.",
    )
    category: str | None = Field(
        default=None,
        description="Filing category to filter by - a preset group of form types.",
    )
    form_type: str | None = Field(
        default=None,
        description="Specific form type(s) to filter by, comma-separated. Prefix a"
        + " form type with a hyphen to exclude it - e.g., -4 excludes Form 4.",
    )
    location: str | None = Field(
        default=None,
        description="Location code of the principal executive offices to filter by.",
    )
    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", "")
        + " The earliest available date is 2001-01-01.",
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )
    limit: int = Field(
        default=100,
        description=QUERY_DESCRIPTIONS.get("limit", ""),
    )

    @field_validator("form_type", mode="before", check_fields=False)
    @classmethod
    def _normalize_form_type(cls, v):
        """Normalize the form-type selection to EDGAR's comma-separated string.

        The Workspace multi-select sends a JSON-array string (e.g. ``["S-1","8-K"]``);
        accept that, a real list/tuple, or a plain comma-separated string.
        """
        if isinstance(v, str):
            stripped = v.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                import json

                try:
                    v = json.loads(stripped)
                except (ValueError, TypeError):
                    return stripped or None
        if isinstance(v, (list, tuple)):
            return ",".join(str(i).strip() for i in v if str(i).strip()) or None
        return v or None


class SecFullTextSearchData(Data):
    """SEC Full-Text Search Data."""

    filing_date: dateType | None = Field(
        default=None, description="Date the filing was submitted."
    )
    form: str | None = Field(default=None, description="The SEC form type.")
    name: str | None = Field(default=None, description="Name of the filer(s).")
    symbol: str | None = Field(
        default=None, description="Ticker symbol(s) of the filer."
    )
    cik: str | None = Field(
        default=None, description="Central Index Key(s) of the filer."
    )
    description: str | None = Field(
        default=None, description="Filing or document description."
    )
    url: str = Field(description="URL of the matched document on SEC EDGAR.")


class SecFullTextSearchFetcher(
    Fetcher[SecFullTextSearchQueryParams, list[SecFullTextSearchData]]
):
    """SEC Full-Text Search Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecFullTextSearchQueryParams:
        """Transform the query parameters."""
        return SecFullTextSearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecFullTextSearchQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the raw data from EDGAR full-text search."""
        from urllib.parse import urlencode

        from openbb_core.provider.utils.helpers import amake_request

        from openbb_sec.utils.definitions import SEC_HEADERS

        forms = ",".join(part for part in (query.category, query.form_type) if part)
        criteria = [
            query.query,
            query.entity,
            forms,
            query.location,
            query.start_date and query.end_date,
        ]
        if not any(criteria):
            raise EmptyDataError("At least one search criterion is required.")

        headers = {
            "User-Agent": SEC_HEADERS.get(
                "User-Agent", "OpenBB Platform support@openbb.co"
            ),
            "Accept-Encoding": "gzip, deflate",
        }
        cap = query.limit or 100
        results: list = []
        offset = 0
        while len(results) < cap:
            params: dict = {"from": offset}
            if query.query:
                params["q"] = query.query
            if query.entity:
                params["entityName"] = query.entity
            if forms:
                params["forms"] = forms
            if query.location:
                params["locationCodes"] = query.location
            if query.start_date and query.end_date:
                params.update(
                    dateRange="custom",
                    startdt=query.start_date.strftime("%Y-%m-%d"),
                    enddt=query.end_date.strftime("%Y-%m-%d"),
                )
            url = "https://efts.sec.gov/LATEST/search-index?" + urlencode(params)
            try:
                response = await amake_request(url, headers=headers)
            except Exception as e:  # noqa: BLE001
                raise OpenBBError(f"Failed to get SEC data: {e}") from e
            if not isinstance(response, dict):
                break
            hits_obj = response.get("hits", {})
            hits = hits_obj.get("hits", [])
            if not hits:
                break
            results.extend(hits)
            offset += len(hits)
            if offset >= hits_obj.get("total", {}).get("value", 0):
                break

        return results[:cap]

    @staticmethod
    def transform_data(
        query: SecFullTextSearchQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[SecFullTextSearchData]:
        """Transform the raw data into the data model."""
        import re

        if not data:
            raise EmptyDataError("No filings were found for the search criteria.")

        results: list[SecFullTextSearchData] = []
        seen: set = set()
        for hit in data:
            source = hit.get("_source", {})
            ciks = source.get("ciks") or []
            doc_id = hit.get("_id", "")
            if not ciks or ":" not in doc_id:
                continue
            url = (
                f"https://www.sec.gov/Archives/edgar/data/{ciks[0]}/"
                f"{source.get('adsh', '').replace('-', '')}/{doc_id.split(':')[1]}"
            )
            if url in seen:
                continue
            seen.add(url)
            names, tickers = [], []
            for display in source.get("display_names", []):
                names.append(display.split("(")[0].strip())
                for part in re.findall(r"\(([^)]*)\)", display):
                    if not part.upper().startswith("CIK"):
                        tickers.append(part.strip())
            results.append(
                SecFullTextSearchData.model_validate(
                    {
                        "filing_date": source.get("file_date"),
                        "form": source.get("form"),
                        "name": ", ".join(n for n in names if n) or None,
                        "symbol": ", ".join(t for t in tickers if t) or None,
                        "cik": ", ".join(c.lstrip("0") or c for c in ciks) or None,
                        "description": source.get("file_description"),
                        "url": url,
                    }
                )
            )

        return results
