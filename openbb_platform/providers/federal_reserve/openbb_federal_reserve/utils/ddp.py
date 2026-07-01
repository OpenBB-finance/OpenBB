"""Federal Reserve Data Download Program (DDP) catalog and client.

The set of published statistical releases is a fixed, known list - it is encoded
as ``RELEASES`` rather than discovered at runtime, so selecting a dataset never
triggers any catalog or freshness network calls. Each release exposes one or
more preformatted *packages* (data tables) addressed by an opaque hash; the
hashes for a single release are scraped from its ``Choose.aspx`` page once and
cached. Payloads are SDMX-ML, parsed by ``openbb_federal_reserve.utils.sdmx``.
"""

from __future__ import annotations

from typing import Any

CHOOSE_URL = "https://www.federalreserve.gov/datadownload/Choose.aspx"
OUTPUT_URL = "https://www.federalreserve.gov/datadownload/Output.aspx"
STRUCTURE_URL = (
    "https://www.federalreserve.gov/datadownload/Output/{rel}/Metadata/{rel}_struct.xml"
)

# The fixed set of currently-published DDP releases: normalized code ->
# (original-case rel code, display name, public dotted code). Discontinued
# releases are omitted.
RELEASES: dict[str, tuple[str, str, str]] = {
    "H6": ("H6", "Money Stock Measures", "H.6"),
    "H8": (
        "H8",
        "Assets and Liabilities of Commercial Banks in the United States",
        "H.8",
    ),
    "H10": ("H10", "Foreign Exchange Rates", "H.10"),
    "H15": ("H15", "Selected Interest Rates", "H.15"),
    "H41": ("H41", "Factors Affecting Reserve Balances", "H.4.1"),
    "G17": ("G17", "Industrial Production and Capacity Utilization", "G.17"),
    "G19": ("G19", "Consumer Credit", "G.19"),
    "G20": ("G20", "Finance Companies", "G.20"),
    "Z1": ("Z1", "Financial Accounts of the United States", "Z.1"),
    "CP": ("CP", "Commercial Paper", "CP"),
    "CHGDEL": (
        "CHGDEL",
        "Charge-Off and Delinquency Rates on Loans and Leases",
        "CHGDEL",
    ),
    "DSR": ("DSR", "Household Debt Service and Financial Obligations Ratios", "DSR"),
    "SLOOS": (
        "SLOOS",
        "Senior Loan Officer Opinion Survey on Bank Lending Practices",
        "SLOOS",
    ),
    "SCOOS": (
        "scoos",
        "Senior Credit Officer Opinion Survey on Dealer Financing",
        "SCOOS",
    ),
}

# Literal-typed user-facing dataset codes (the public release codes).
DATASET_CHOICES = tuple(public for _, _, public in RELEASES.values())

# The Fed statistical release schedule feed (UTF-8 BOM), distinct from the
# newsevents calendar; powers ``federalreserve.gov/data/releaseschedule.htm``.
SCHEDULE_URL = "https://www.federalreserve.gov/data/statcalendar.json"


def _normalize_release(value: str) -> str:
    """Normalize a public release code (e.g. ``H.15``) to its bare DDP code."""
    return value.replace(".", "").replace(" ", "").strip().upper()


def match_release_title(title: str) -> str | None:
    """Map a release-schedule event title to a DDP public code, else ``None``.

    Titles take the form ``"H.15 - Selected Interest Rates"`` (code prefix),
    ``"... (SLOOS)"`` (parenthetical code), or a code-less name. A leading code
    that is not a current DDP release (e.g. the discontinued ``G.5``/``H.3``)
    returns ``None`` rather than falling through to a same-named release.
    """
    import re

    upper = title.strip().upper()
    for _, _, public in RELEASES.values():
        if (
            re.match(rf"^{re.escape(public.upper())}[\s\-–]", upper)
            or upper == public.upper()
        ):
            return public
    for _, _, public in RELEASES.values():
        if f"({public.upper()})" in upper:
            return public
    if re.match(r"^[A-Z]\.?\d", upper):
        return None
    for _, name, public in RELEASES.values():
        if name.upper() in upper:
            return public
    return None


def list_releases() -> list[dict[str, str]]:
    """Return the fixed catalog of DDP statistical releases (no network)."""
    return [
        {"dataset": public, "code": code, "name": name}
        for code, (_, name, public) in RELEASES.items()
    ]


