"""Federal Reserve Bank of Cleveland publication-archive indexing.

The Cleveland Fed renders every publication listing through a Sitecore site-search
JSON service at ``/frbc/sitesearch/results``. Each listing page is identified by a
Sitecore item GUID and a ``publication`` facet filter; the service returns one
record per publication carrying its title, release date, authors, and a
``mediaLinks`` array that includes the direct PDF URL. This module pages that
service per series, keeps the records that resolve to a real PDF, and classifies
them into catalog records served as base64-encoded PDFs in the multi-file viewer.
"""

from __future__ import annotations

from typing import Any

BASE_URL = "https://www.clevelandfed.org"
_SEARCH_ENDPOINT = f"{BASE_URL}/frbc/sitesearch/results"
_PAGE_SIZE = 100
_MAX_PAGES = 60
_SORT = "field.sortDate.desc"

_SERIES: dict[str, dict[str, Any]] = {
    "economic_commentary": {
        "label": "Economic Commentary",
        "itemid": "{C9FDAB86-9652-4697-9057-DA522EFB513C}",
        "filters": {"publication": ["Economic Commentary"]},
    },
    "working_paper": {
        "label": "Working Paper",
        "itemid": "{A6E65BC3-D7D4-436E-BE22-475B9609A792}",
        "filters": {
            "contentType": ["Working Paper"],
            "publication": [
                "Working Paper",
                "Financial Services Research Group Working Papers",
            ],
        },
    },
    "policy_discussion_papers": {
        "label": "Policy Discussion Paper",
        "itemid": "{6019927D-5285-4080-999D-B0A04EAA01ED}",
        "filters": {"publication": ["Policy Discussion Papers"]},
    },
    "district_data_brief": {
        "label": "Cleveland Fed District Data Brief",
        "itemid": "{362C2127-553D-498F-9EF7-58904B96D4ED}",
        "filters": {"publication": ["Cleveland Fed District Data Brief"]},
    },
    "annual_report": {
        "label": "Annual Report",
        "itemid": "{8AD0061A-E76D-40B0-808A-1AE53207D971}",
        "filters": {
            "publication": ["Annual Report of the Federal Reserve Bank of Cleveland"]
        },
    },
    "regional_policy_report": {
        "label": "Regional Policy Report",
        "itemid": "{14EC185D-893F-49A5-90C8-A68AD4627408}",
        "filters": {"publication": ["Regional Policy Report"]},
    },
    "economic_review": {
        "label": "Economic Review",
        "itemid": "{029BF2A8-AA11-4E2A-85E1-AB61782DBC71}",
        "filters": {"publication": ["Economic Review"]},
    },
}

_SERIES_LABELS = {name: spec["label"] for name, spec in _SERIES.items()}


def _pdf_link(record: dict[str, Any]) -> str | None:
    """Return the first ``.pdf`` media link on a search record, if any."""
    for link in record.get("mediaLinks") or []:
        if isinstance(link, str) and link.lower().endswith(".pdf"):
            return link
    return None


def _authors(record: dict[str, Any]) -> str | None:
    """Join a search record's author labels into a comma-separated string."""
    names = [
        author.get("label", "").strip()
        for author in record.get("authors") or []
        if author.get("label")
    ]
    return ", ".join(names) or None


def _index_series(name: str) -> list[dict[str, Any]]:
    """Page the site-search service for one series and keep its PDF records."""
    from urllib.parse import urlencode

    from openbb_core.provider.utils.helpers import make_request

    spec = _SERIES[name]
    records: dict[str, dict[str, Any]] = {}
    offset = 0
    for _ in range(_MAX_PAGES):
        params: list[tuple[str, str]] = [
            ("p", str(_PAGE_SIZE)),
            ("e", str(offset)),
            ("o", _SORT),
            ("itemid", spec["itemid"]),
        ]
        params.extend(
            (facet, "|".join(values)) for facet, values in spec["filters"].items()
        )
        response = make_request(f"{_SEARCH_ENDPOINT}?{urlencode(params)}")
        response.raise_for_status()
        payload = response.json()
        results = payload.get("results") or []
        if not results:
            break
        for item in results:
            url = _pdf_link(item)
            if not url:
                continue
            identifier = url.rstrip("/").rsplit("/", 1)[-1]
            records[identifier] = {
                "series": name,
                "id": identifier,
                "date": (item.get("releaseDate") or item.get("sortDate") or "")[:10],
                "title": (item.get("title") or "").strip(),
                "url": url,
                "authors": _authors(item),
            }
        offset += len(results)
        total = (payload.get("pagingInfo") or {}).get("total")
        if total is not None and offset >= total:
            break
    return [
        records[key]
        for key in sorted(records, key=lambda k: records[k]["date"], reverse=True)
    ]


def list_publications(series: str | None = None) -> list[dict[str, Any]]:
    """Return the catalog of Cleveland Fed publication PDFs, newest first.

    Parameters
    ----------
    series : str | None
        One of the keys in ``_SERIES``; ``None`` returns every series merged.

    Returns
    -------
    list[dict]
        Catalog records ``{series, id, date, title, url, authors}``, newest first.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    if series is not None and series not in _SERIES:
        raise OpenBBError(
            f"No Cleveland Fed publication series '{series}'."
            f" Use one of: {', '.join(_SERIES)}."
        )

    targets = [series] if series else list(_SERIES)

    def _producer() -> list[dict[str, Any]]:
        """Index every target series and merge, newest first."""
        records: list[dict[str, Any]] = []
        for name in targets:
            records.extend(_index_series(name))
        return sorted(records, key=lambda record: record["date"], reverse=True)

    return cached(
        ("cleveland_publications", series),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )
