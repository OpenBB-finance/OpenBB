"""Federal Reserve Bank of St. Louis data client."""

from __future__ import annotations

import threading
from typing import Any

from openbb_federal_reserve.utils.curl_session import (
    get_session,
    reset_session as _reset,
)

FRED_GRAPH_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
FRED_MD_URL = (
    "https://www.stlouisfed.org/-/media/project/frbstl/stlouisfed/research"
    "/fred-md/monthly/current.csv"
)
FRED_QD_URL = (
    "https://www.stlouisfed.org/-/media/project/frbstl/stlouisfed/research"
    "/fred-md/quarterly/current.csv"
)
FEDINPRINT_PROVIDER = "Federal Reserve Bank of St. Louis"

_WARMUP_HOSTS = (
    "https://www.stlouisfed.org/",
    "https://fred.stlouisfed.org/",
    "https://fraser.stlouisfed.org/",
)


def _warmup(session: Any) -> None:
    """Prime the session against every St. Louis Fed host."""
    for host in _WARMUP_HOSTS:
        session.get(host, timeout=60)


def _get_session() -> Any:
    """Return the calling thread's ``curl_cffi`` session, warmed once per thread."""
    return get_session(f"st_louis:{threading.get_ident()}", _warmup)


def reset_session() -> None:
    """Drop the calling thread's cached session so the next call re-warms it."""
    _reset(f"st_louis:{threading.get_ident()}")


def fetch_text(url: str, referer: str | None = None) -> str:
    """Fetch a St. Louis Fed URL as text, re-warming the session once on a 403.

    Parameters
    ----------
    url : str
        The absolute URL to fetch.
    referer : str | None
        An optional ``Referer`` header value.

    Returns
    -------
    str
        The decoded response body.
    """
    headers = {"Referer": referer} if referer else {}
    session = _get_session()
    response = session.get(url, headers=headers, timeout=180)
    if response.status_code == 403:
        reset_session()
        response = _get_session().get(url, headers=headers, timeout=180)
    response.raise_for_status()
    return response.text


def fetch_bytes(url: str, referer: str | None = None) -> bytes:
    """Fetch a St. Louis Fed URL as bytes, re-warming the session once on a 403.

    Parameters
    ----------
    url : str
        The absolute URL to fetch.
    referer : str | None
        An optional ``Referer`` header value.

    Returns
    -------
    bytes
        The raw response body.
    """
    headers = {"Referer": referer} if referer else {}
    session = _get_session()
    response = session.get(url, headers=headers, timeout=180)
    if response.status_code == 403:
        reset_session()
        response = _get_session().get(url, headers=headers, timeout=180)
    response.raise_for_status()
    return response.content


def fetch_fred_graph_csv(series_id: str) -> str:
    """Download a ``fredgraph.csv`` two-column series, cached weekly.

    Parameters
    ----------
    series_id : str
        The FRED series identifier (for example ``STLFSI4``).

    Returns
    -------
    str
        The raw two-column ``observation_date,<series_id>`` CSV text.
    """
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    return cached(
        ("st_louis_fredgraph", series_id),
        lambda: seconds_until_next_release("weekly"),
        lambda: fetch_text(FRED_GRAPH_URL.format(series_id=series_id)),
    )


def fetch_fred_panel(frequency: str) -> str:
    """Download the FRED-MD or FRED-QD wide panel CSV, cached monthly.

    Parameters
    ----------
    frequency : str
        One of ``"monthly"`` (FRED-MD) or ``"quarterly"`` (FRED-QD).

    Returns
    -------
    str
        The raw panel CSV text including its header and transform/factor rows.
    """
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    if frequency not in ("monthly", "quarterly"):
        raise ValueError("frequency must be 'monthly' or 'quarterly'.")
    url = FRED_MD_URL if frequency == "monthly" else FRED_QD_URL
    return cached(
        ("st_louis_fred_panel", frequency),
        lambda: seconds_until_next_release("monthly"),
        lambda: fetch_text(url),
    )