def fetch_release_schedule() -> list[dict[str, Any]]:
    """Return the Federal Reserve statistical release schedule (cached daily).

    Each scheduled release event is expanded to one row per date, carrying the
    matched DDP public code (``release``) when the event corresponds to a
    currently-published release.
    """
    import json

    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> list[dict[str, Any]]:
        """Download and expand the release-schedule feed into per-date rows."""
        raw = make_request(SCHEDULE_URL, timeout=30).content.decode(
            "utf-8-sig", "replace"
        )
        rows: list[dict[str, Any]] = []
        for event in json.loads(raw).get("events", []):
            title = (event.get("title") or "").strip()
            month = (event.get("month") or "").strip()
            year, _, mon = month.partition("-")
            if not title or not (year and mon):
                continue
            release = match_release_title(title)
            for raw_day in (event.get("days") or "").split(","):
                day = raw_day.strip()
                if not day:
                    continue
                try:
                    iso = f"{int(year):04d}-{int(mon):02d}-{int(day):02d}"
                except ValueError:
                    continue
                rows.append(
                    {
                        "date": iso,
                        "time": (event.get("time") or "").strip() or None,
                        "release": release,
                        "title": title,
                        "event_type": event.get("type"),
                    }
                )
        rows.sort(key=lambda row: row["date"])
        return rows

    return cached(
        "release_schedule",
        lambda: seconds_until_next_release("daily"),
        _producer,
    )


def release_packages(release: str) -> list[dict[str, str]]:
    """Return a release's named data tables, scraping ``Choose.aspx`` once (cached)."""
    import re
    from html import unescape

    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    code = _normalize_release(release)
    if code not in RELEASES:
        return []
    original = RELEASES[code][0]

    def _producer() -> list[dict[str, str]]:
        """Scrape the release's Choose.aspx page for its package hashes and names."""
        response = make_request(f"{CHOOSE_URL}?rel={original}", timeout=30)
        response.raise_for_status()
        text = unescape(response.text)
        # Small releases list packages as radio inputs with a trailing <label>;
        # large releases (e.g. Z.1) list them as <option>s. Both carry the table
        # name immediately before a ``[csv, ...]`` size annotation.
        pattern = (
            r"series=([0-9a-f]{16,})[^\"]*\"[^>]*>"
            r"(?:\s*<label[^>]*>)?\s*([^[<]+?)\s*\["
        )
        packages: list[dict[str, str]] = []
        seen: set[str] = set()
        for package, name in re.findall(pattern, text):
            if package not in seen:
                seen.add(package)
                packages.append({"package": package, "name": name.strip()})
        return packages

    return cached(
        ("ddp_packages", code), lambda: seconds_until_next_release("monthly"), _producer
    )


def list_datasets(dataset: str) -> list[dict[str, str]]:
    """Return the selectable data tables within a single release."""
    code = _normalize_release(dataset)
    entry = RELEASES.get(code)
    name = entry[1] if entry else code
    public = entry[2] if entry else dataset
    return [
        {"table": package["name"], "dataset": public, "release_name": name}
        for package in release_packages(code)
    ]


def resolve_dataset(release: str, table: str | None = None) -> tuple[str, str]:
    """Resolve a release (and optional table) to a ``(release, package)`` pair.

    Selecting a dataset scrapes only that one release's tables (cached) - no
    catalog or freshness calls. With no ``table`` the release's first table is
    used; otherwise the table is matched by name (exact-first, then substring).
    """
    code = _normalize_release(release)
    if code not in RELEASES:
        valid = ", ".join(DATASET_CHOICES)
        raise ValueError(f"Unknown release '{release}'. One of: {valid}.")

    packages = release_packages(code)
    if not packages:
        raise ValueError(f"No data tables found for release '{release}'.")

    if not table:
        return code, packages[0]["package"]

    exact = [p for p in packages if p["name"].lower() == table.lower()]
    partial = [p for p in packages if table.lower() in p["name"].lower()]
    chosen = exact or partial
    if not chosen:
        names = ", ".join(repr(p["name"]) for p in packages)
        raise ValueError(
            f"No table matching '{table}' in release {code}. Available: {names}."
        )
    return code, chosen[0]["package"]


