"""FFIEC CDR client for the UBPR Peer Group Average Distribution report.

Fetches the percentile distribution of a UBPR ratio page across every bank in a
peer group from the ``UbprReport.aspx`` WebForms report (report type 285). The
public router exposes the page list, but the grid itself is an ASP.NET postback:
load the report shell for its view state, then post back the page's table-of-
contents link to render the distribution table (1st .. 99th percentiles and the
trimmed average) for the selected reporting period.
"""

from __future__ import annotations

import re
from typing import Any

from openbb_federal_reserve.utils.ubpr_pages import UBPR_PAGE_DESCRIPTIONS

_RPTID = 285
_URL = "https://cdr.ffiec.gov/Public/Reports/UbprReport.aspx"
_HEADERS = {"Referer": "https://cdr.ffiec.gov/Public/Reports/UbprReport.html"}

PERCENTILE_COLUMNS = [
    "1ST",
    "5TH",
    "10TH",
    "20TH",
    "25TH",
    "50TH",
    "75TH",
    "80TH",
    "90TH",
    "95TH",
    "99TH",
    "TRIMMED AVERAGE",
]

PEER_GROUP_COLUMN = "PEER GROUP"

_MEMO_CONCEPTS: dict[str, str] = {
    "Average Total Assets": "UBPRD659",
    "Net Income": "UBPR4340",
}

_CELL = re.compile(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", re.DOTALL)
_ROW = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.DOTALL)
_TAG = re.compile(r"<[^>]+>")
_PERIOD = re.compile(r"^\d\d_\d\d_\d{4}$")
_MAP_RSSD = "112837"
_NBSP = " "


def _field(html: str, name: str) -> str:
    """Read an ASP.NET hidden form field value from the report shell."""
    match = re.search(rf'id="{name}"[^>]*value="([^"]*)"', html)
    return match.group(1) if match else ""


def _text(cell: str) -> str:
    """Strip tags and normalise the entities/whitespace of a grid cell."""
    body = _TAG.sub("", cell)
    body = (
        body.replace("&nbsp;", _NBSP)
        .replace("&amp;", "&")
        .replace("&#39;", "'")
        .replace("&quot;", '"')
    )
    return body.replace("\r", " ").replace("\n", " ").strip(" \t")


def _toc(html: str) -> list[tuple[str, str]]:
    """Return the report's table-of-contents as ``(postback target, title)``."""
    out: list[tuple[str, str]] = []
    pattern = re.compile(
        r"__doPostBack\(&#39;(rptTOC\$rptTOC\$ctl\d+\$lbItem)&#39;[^>]*>([^<]*)</a>"
    )
    for match in pattern.finditer(html):
        out.append((match.group(1), _text(match.group(2))))
    return out


def _caption(label: str) -> str:
    """Guard a line item's indentation with a leading ``>`` for the workspace."""
    body = label.lstrip(_NBSP + " ")
    indent = len(label) - len(label.lstrip(_NBSP + " "))
    return (">" + _NBSP * indent + body) if indent else body


def _number(text: str) -> float | None:
    """Parse a grid value, mapping ``N/A`` and blanks to ``None``."""
    cleaned = text.replace(",", "").strip(_NBSP + " ")
    try:
        return float(cleaned)
    except (TypeError, ValueError):
        return None


