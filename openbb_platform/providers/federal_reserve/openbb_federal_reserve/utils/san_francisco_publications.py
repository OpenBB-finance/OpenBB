"""San Francisco Fed publications enumeration and PDF presentation.

The FRBSF Economic Letter and SF FedViews are published as per-release PDFs and
catalogued through the WordPress REST API. This module enumerates that catalog
via the ``sffed_publications`` endpoint and serves a selected publication as a
base64-encoded PDF for an OpenBB Workspace PDF widget. Each entry's PDF URL is
derived from its release metadata and, when the derived name is wrong (revised
or suffixed files), resolved by scraping the entry's landing page.
"""

from __future__ import annotations

import re
from typing import Any

BASE_URL = "https://www.frbsf.org"
WP_JSON_URL = f"{BASE_URL}/wp-json/wp/v2/sffed_publications"
UPLOADS_URL = f"{BASE_URL}/wp-content/uploads"

PUBLICATION_TYPES = {
    "economic_letter": 1805,
    "fedviews": 1807,
}
_TYPE_LABELS = {
    "economic_letter": "FRBSF Economic Letter",
    "fedviews": "SF FedViews",
}
_PREFIX = {"economic_letter": "el", "fedviews": "fv"}


def _derive_pdf(publication_type: str, entry: dict[str, Any]) -> str | None:
    """Return the conventional PDF URL for an entry, or ``None`` if underivable."""
    if publication_type == "economic_letter":
        meta = entry.get("meta", {})
        volume = str(meta.get("publication_volume", "")).strip()
        issue = str(meta.get("publication_issue", "")).strip()
        if volume.isdigit() and issue.isdigit():
            return f"{UPLOADS_URL}/el{volume}-{int(issue):02d}.pdf"
        return None
    yyyymmdd = entry["date"][:10].replace("-", "")
    return f"{UPLOADS_URL}/fv{yyyymmdd}.pdf"


def _record(publication_type: str, entry: dict[str, Any]) -> dict[str, Any]:
    """Build a catalog record for a single publication entry."""
    meta = entry.get("meta", {})
    title = entry.get("title", {}).get("rendered", entry.get("slug", ""))
    return {
        "date": entry["date"][:10],
        "publication_type": publication_type,
        "slug": entry.get("slug", ""),
        "title": re.sub(r"<[^>]+>", "", title).strip(),
        "volume": str(meta.get("publication_volume", "")).strip() or None,
        "issue": str(meta.get("publication_issue", "")).strip() or None,
        "link": entry.get("link", ""),
        "url": _derive_pdf(publication_type, entry),
    }


def list_publications(
    publication_type: str | None = None,
) -> list[dict[str, Any]]:
    """Return the catalog of publications for a type, newest first.

    Parameters
    ----------
    publication_type : str | None
        One of ``"economic_letter"`` or ``"fedviews"``; when ``None`` every
        publication type is enumerated and merged, newest first.

    Returns
    -------
    list[dict[str, Any]]
        Catalog records, newest first.
    """
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    if publication_type is None:
        merged: list[dict[str, Any]] = []
        for series in PUBLICATION_TYPES:
            merged.extend(list_publications(series))
        return sorted(merged, key=lambda record: record["date"], reverse=True)

    type_id = PUBLICATION_TYPES.get(publication_type)
    if type_id is None:
        raise OpenBBError(f"Unknown publication type '{publication_type}'.")

    def _producer() -> list[dict[str, Any]]:
        """Page the wp-json endpoint and classify every entry."""
        records: list[dict[str, Any]] = []
        page = 1
        total_pages = 1
        while page <= total_pages:
            response = make_request(
                f"{WP_JSON_URL}?publication-type={type_id}&per_page=100&page={page}"
            )
            response.raise_for_status()
            total_pages = int(response.headers.get("X-WP-TotalPages", "1") or "1")
            for entry in response.json():
                records.append(_record(publication_type, entry))
            page += 1
        return sorted(records, key=lambda record: record["date"], reverse=True)

    return cached(
        ("san_francisco_publications", publication_type),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )


def _resolve_pdf_url(record: dict[str, Any]) -> str:
    """Return the working PDF URL for a record, scraping when the derived one fails."""
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.helpers import make_request

    candidate = record.get("url")
    if candidate:
        head = make_request(candidate)
        if head.ok and "pdf" in (head.headers.get("Content-Type") or ""):
            return candidate

    prefix = _PREFIX[record["publication_type"]]
    page = make_request(record["link"])
    page.raise_for_status()
    match = re.search(
        rf"({re.escape(UPLOADS_URL)}/{prefix}[^\"'<> ]+?\.pdf)", page.text
    )
    if match:
        return match.group(1)
    raise OpenBBError(f"Could not resolve a PDF for '{record['slug']}'.")


def fetch_publication_pdf(
    publication_type: str = "economic_letter", date: str | None = None
) -> dict[str, Any]:
    """Return a selected publication as a base64-encoded PDF payload.

    Parameters
    ----------
    publication_type : str
        One of ``"economic_letter"`` or ``"fedviews"``.
    date : str | None
        The publication month as ``YYYY-MM``; defaults to the most recent release.

    Returns
    -------
    dict[str, Any]
        ``content`` holds the base64-encoded PDF and ``data_format`` its metadata.
    """
    import base64

    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    catalog = list_publications(publication_type)
    if not catalog:
        raise OpenBBError(
            f"No '{_TYPE_LABELS.get(publication_type, publication_type)}'"
            + " publications are available."
        )

    selected = catalog[0]
    if date:
        target = date[:7]
        selected = next(  # type: ignore[assignment]
            (record for record in catalog if record["date"].startswith(target)), None
        )
        if not selected:
            raise OpenBBError(
                f"No '{_TYPE_LABELS.get(publication_type, publication_type)}'"
                + f" publication for '{date}'."
            )

    url = _resolve_pdf_url(selected)

    def _producer() -> str:
        """Download and base64-encode the selected publication PDF."""
        response = make_request(url)
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")

    content = cached(
        ("san_francisco_publication_pdf", selected["publication_type"], url),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )
    filename = url.rsplit("/", 1)[-1]
    return {
        "content": content,
        "data_format": {"data_type": "pdf", "filename": filename},
    }
