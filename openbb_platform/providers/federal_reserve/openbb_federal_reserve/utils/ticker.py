"""Resolve publicly-traded bank tickers to their parent holding company RSSD."""

from __future__ import annotations

import re

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"

_STATES = set(
    [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]
)

_DROP = {
    "THE",
    "CORP",
    "CORPORATION",
    "INCORPORATED",
    "INC",
    "CO",
    "COMPANY",
    "COMPANIES",
    "NA",
    "LTD",
    "LP",
    "PLC",
    "NEW",
}


def normalize_name(name: str) -> str:
    """Return an order-independent normalized key for a legal entity name."""
    cleaned = (name or "").upper().split("/")[0]
    cleaned = cleaned.replace(".", "").replace("&", " AND ")
    cleaned = re.sub(r"[^A-Z0-9 ]", " ", cleaned)
    tokens = cleaned.split()
    while tokens and tokens[-1] in _STATES:
        tokens.pop()
    return " ".join(sorted(t for t in tokens if t not in _DROP))


def is_parent_holding_company(record: dict) -> bool:
    """Return True when a NIC record is a holding company (a potential parent)."""
    return (
        record.get("BHC_IND") == "1"
        or record.get("FHC_IND") == "1"
        or record.get("SLHC_IND") == "1"
    )


def fetch_sec_tickers() -> dict[str, str]:
    """Return a ``{ticker: issuer_name}`` map from the SEC bulk file, cached weekly."""
    from openbb_core.provider.utils.helpers import make_request

    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> dict[str, str]:
        """Download and flatten the SEC company-tickers file."""
        response = make_request(
            SEC_TICKERS_URL,
            headers={"User-Agent": "OpenBB federal_reserve hello@openbb.co"},
        )
        response.raise_for_status()
        return {
            str(entry["ticker"]).upper(): entry["title"]
            for entry in response.json().values()
        }

    return cached(
        "sec_tickers",
        lambda: seconds_until_next_release("weekly"),
        _producer,
    )


def parent_name_index() -> dict[str, str]:
    """Return a ``{normalized_name: rssd_id}`` index of parent holding companies."""
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release
    from openbb_federal_reserve.utils.ffiec import fetch_institutions

    def _producer() -> dict[str, str]:
        """Build the parent-holding-company name index from the NIC directory."""
        index: dict[str, str] = {}
        for record in fetch_institutions("active"):
            if not is_parent_holding_company(record):
                continue
            key = normalize_name(record.get("NM_LGL", ""))
            rssd_id = record.get("#ID_RSSD")
            if key and rssd_id:
                index.setdefault(key, rssd_id)
        return index

    return cached(
        "parent_name_index",
        lambda: seconds_until_next_release("daily"),
        _producer,
    )


def resolve_ticker_to_rssd(ticker: str) -> str | None:
    """Resolve a stock ticker to its parent holding company's RSSD, or ``None``."""
    title = fetch_sec_tickers().get(ticker.strip().upper())
    if not title:
        return None
    return parent_name_index().get(normalize_name(title))


def controlled_subtree(parent_rssd: str) -> set[str]:
    """Return every RSSD in a parent's active, controlled ownership subtree."""
    from collections import deque

    from openbb_federal_reserve.utils.ffiec import fetch_relationships

    adjacency: dict[str, set[str]] = {}
    for record in fetch_relationships():
        if (
            record.get("CTRL_IND") == "1"
            and record.get("DT_END") in (None, "", "99991231")
            and record.get("ID_RSSD_OFFSPRING")
        ):
            adjacency.setdefault(record["#ID_RSSD_PARENT"], set()).add(
                record["ID_RSSD_OFFSPRING"]
            )

    seen: set[str] = set()
    queue = deque([str(parent_rssd)])
    while queue:
        node = queue.popleft()
        for child in adjacency.get(node, ()):
            if child not in seen:
                seen.add(child)
                queue.append(child)
    return seen


def lead_subsidiary_bank(
    holding_rssd: str, filers: set[str], period: str | None
) -> str | None:
    """Resolve a holding company to the largest subsidiary bank that files."""
    holding_rssd = str(holding_rssd)
    if holding_rssd in filers:
        return holding_rssd
    candidates = controlled_subtree(holding_rssd) & filers
    if not candidates:
        return None
    if len(candidates) == 1:
        return next(iter(candidates))

    from openbb_federal_reserve.utils.cdr import total_assets_by_rssd

    assets = total_assets_by_rssd(period, candidates)
    return max(sorted(candidates, key=int), key=lambda rssd: assets.get(rssd) or 0.0)


def resolve_ticker_to_bank(
    ticker: str, filers: set[str], period: str | None = None
) -> str | None:
    """Resolve a ticker to the subsidiary bank RSSD present in ``filers``."""
    holding = resolve_ticker_to_rssd(ticker)
    if not holding:
        return None
    return lead_subsidiary_bank(holding, filers, period)


def call_report_filers() -> set[str]:
    """Return the RSSDs that file the latest single-period Call Report."""
    from openbb_federal_reserve.utils.cdr import bulk_rssids, fetch_bulk

    latest = fetch_bulk("call_single", None, fmt="xbrl")
    if latest[:2] != b"PK":
        return set()
    return bulk_rssids(latest)


def resolve_rssd_to_bank(rssd_id: str) -> tuple[str, str | None]:
    """Resolve an RSSD to its lead filing bank and that bank's name.

    A holding-company RSSD carries no bank-level (Call Report / UBPR) report; it
    is resolved to the largest controlled bank that files via
    :func:`lead_subsidiary_bank`. When the supplied RSSD already files, it is
    returned unchanged. The returned name is the resolved bank's NIC name when
    the resolution changed the RSSD (so the substitution is not silent), else
    ``None``.

    Returns
    -------
    tuple[str, str | None]
        The resolved bank RSSD and its name (``None`` when unchanged or unknown).
    """
    rssd_id = str(rssd_id)
    resolved = lead_subsidiary_bank(rssd_id, call_report_filers(), None) or rssd_id
    if resolved == rssd_id:
        return resolved, None
    from openbb_federal_reserve.utils.ffiec import rssd_names

    return resolved, rssd_names().get(resolved)