def _concept_map(section: str, cycle_ids: str) -> dict[str, str]:
    """Map a section's trimmed line captions to their UBPR concept codes.

    The distribution report (rptid 285) renders only abbreviated captions, so the
    concept code is recovered from the single-bank UBPR report (rptid 283), whose
    ``MyUbprLinesData`` payload carries both the same captions and the code. The
    first occurrence of a caption wins, which resolves the rare captions the report
    repeats verbatim under different sub-headers.
    """
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release
    from openbb_federal_reserve.utils.ubpr_report import (
        _concept_code,
        _post,
        _section_id,
    )

    def _producer() -> dict[str, str]:
        """Fetch the single-bank section and key each caption to its code."""
        page_id, _ = _section_id(section, 283)
        raw = _post(
            "MyUbprLinesData",
            {
                "ID_RSSD": _MAP_RSSD,
                "ScheduleID": page_id,
                "ReportingCycleIdList": cycle_ids,
                "PeerDefinition": "",
            },
        )
        mapping: dict[str, str] = {}
        for line in raw if isinstance(raw, list) else []:
            caption = str(line.get("linecaption", ""))
            if caption.startswith("#"):
                continue
            code: str | None = None
            for key in (k for k in line if _PERIOD.match(k)):
                code = _concept_code(line.get(key))
                if code:
                    break
            text = caption.strip()
            if code and text not in mapping:
                mapping[text] = code
        return mapping

    return cached(
        ("ubpr_pg_distribution_codes", section, cycle_ids),
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )


def _row_concept(row: dict[str, Any], codes: dict[str, str]) -> str:
    """Resolve a row's concept code from its trimmed caption.

    Memo footer rows (those carrying a ``PEER GROUP`` aggregate) resolve via the
    pinned :data:`_MEMO_CONCEPTS` so their dollar concept is not shadowed by the
    same-captioned distributed ratio line; all other rows resolve via the
    caption-to-code map.
    """
    text = re.sub(rf">?[\s{_NBSP}]*", "", str(row["label"]), count=1)
    if PEER_GROUP_COLUMN in row and text in _MEMO_CONCEPTS:
        return _MEMO_CONCEPTS[text]
    return codes.get(text, "")


def _enrich(
    rows: list[dict[str, Any]], codes: dict[str, str], index: dict[str, Any]
) -> list[dict[str, Any]]:
    """Add full names, guide narratives, and dollar scaling to the parsed rows."""
    from openbb_federal_reserve.utils.concepts import clean_name, indented_name
    from openbb_federal_reserve.utils.guide import fetch_guide_concepts

    concepts = {_row_concept(row, codes) for row in rows if not row.get("is_header")}
    guide = fetch_guide_concepts(sorted(c for c in concepts if c))
    for row in rows:
        if row.get("is_header"):
            row["narrative"] = None
            continue
        code = _row_concept(row, codes)
        meta = index.get(code, {})
        g = guide.get(code or "", {})
        label_name = clean_name(g.get("description")) or meta.get("name")
        row["label"] = indented_name(row["label"], label_name)
        row["narrative"] = g.get("narrative") or meta.get("narrative")
        if meta.get("monetary"):
            for column in (*PERCENTILE_COLUMNS, PEER_GROUP_COLUMN):
                value = row.get(column)
                if value is not None:
                    row[column] = value * 1000
    return rows


def _set_page_narrative(rows: list[dict[str, Any]], section: str) -> None:
    """Set the leading header row's narrative to the section's page description.

    The first row of a rendered page is a section header carrying no period
    values; its hover card shows the FFIEC "Summary of UBPR Page Content"
    description for the page when one is mapped, leaving line-item narratives
    untouched.
    """
    if not rows:
        return
    head = rows[0]
    has_values = any(
        head.get(name) is not None for name in (*PERCENTILE_COLUMNS, PEER_GROUP_COLUMN)
    )
    if head.get("is_header") and not has_values:
        head["narrative"] = UBPR_PAGE_DESCRIPTIONS.get(section)


def _grid(html: str) -> list[dict[str, Any]]:
    """Parse the rendered distribution table into wide percentile rows.

    The memo footer rows (peer-group average assets, net income, and bank count)
    render their single peer-group aggregate in the first data column; they are
    keyed to a ``PEER GROUP`` column instead of misreading the value as the 1st
    percentile.
    """
    match = re.search(
        r'<table[^>]*id="tableReportData"[^>]*>(.*?)</table>', html, re.DOTALL
    )
    if not match:
        return []
    rows = [[_text(c) for c in _CELL.findall(r)] for r in _ROW.findall(match.group(1))]
    rows = [r for r in rows if r]
    if not rows:
        return []

    header = rows[0]
    columns = {
        name: index for index, name in enumerate(header) if name in PERCENTILE_COLUMNS
    }
    records: list[dict[str, Any]] = []
    for cells in rows[1:]:
        label = cells[0] if cells else ""
        if not label.strip(_NBSP + " "):
            continue
        values = {
            name: _number(cells[index])
            for name, index in columns.items()
            if index < len(cells)
        }
        is_header = all(value is None for value in values.values())
        populated = [name for name, value in values.items() if value is not None]
        record: dict[str, Any] = {
            "label": _caption(label),
            "is_header": is_header,
        }
        if populated == ["1ST"]:
            record[PEER_GROUP_COLUMN] = values["1ST"]
        elif not is_header:
            record.update(values)
        records.append(record)
    return records


