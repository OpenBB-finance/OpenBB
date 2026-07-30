"""FFIEC CDR Custom Peer Group (CPG) report client."""

from __future__ import annotations

import html as _html
import json
import re
from typing import Any

from openbb_federal_reserve.utils.ubpr_pages import UBPR_PAGE_DESCRIPTIONS

_REPORT_URL = "https://cdr.ffiec.gov/Public/Reports/UbprReport.aspx"
_MANAGE_URL = "https://cdr.ffiec.gov/public/ManageFacsimiles.aspx"
_REPORT_TYPE_ID = 288

_VALUE_COL = re.compile(r"^\d{4}-\d{2}-\d{2}(?: .+)?$")

UBPR_SECTIONS = [
    "Summary Ratios",
    "Income Statement $",
    "QTR Income Statement $",
    "Noninterest Income and Expenses",
    "Asset Yields and Funding Costs",
    "Balance Sheet $",
    "Off Balance Sheet Items",
    "Derivative Instruments",
    "Derivative Analysis",
    "Balance Sheet %",
    "Allowance & Loan Mix-a",
    "Allowance & Loan Mix-b",
    "Concentrations of Credit",
    "PD, Nonacc & Rest Loans-a",
    "PD, Nonacc & Rest Loans-b",
    "Interest Rate Risk-a",
    "Interest Rate Risk-b",
    "Liquidity & Funding",
    "Liquidity & Inv Portfolio",
    "Capital Analysis-a",
    "Capital Analysis-b",
    "Capital Analysis-c",
    "Income Statement 1-Qtr-Ann",
    "Securitization & Asset Sale-a",
    "Securitization & Asset Sale-b",
    "Securitization & Asset Sale-c",
    "Fiduciary Services-a",
    "Fiduciary Services-b",
]


def _field(name: str, html: str) -> str:
    """Extract an ASP.NET hidden view-state field's value from the page."""
    match = re.search(rf'id="{name}"[^>]*value="([^"]*)"', html)
    return match.group(1) if match else ""


_NAME_ACRONYMS = {"NA", "FSB", "USA", "US", "FA", "SSB"}
_NAME_SMALL_WORDS = {"of", "and", "the", "for"}
_NAME_FIXUPS = {"Jpmorgan": "JPMorgan"}


def _bank_name(raw: str) -> str:
    """Title-case an all-caps FFIEC institution name into a readable label."""
    text = re.sub(r"\s+", " ", raw).strip()
    seen_first = [False]

    def _case(match: re.Match[str]) -> str:
        """Case one name word: acronym upper, small word lower, else capitalized."""
        word = match.group(0)
        is_first = not seen_first[0]
        seen_first[0] = True
        if word.upper() in _NAME_ACRONYMS:
            return word.upper()
        if not is_first and word.lower() in _NAME_SMALL_WORDS:
            return word.lower()
        capitalized = word[:1].upper() + word[1:].lower()
        return _NAME_FIXUPS.get(capitalized, capitalized)

    return re.sub(r"[A-Za-z]+", _case, text)


def _extract_bank_name(html: str, rssd_id: str) -> str:
    """Read the target bank's readable name from the rendered page's header table."""
    start = html.find('id="headerTable"')
    if start >= 0:
        match = re.search(r'<td[^>]*colspan="2"[^>]*>([^<]*;[^<]*)</td>', html[start:])
        if match:
            name = _html.unescape(match.group(1)).split(";")[0].strip()
            if name:
                return _bank_name(name)
    return rssd_id


def _section_index(section: str | None) -> int:
    """Resolve a section title to its table-of-contents position."""
    target = (section or UBPR_SECTIONS[0]).strip().lower()
    for index, name in enumerate(UBPR_SECTIONS):
        if name.lower() == target:
            return index
    raise ValueError(f"Unknown report section '{section}'.")


def _graph_key(date: str) -> str:
    """Normalize ``MM/DD/YYYY`` to the ``M/D/YYYY`` key used in the graph set."""
    month, day, year = date.split("/")
    return f"{int(month)}/{int(day)}/{year}"


def _label(cell: str) -> str:
    """Render a grid label cell to indented text, nbsp/markup collapsed to spaces."""
    text = _html.unescape(re.sub(r"<[^>]+>", "", cell)).replace("\u00a0", " ")
    return _caption(text.rstrip())


def _concept_code(cell: str) -> str | None:
    """Extract the line's UBPR concept code from the label cell's guide anchor."""
    match = re.search(r"[?&]Concept=([A-Za-z0-9]+)", cell)
    return match.group(1) if match else None