def build_url(
    release: str,
    package: str,
    start_date: str | None = None,
    end_date: str | None = None,
    last_obs: int | None = None,
) -> str:
    """Build a DDP SDMX-ML download URL for a release package.

    An empty ``lastobs=`` is read by the DDP as zero observations, so the limit
    and date-window parameters are OMITTED entirely when unset — a request with
    none of them returns the full series, which is what ``limit=None``/``0`` means.
    """
    from urllib.parse import urlencode

    # With a date window the DDP needs BOTH bounds (a missing one is filled with
    # a wide sentinel it clamps to the series' range).
    if start_date and not end_date:
        end_date = "2099-12-31"
    elif end_date and not start_date:
        start_date = "1900-01-01"

    def _fmt(value: str) -> str:
        """Render an ISO ``YYYY-MM-DD`` date as the DDP ``MM/DD/YYYY`` form."""
        year, month, day = value.split("-")
        return f"{month}/{day}/{year}"

    params = {"rel": release, "series": package}
    if last_obs:
        params["lastobs"] = str(last_obs)
    if start_date:
        params["from"] = _fmt(start_date)
    if end_date:
        params["to"] = _fmt(end_date)
    params["filetype"] = "sdmx"
    params["label"] = "include"
    params["layout"] = "seriescolumn"
    return f"{OUTPUT_URL}?{urlencode(params)}"


def fetch_structure(release: str) -> dict[str, dict[str, str]]:
    """Return a release's dimension codelists from its structure file (cached).

    The structure file is a small, observation-free SDMX document; parsing it
    yields ``{dimension: {code: label}}`` for resolving the data's dimension
    codes to their official Federal Reserve labels.
    """
    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release
    from openbb_federal_reserve.utils.sdmx import parse_structure

    code = _normalize_release(release)

    def _producer() -> dict[str, dict[str, str]]:
        """Fetch and parse the release's structure file."""
        response = make_request(STRUCTURE_URL.format(rel=code), timeout=30)
        if response.status_code != 200:
            return {}
        # The DDP serves UTF-8 (some files with a BOM) but sets no charset.
        return parse_structure(response.content.decode("utf-8-sig", "replace"))

    return cached(
        ("ddp_structure", code),
        lambda: seconds_until_next_release("monthly"),
        _producer,
    )


def _last_n_observations(
    rows: list[dict[str, Any]], limit: int
) -> list[dict[str, Any]]:
    """Keep only each series' most recent ``limit`` observations."""
    from collections import defaultdict

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("series_id"))].append(row)
    trimmed: list[dict[str, Any]] = []
    for series_rows in grouped.values():
        series_rows.sort(key=lambda row: str(row.get("date")))
        trimmed.extend(series_rows[-limit:])
    return trimmed


def fetch_dataset(
    release: str,
    package: str,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Download and parse one DDP data table into long-format rows (cached).

    ``limit`` maps to the DDP ``lastNObservations`` parameter; ``0`` or ``None``
    returns the full series. When the full series is already cached it is sliced
    from the cache rather than re-fetched; otherwise only the last ``limit``
    observations are downloaded.
    """
    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import (
        cached,
        get_cache,
        seconds_until_next_release,
    )
    from openbb_federal_reserve.utils.sdmx import parse_series, to_rows

    full_key = ("ddp", release, package, start_date, end_date)

    def _producer(last_obs: int | None) -> list[dict[str, Any]]:
        """Fetch the SDMX payload and flatten it to labelled rows."""
        response = make_request(
            build_url(release, package, start_date, end_date, last_obs), timeout=60
        )
        response.raise_for_status()
        # The DDP serves UTF-8 (some files with a BOM) but sets no charset.
        xml = response.content.decode("utf-8-sig", "replace")
        return to_rows(parse_series(xml), fetch_structure(release))

    def _ttl() -> float:
        """Expire the entry at the next daily release boundary."""
        return seconds_until_next_release("daily")

    if not limit:
        return cached(full_key, _ttl, lambda: _producer(None))

    cached_full = get_cache().get(full_key)
    if cached_full is not None:
        return _last_n_observations(cached_full, limit)

    return cached((*full_key, "lastobs", limit), _ttl, lambda: _producer(limit))
