"""Chicago Fed publication-archive (PDF) indexing and presentation."""

from __future__ import annotations

from datetime import date as dateType
from typing import Any

_SERIES = {
    "agletter": {
        "guid": "88B3A2C2A26747C9878052EE76B466D7",
        "label": "AgLetter",
        "cadence": "quarterly",
    },
    "chicago_fed_letter": {
        "guid": "963ADC67B1D64F7CBAC86DE1E9B7B4EE",
        "label": "Chicago Fed Letter",
        "cadence": "monthly",
    },
    "economic_perspectives": {
        "guid": "C59705AF645E4C3BBC6770001E280146",
        "label": "Economic Perspectives",
        "cadence": "quarterly",
    },
    "working_papers": {
        "guid": "012AE8CBBFAF461981729EE5A82D1C30",
        "label": "Working Papers",
        "cadence": "monthly",
    },
}

_MAX_PAGES = 60


def _parse_date(value: str | None) -> dateType | None:
    """Parse a feed date string into a ``date``, or ``None``."""
    if not value or not value.isdigit() or len(value) not in (4, 6, 8):
        return None
    year = int(value[:4])
    month = int(value[4:6]) if len(value) >= 6 else 1
    day = int(value[6:8]) if len(value) == 8 else 1
    if not 1 <= month <= 12 or not 1 <= day <= 31:
        return None
    return dateType(year, month, day)


def _record(series: str, entry: dict[str, Any]) -> dict[str, Any] | None:
    """Build a catalog record from a raw NewsFeed entry, or ``None`` if unusable."""
    pub_date = _parse_date(entry.get("Date"))
    link = entry.get("PublicationLink") or ""
    if pub_date is None or not link:
        return None
    return {
        "date": pub_date.isoformat(),
        "series": series,
        "title": (entry.get("Title") or "").strip(),
        "volume": (str(entry.get("Volume")).strip() or None)
        if entry.get("Volume")
        else None,
        "issue": (str(entry.get("Issue")).strip() or None)
        if entry.get("Issue")
        else None,
        "landing_url": entry.get("Url") or "",
        "url": link.split("?", 1)[0],
    }


def list_publications(series: str | None = None) -> list[dict[str, Any]]:
    """Return the catalog of Chicago Fed publication PDFs, newest first.

    Parameters
    ----------
    series : str | None
        A single series key to enumerate; ``None`` enumerates every series.

    Returns
    -------
    list[dict[str, Any]]
        Catalog records, newest first.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release
    from openbb_federal_reserve.utils.chicago import post_newsfeed

    if series is not None and series not in _SERIES:
        raise OpenBBError(
            f"Unknown publication series '{series}'. Choose from {sorted(_SERIES)}."
        )
    targets = [series] if series else list(_SERIES)

    def _producer() -> list[dict[str, Any]]:
        """Page each target series' NewsFeed and classify every entry."""
        records: dict[tuple[str, str], dict[str, Any]] = {}
        for name in targets:
            for page in range(1, _MAX_PAGES + 1):
                feed = post_newsfeed(_SERIES[name]["guid"], page)
                if not feed:
                    break
                before = len(records)
                for entry in feed:
                    record = _record(name, entry)
                    if record is None:
                        continue
                    records[(name, record["url"])] = record
                if len(records) == before:
                    break
        return sorted(
            records.values(),
            key=lambda record: (record["date"], record["title"]),
            reverse=True,
        )

    return cached(
        ("chicago_publications", series),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )


def fetch_publication_pdf(
    series: str = "agletter",
    date: str | None = None,
) -> dict[str, Any]:
    """Return a selected Chicago Fed publication PDF as a base64 payload.

    Parameters
    ----------
    series : str
        The publication series key; defaults to ``agletter``.
    date : str | None
        A ``YYYY-MM`` (or longer) prefix to select an issue; defaults to latest.

    Returns
    -------
    dict[str, Any]
        ``content`` holds the base64-encoded PDF and ``data_format`` its metadata.
    """
    import base64

    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release
    from openbb_federal_reserve.utils.chicago import get_bytes

    if series not in _SERIES:
        raise OpenBBError(
            f"Unknown publication series '{series}'. Choose from {sorted(_SERIES)}."
        )
    catalog = list_publications(series)
    if not catalog:
        raise OpenBBError(
            f"No Chicago Fed '{_SERIES[series]['label']}' publications are available."
        )

    selected: dict[str, Any] | None = catalog[0]
    if date:
        target = date[:7]
        selected = next(
            (record for record in catalog if record["date"].startswith(target)), None
        )
        if not selected:
            raise OpenBBError(f"No Chicago Fed '{series}' publication for '{date}'.")

    def _producer() -> str:
        """Download and base64-encode the selected publication PDF."""
        return base64.b64encode(get_bytes(selected["url"])).decode("utf-8")

    content = cached(
        ("chicago_publication_pdf", selected["series"], selected["url"]),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )
    filename = selected["url"].rsplit("/", 1)[-1] or f"{series}.pdf"
    return {
        "content": content,
        "data_format": {"data_type": "pdf", "filename": filename},
    }