def _number(value: Any) -> float | None:
    """Parse a rendered grid value, mapping non-numeric tokens to ``None``.

    The FFIEC prints ``##`` for a peer-group statistic computed from fewer than
    five observations and ``--``/``NA``/``N/A``/blank for a value that is not
    reported; every such token, like ``null`` and ``None``, resolves to ``None``
    rather than raising.

    Parameters
    ----------
    value : Any
        The raw cell value from the graph set.

    Returns
    -------
    float | None
        The parsed number, or ``None`` when the token is non-numeric.
    """
    if value is None:
        return None
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def _caption(raw: str) -> str:
    """Guard a line caption indentation with a leading marker and nbsp fill."""
    body = raw.lstrip(" ")
    indent = len(raw) - len(body)
    return (">" + "\u00a0" * indent + body) if indent else body


def _set_peer_group(session: Any, peers: str, cycle_id: str) -> None:
    """Register the custom peer-group RSSD list on the CDR session."""
    from openbb_federal_reserve.utils.ubpr_report import _post

    _post("CpgSearchBanks", {"ReportingCycleID": cycle_id, "FIList": peers})
    _post(
        "SetSessionData",
        {"SessionData": peers, "SourceObject": "__UbprReportCustomIDRSSDs"},
    )


def _render_section(
    session: Any, rssd_id: str, cycle_ids: str, section_index: int
) -> str:
    """Load the report page then post back the section to render its grid."""
    url = (
        f"{_REPORT_URL}?rptid={_REPORT_TYPE_ID}&idrssd={rssd_id}"
        f"&rptCycleIds={cycle_ids}&title=Custom Peer Group&usetrimmed=0"
    )
    page = session.get(url, timeout=120).text
    target = f"rptTOC$rptTOC$ctl{section_index + 2:02d}$lbItem"
    payload = {
        "__EVENTTARGET": target,
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": _field("__VIEWSTATE", page),
        "__VIEWSTATEGENERATOR": _field("__VIEWSTATEGENERATOR", page),
        "__EVENTVALIDATION": _field("__EVENTVALIDATION", page),
    }
    return session.post(url, data=payload, timeout=120).text


def _parse_grid(
    html: str,
    period_keys: list[str],
    iso: dict[str, str],
    bank_name: str,
) -> list[dict]:
    """Parse the rendered section grid into wide bank-only rows.

    Only the ``BANK`` series of each line's ``graph_set`` carries data; the
    ``PG``/``PCT`` series the page also emits are always null for a custom peer
    group, so they are dropped. Each period contributes one ``"<ISO> <bank name>"``
    column that names the target bank.

    Parameters
    ----------
    html : str
        The rendered section grid markup.
    period_keys : list[str]
        The graph-set period keys, newest first.
    iso : dict[str, str]
        Mapping of each period key to its ISO ``YYYY-MM-DD`` date.
    bank_name : str
        The target bank's readable name, appended to each period column so the
        column names the bank.

    Returns
    -------
    list[dict]
        One row per report line item, header rows carrying only a label.
    """
    start = html.find('id="tableReportData"')
    if start < 0:
        return []
    table = html[start:]
    rows: list[dict] = []
    for block in re.split(r"<tr", table):
        label_match = re.search(
            r'class="UbprReportDataRow[^"]*"[^>]*>(.*?)</td>', block, re.DOTALL
        )
        cell = label_match.group(1) if label_match else ""
        label = _label(cell) if label_match else ""
        graph_match = re.search(r'data-graph_set="([^"]*)"', block)
        if not graph_match:
            if label:
                rows.append({"label": _caption(label), "is_header": True})
            continue
        series = json.loads(_html.unescape(graph_match.group(1)))
        by_period: dict[str, dict[str, str]] = {}
        for item in series:
            by_period.setdefault(item["category"], {})[item["name"]] = item["value"]
        record: dict[str, Any] = {
            "label": _caption(label),
            "is_header": False,
            "concept": _concept_code(cell),
        }
        has_value = False
        for key in period_keys:
            number = _number(by_period.get(key, {}).get("BANK"))
            record[f"{iso[key]} {bank_name}"] = number
            has_value = has_value or number is not None
        record["is_header"] = not has_value
        rows.append(record)
    return rows


_RENDER_CAP = 5


def _merge_batches(batches: list[list[dict]]) -> list[dict]:
    """Merge per-batch rows positionally, unioning their period columns.

    Each batch renders the same line items in the same order, so rows align by
    index; the merged row keeps the first batch's label/concept/header flag and
    accumulates every batch's ``"<ISO>"`` value columns.

    Parameters
    ----------
    batches : list[list[dict]]
        One parsed grid per period batch, newest batch first.

    Returns
    -------
    list[dict]
        The merged rows carrying the union of all batches' period columns.
    """
    if not batches:
        return []
    base = [dict(row) for row in batches[0]]
    for batch in batches[1:]:
        for index, row in enumerate(batch):
            if index >= len(base):
                base.append(dict(row))
                continue
            for key, value in row.items():
                if re.match(r"^\d{4}-\d{2}-\d{2}", key):
                    base[index][key] = value
    for row in base:
        if "concept" in row:
            row["is_header"] = not any(
                re.match(r"^\d{4}-\d{2}-\d{2}", key) and value is not None
                for key, value in row.items()
            )
    return base