ST_LOUIS_SERIES: tuple[tuple[str, str], ...] = (
    ("working_papers", "Working Papers"),
    ("review", "Review"),
    ("speech", "Speech"),
    ("economic_synopses", "Economic Synopses"),
    ("national_economic_trends", "National Economic Trends"),
    ("page_one_economics", "Page One Economics Newsletter"),
    ("burgundy_books", "Burgundy Books"),
    ("bridges", "Bridges"),
    ("monetary_trends", "Monetary Trends"),
    ("proceedings", "Proceedings"),
    ("community_development", "Community Development Publications and Reports"),
    ("central_banker", "Central Banker"),
    ("regional_economic_development", "Regional Economic Development"),
    ("inside_the_vault", "Inside the Vault"),
    ("annual_report", "Annual Report"),
    ("international_economic_trends", "International Economic Trends"),
    ("liber8", "Liber8 Economic Information Newsletter"),
    ("in_the_balance", "In the Balance"),
    ("economic_equity_insights", "Economic Equity Insights"),
    ("quarterly_debt_monitor", "Quarterly Debt Monitor"),
    ("demographics_of_wealth", "Demographics of Wealth"),
)

_FACET_BY_SLUG: dict[str, str] = {slug: facet for slug, facet in ST_LOUIS_SERIES}
SERIES_SLUGS: tuple[str, ...] = tuple(_FACET_BY_SLUG)

DEFAULT_LIMIT = 20


def series_choices() -> list[dict[str, str]]:
    """Return series dropdown options mapping each display label to its slug value."""
    from openbb_federal_reserve.utils.fedinprint import clean_label

    return [
        {"label": clean_label(facet), "value": slug} for slug, facet in ST_LOUIS_SERIES
    ]


def list_series() -> list[dict[str, Any]]:
    """Return the supported publication series with their live document counts.

    Returns
    -------
    list[dict[str, Any]]
        One record per supported series with its ``series`` slug, human-readable
        ``name``, and current document ``count``.
    """
    from openbb_federal_reserve.utils import fedinprint
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> list[dict[str, Any]]:
        counts = fedinprint.series_counts(FEDINPRINT_PROVIDER, fetch_text)
        return [
            {
                "series": slug,
                "name": fedinprint.clean_label(facet),
                "count": counts.get(fedinprint.clean_label(facet), 0),
            }
            for slug, facet in ST_LOUIS_SERIES
        ]

    return cached(
        "st_louis_publication_series",
        lambda: seconds_until_next_release("weekly"),
        _producer,
    )


def search_publications(
    series: str | None = None,
    min_year: str = "",
    start: int = 0,
    limit: int = DEFAULT_LIMIT,
) -> list[dict[str, Any]]:
    """Return a page of St. Louis Fed publications from the Fed in Print search.

    Parameters
    ----------
    series : str | None
        A series slug to narrow to one series; ``None`` covers every series.
    min_year : str
        The earliest four-digit year to keep, bounding how far paging descends.
    start : int
        The result offset to begin from, for pagination.
    limit : int
        The maximum number of documents to return.

    Returns
    -------
    list[dict[str, Any]]
        One record per publication with ``series``, ``date``, ``title``, and the
        direct document ``url``, newest first.
    """
    from openbb_federal_reserve.utils import fedinprint

    return fedinprint.resolved_page(
        FEDINPRINT_PROVIDER,
        _FACET_BY_SLUG,
        series,
        min_year,
        start,
        limit,
    )


def list_publications(
    series: str | None = None,
    start_date: Any = None,
    start: int = 0,
    limit: int = DEFAULT_LIMIT,
) -> list[dict[str, Any]]:
    """Return a cached page of St. Louis Fed publications, newest first.

    Parameters
    ----------
    series : str | None
        A series slug to narrow to one series; ``None`` covers every series.
    start_date : datetime.date | None
        The earliest publication date to fetch; bounds how far paging descends.
    start : int
        The result offset to begin from, for pagination.
    limit : int
        The maximum number of documents to return.

    Returns
    -------
    list[dict[str, Any]]
        One record per publication with ``series``, ``date``, ``title``, and the
        direct document ``url``, newest first.
    """
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    slug = series if series in _FACET_BY_SLUG else None
    min_year = str(start_date.year) if start_date else ""
    return cached(
        ("st_louis_publications", slug, min_year, start, limit),
        lambda: seconds_until_next_release("weekly"),
        lambda: search_publications(slug, min_year, start, limit),
    )
