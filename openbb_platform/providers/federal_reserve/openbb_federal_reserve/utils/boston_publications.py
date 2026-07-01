"""Federal Reserve Bank of Boston publication-archive (PDF) helpers.

The Boston Fed hosts New England Economic Conditions (NEEC) as monthly PDFs at a
deterministic Sitecore media path, ``/-/media/Documents/neec/{YYYY}/{YYYYMM}NEEC
.pdf``. The listing page renders its links via JavaScript, so the catalog is
built by constructing candidate URLs over a year-by-month grid and verifying each
against a real PDF magic-number (the host answers missing files with a 200 HTML
soft-404). Verified URLs are served as base64-encoded PDFs for an OpenBB
Workspace PDF widget. Access goes through a single patchable ``fetch_bytes``.
"""

from __future__ import annotations

from datetime import date as dateType
from typing import Any

BASE_URL = "https://www.bostonfed.org"
NEEC_START_YEAR = 2023

_MONTH_NAMES = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


def fetch_bytes(url: str) -> bytes:
    """Return the raw bytes of a Boston Fed URL.

    Parameters
    ----------
    url : str
        The Boston Fed resource URL.

    Returns
    -------
    bytes
        The response body. Wrapped in one helper so a browser-impersonating
        fallback can be substituted if the host begins rejecting plain clients.
    """
    from openbb_core.provider.utils.helpers import make_request

    response = make_request(url)
    response.raise_for_status()
    return response.content


def _neec_url(year: int, month: int) -> str:
    """Return the NEEC media URL for a year and month."""
    return f"{BASE_URL}/-/media/Documents/neec/{year}/{year}{month:02d}NEEC.pdf"


def _is_pdf(content: bytes) -> bool:
    """Return whether the response body is a real PDF rather than a soft-404."""
    return content[:5] == b"%PDF-"


def list_publications(series: str = "neec") -> list[dict[str, Any]]:
    """Return the catalog of Boston Fed NEEC publication PDFs, newest first.

    Parameters
    ----------
    series : str
        The publication series; only ``"neec"`` is supported.

    Returns
    -------
    list[dict]
        One record per verified issue ``{series, id, date, title, url}``.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    if series != "neec":
        raise OpenBBError(f"No Boston Fed publication series '{series}'. Use 'neec'.")

    def _producer() -> list[dict[str, Any]]:
        """Construct candidate NEEC URLs by year/month and verify each PDF."""
        today = dateType.today()
        records: list[dict[str, Any]] = []
        for year in range(NEEC_START_YEAR, today.year + 1):
            last_month = today.month if year == today.year else 12
            for month in range(1, last_month + 1):
                url = _neec_url(year, month)
                try:
                    if not _is_pdf(fetch_bytes(url)):
                        continue
                except Exception:  # noqa: BLE001, S112
                    continue
                records.append(
                    {
                        "series": "neec",
                        "id": f"{year}{month:02d}",
                        "date": dateType(year, month, 1).isoformat(),
                        "title": (
                            f"New England Economic Conditions "
                            f"{_MONTH_NAMES[month - 1]} {year}"
                        ),
                        "url": url,
                    }
                )
        return sorted(records, key=lambda record: record["date"], reverse=True)

    return cached(
        ("boston_publications", series),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )


def fetch_publication_pdf(
    series: str = "neec",
    date: str | None = None,
) -> dict[str, Any]:
    """Return a selected Boston Fed NEEC publication PDF as a base64 payload.

    Parameters
    ----------
    series : str
        The publication series; only ``"neec"`` is supported.
    date : str | None
        The issue month as ``YYYY-MM``; defaults to the most recent release.

    Returns
    -------
    dict
        ``content`` holds the base64-encoded PDF and ``data_format`` its metadata.
    """
    import base64

    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    catalog = list_publications(series)
    if not catalog:
        raise OpenBBError(f"No Boston Fed '{series}' publications are available.")

    selected: dict[str, Any] | None = catalog[0]
    if date:
        target = date[:7]
        selected = next(
            (record for record in catalog if record["date"].startswith(target)), None
        )
        if not selected:
            raise OpenBBError(f"No Boston Fed '{series}' publication for '{date}'.")

    issue_id = selected["id"]

    def _producer() -> str:
        """Download and base64-encode the selected publication PDF."""
        return base64.b64encode(fetch_bytes(selected["url"])).decode("utf-8")

    content = cached(
        ("boston_publication_pdf", issue_id),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )
    return {
        "content": content,
        "data_format": {
            "data_type": "pdf",
            "filename": f"Boston_NEEC_{issue_id}.pdf",
        },
    }