def fetch_distribution(
    peer_group: str,
    section: str = "Summary Ratios",
    *,
    cycle_id: str | None = None,
) -> dict[str, Any]:
    """Fetch one page of the peer-group distribution for a reporting period.

    Parameters
    ----------
    peer_group : str
        A peer-group name (e.g. ``"1"``, ``"NATIONAL"``, ``"ALCOM"``).
    section : str
        The report page (table-of-contents title) to render.
    cycle_id : str | None
        The reporting-cycle id (newest first) to report; defaults to the latest.

    Returns
    -------
    dict
        ``{"section", "period", "peer_group", "rows"}`` where each row is
        ``{"label", "is_header", <percentile cols>}``.
    """
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release
    from openbb_federal_reserve.utils.cdr import _get_session
    from openbb_federal_reserve.utils.concepts import concept_index
    from openbb_federal_reserve.utils.peer_groups import (
        STATIC_PEER_GROUPS,
        resolve_peer_group_id,
    )
    from openbb_federal_reserve.utils.ubpr_report import rectangularize, report_cycles

    key = (peer_group or "").strip().upper()
    if key not in STATIC_PEER_GROUPS:
        raise ValueError(f"Unknown peer group '{peer_group}'.")

    cycles = report_cycles()
    if not cycles:
        raise ValueError("The reporting-cycle list could not be retrieved.")
    target = next(
        (c for c in cycles if c["reportingcycleid"] == str(cycle_id)),
        cycles[0],
    )
    peergroupid = resolve_peer_group_id(key, cycle_id=target["reportingcycleid"])
    ordered = [target] + [c for c in cycles if c is not target][:4]
    cycle_ids = ",".join(c["reportingcycleid"] for c in ordered)

    def _producer() -> dict[str, Any]:
        """Drive the WebForms postback and parse the distribution page."""
        session = _get_session()
        url = (
            f"{_URL}?rptCycleIds={cycle_ids}&rptid={_RPTID}"
            f"&peergroupid={peergroupid}&isTest=False"
        )
        shell = session.get(url, headers=_HEADERS, timeout=90).text
        toc = _toc(shell)
        wanted = section.strip().lower()
        target_ctl = next((ctl for ctl, title in toc if title.lower() == wanted), None)
        if target_ctl is None:
            raise ValueError(f"Unknown report section '{section}'.")
        form = {
            "__EVENTTARGET": target_ctl,
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": _field(shell, "__VIEWSTATE"),
            "__VIEWSTATEGENERATOR": _field(shell, "__VIEWSTATEGENERATOR"),
            "__EVENTVALIDATION": _field(shell, "__EVENTVALIDATION"),
        }
        rendered = session.post(url, data=form, headers=_HEADERS, timeout=120).text
        title = next((t for c, t in toc if c == target_ctl), section)
        codes = _concept_map(title, cycle_ids)
        index = concept_index("ubpr_ratio_single")
        rows = rectangularize(_enrich(_grid(rendered), codes, index))
        _set_page_narrative(rows, title)
        return {"section": title, "rows": rows}

    result = cached(
        ("ubpr_pg_distribution", peergroupid, section, cycle_ids),
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )
    month, day, year = target["enddateformatted"].split("/")
    iso = f"{year}-{month}-{day}"
    return {
        "section": result["section"],
        "period": iso,
        "peer_group": key,
        "rows": result["rows"],
    }