def _enrich(rows: list[dict]) -> list[dict]:
    """Apply concept full names, guide narratives, and dollar scaling to rows."""
    from openbb_federal_reserve.utils.concepts import (
        clean_name,
        concept_index,
        indented_name,
    )
    from openbb_federal_reserve.utils.guide import fetch_guide_concepts

    index = concept_index("ubpr_ratio_single", None)
    concepts = {
        row["concept"]
        for row in rows
        if not row.get("is_header") and row.get("concept")
    }
    guide = fetch_guide_concepts(list(concepts))
    for row in rows:
        if row.get("is_header"):
            row["narrative"] = None
            row.pop("concept", None)
            continue
        code = row.pop("concept", None) or ""
        meta = index.get(code, {})
        g = guide.get(code or "", {})
        label_name = clean_name(g.get("description")) or meta.get("name")
        row["label"] = indented_name(row["label"], label_name)
        row["narrative"] = g.get("narrative") or meta.get("narrative")
        if meta.get("monetary"):
            for key in list(row):
                if _VALUE_COL.match(key) and isinstance(row[key], (int, float)):
                    row[key] = row[key] * 1000
    return rows


def fetch_custom_peer_group(
    rssd_id: str,
    peers: str,
    section: str | None = "Summary Ratios",
    *,
    periods: int = 5,
    all_periods: bool = False,
) -> dict[str, Any]:
    """Fetch one CPG section as wide rows across reporting periods.

    Parameters
    ----------
    rssd_id : str
        The target bank's RSSD identifier.
    peers : str
        Comma-separated RSSD identifiers forming the custom peer group.
    section : str | None
        The UBPR section (page) to render; defaults to ``Summary Ratios``.
    periods : int
        The number of most-recent reporting cycles to include.
    all_periods : bool
        When True, render every reported period rather than the most recent.

    Returns
    -------
    dict
        ``{section, rows}`` where each row is ``{label, is_header, narrative,
        "<ISO date> <bank name>": value}`` — one bank-only column per period that
        names the target bank.
    """
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release
    from openbb_federal_reserve.utils.cdr import _get_session
    from openbb_federal_reserve.utils.ubpr_report import rectangularize, report_cycles

    section_index = _section_index(section)
    cycles = report_cycles() if all_periods else report_cycles()[:periods]
    cycle_ids = ",".join(c["reportingcycleid"] for c in cycles)
    period_keys = [_graph_key(c["enddateformatted"]) for c in cycles]
    iso = {
        _graph_key(c["enddateformatted"]): (
            f"{c['enddateformatted'][6:]}-{c['enddateformatted'][:2]}-"
            f"{c['enddateformatted'][3:5]}"
        )
        for c in cycles
    }
    cleaned = ",".join(p.strip() for p in str(peers).split(",") if p.strip())

    def _producer() -> list[dict]:
        """Register the peer group then render and parse the section."""
        session = _get_session()
        session.get(_MANAGE_URL, timeout=60)
        _set_peer_group(session, cleaned, cycles[0]["reportingcycleid"])
        if not all_periods:
            html = _render_section(session, str(rssd_id), cycle_ids, section_index)
            bank_name = _extract_bank_name(html, str(rssd_id))
            return _enrich(_parse_grid(html, period_keys, iso, bank_name))
        batches: list[list[dict]] = []
        bank_name = str(rssd_id)
        for start in range(0, len(cycles), _RENDER_CAP):
            chunk = cycles[start : start + _RENDER_CAP]
            ids = ",".join(c["reportingcycleid"] for c in chunk)
            keys = [_graph_key(c["enddateformatted"]) for c in chunk]
            html = _render_section(session, str(rssd_id), ids, section_index)
            if start == 0:
                bank_name = _extract_bank_name(html, str(rssd_id))
            batches.append(_parse_grid(html, keys, iso, bank_name))
        return _enrich(_merge_batches(batches))

    rows = cached(
        (
            "cpg_lines",
            str(rssd_id),
            cleaned,
            section_index,
            cycle_ids,
            all_periods,
        ),
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )
    section_name = UBPR_SECTIONS[section_index]
    rectangular = rectangularize(rows)
    if (
        rectangular
        and rectangular[0].get("is_header")
        and not any(
            _VALUE_COL.match(key) and value is not None
            for key, value in rectangular[0].items()
        )
    ):
        rectangular[0]["narrative"] = UBPR_PAGE_DESCRIPTIONS.get(section_name)
    return {"section": section_name, "rows": rectangular}
