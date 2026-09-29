"""FFIEC CDR client for the UBPR Peer Group Average Report."""

from __future__ import annotations

import html as _html
import json
import re
from typing import Any

_BASE = "https://cdr.ffiec.gov/Public/Reports/UbprReport.aspx"
_REPORT_TYPE_ID = 284
_TOC = re.compile(
    r"__doPostBack\(&#39;(rptTOC\$rptTOC\$ctl\d+\$lbItem)&#39;,&#39;&#39;\)\">([^<]+)</a>"
)
_ROW = re.compile(r"<tr>(.*?)</tr>", re.DOTALL)
_LABEL = re.compile(r'<td class="UbprReportDataRow"[^>]*>(.*?)</td>', re.DOTALL)
_GRAPH = re.compile(r'data-graph_set="([^"]*)"')
_CONCEPT = re.compile(r'"conceptname":"([^"]*)"')
_DESCRIPTOR_GRAPH = re.compile(r'data-graph_descriptor="([^"]*)"')
_DESCRIPTOR = re.compile(r'data-report_descriptor="([^"]+)"')
_HEADER = re.compile(r'id="headerTable".*?</table>', re.DOTALL)
_CELL = re.compile(r"<td[^>]*>(.*?)</td>", re.DOTALL)
_DATE = re.compile(r"^\d{1,2}/\d{1,2}/\d{4}$")


def _field(text: str, name: str) -> str:
    """Read an ASP.NET hidden form field's value from the page."""
    match = re.search(rf'name="{name}"[^>]*value="([^"]*)"', text)
    return match.group(1) if match else ""


def _iso(date: str) -> str:
    """Convert an ``M/D/YYYY`` cell date to an ISO ``YYYY-MM-DD`` string."""
    month, day, year = date.split("/")
    return f"{year}-{int(month):02d}-{int(day):02d}"


def _date_key(date: str) -> tuple[int, int, int]:
    """Return a sortable ``(year, month, day)`` tuple for a cell date."""
    month, day, year = date.split("/")
    return int(year), int(month), int(day)


_NBSP = "\u00a0"


def _caption(raw: str) -> str:
    """Guard a row's leading indentation with a ``>`` for the workspace grid."""
    body = raw.lstrip(" " + _NBSP)
    indent = len(raw) - len(body)
    return (">" + _NBSP * indent + body) if indent else body


def _value(token: Any) -> float | None:
    """Parse a graph value to a float, mapping any non-numeric token to ``None``.

    The FFIEC prints ``"##"`` for a peer-group value computed from fewer than five
    observations and may print ``"--"``, ``"NA"``, ``"N/A"``, ``"null"`` or a blank
    for a missing value; each maps to ``None`` rather than raising.

    Parameters
    ----------
    token : Any
        The raw graph value.

    Returns
    -------
    float or None
        The parsed value, or ``None`` when the token is not numeric.
    """
    try:
        return float(token)
    except (TypeError, ValueError):
        return None


def resolve_peer_group_id(peer_group: str) -> int:
    """Resolve a peer-group name to the report URL's ``peergroupid``."""
    from openbb_federal_reserve.utils.peer_groups import (
        resolve_peer_group_id as _resolve,
    )
    from openbb_federal_reserve.utils.ubpr_report import report_cycles

    cycles = report_cycles()
    cycle_id = cycles[0]["reportingcycleid"] if cycles else None
    return _resolve(peer_group, cycle_id=cycle_id)


def _toc(page: str) -> dict[str, str]:
    """Map each report section title to its TOC postback control target."""
    return {
        _html.unescape(title).strip(): target for target, title in _TOC.findall(page)
    }


def _peer_group_description(page: str) -> str | None:
    """Extract the peer group description from the rendered report header."""
    block = _HEADER.search(page)
    if not block:
        return None
    for cell in _CELL.findall(block.group(0)):
        text = _html.unescape(re.sub(r"<[^>]+>", "", cell)).strip()
        if "bank" in text.lower() and (
            "$" in text or "assets" in text.lower() or "institution" in text.lower()
        ):
            return text
    return None


def _parse_rows(page: str) -> list[tuple[str, str | None, dict[str, float | None]]]:
    """Parse each report line into its label, concept code, and value series."""
    rows: list[tuple[str, str | None, dict[str, float | None]]] = []
    for match in _ROW.finditer(page):
        row = match.group(1)
        label_match = _LABEL.search(row)
        if not label_match:
            continue
        label = _html.unescape(re.sub(r"<[^>]+>", "", label_match.group(1)))
        descriptor_match = _DESCRIPTOR_GRAPH.search(row)
        code_match = (
            _CONCEPT.search(_html.unescape(descriptor_match.group(1)))
            if descriptor_match
            else None
        )
        code = code_match.group(1) if code_match else None
        graph_match = _GRAPH.search(row)
        series: dict[str, float | None] = {}
        if graph_match and graph_match.group(1):
            for point in json.loads(_html.unescape(graph_match.group(1))):
                series[point["category"]] = _value(point.get("value"))
        rows.append((label, code, series))
    return rows


def report_sections(peergroupid: int) -> list[str]:
    """Return the report's section titles, excluding the cover page."""
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release
    from openbb_federal_reserve.utils.cdr import _get_session
    from openbb_federal_reserve.utils.ubpr_report import report_cycles

    def _producer() -> list[str]:
        """Fetch the report shell and read its table of contents."""
        cycle_id = report_cycles()[0]["reportingcycleid"]
        url = (
            f"{_BASE}?rptCycleIds={cycle_id}&rptid={_REPORT_TYPE_ID}"
            f"&peergroupid={peergroupid}&isTest=False"
        )
        page = _get_session().get(url, timeout=90).text
        return [title for title in _toc(page) if title.lower() != "cover page"]

    return cached(
        ("pga_sections", peergroupid),
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )


_MAX_CYCLES_PER_REQUEST = 5


def _fetch_section_batch(
    peergroupid: int, section: str, cycle_ids: str
) -> dict[str, Any]:
    """Render and parse one section for a single batch of reporting cycles."""
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release
    from openbb_federal_reserve.utils.cdr import _get_session

    def _producer() -> dict[str, Any]:
        """Render the section via the TOC postback and parse its grid."""
        session = _get_session()
        url = (
            f"{_BASE}?rptCycleIds={cycle_ids}&rptid={_REPORT_TYPE_ID}"
            f"&peergroupid={peergroupid}&isTest=False"
        )
        shell = session.get(url, timeout=90).text
        toc = _toc(shell)
        target = next(
            (
                control
                for title, control in toc.items()
                if title.lower() == section.strip().lower()
            ),
            None,
        )
        if not target:
            raise ValueError(
                f"Unknown report section '{section}'. Available: "
                f"{', '.join(t for t in toc if t.lower() != 'cover page')}."
            )
        form = {
            "__EVENTTARGET": target,
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": _field(shell, "__VIEWSTATE"),
            "__VIEWSTATEGENERATOR": _field(shell, "__VIEWSTATEGENERATOR"),
        }
        page = session.post(url, data=form, timeout=120).text
        descriptor_match = _DESCRIPTOR.search(page)
        descriptor = (
            json.loads(_html.unescape(descriptor_match.group(1)))
            if descriptor_match
            else {}
        )
        return {
            "title": descriptor.get("PageNumber") or section,
            "peer_group": _peer_group_description(page),
            "parsed": _parse_rows(page),
        }

    return cached(
        ("pga_lines", peergroupid, section.lower(), cycle_ids),
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )


def _merge_batches(
    batches: list[dict[str, Any]],
) -> tuple[str, str | None, list[tuple[str, str | None, dict[str, float | None]]]]:
    """Merge per-batch parsed rows into one line list with a combined series."""
    title = batches[0]["title"]
    peer_group = batches[0]["peer_group"]
    order: list[tuple[str, str | None]] = []
    merged: dict[tuple[str, str | None], dict[str, float | None]] = {}
    for batch in batches:
        for label, code, series in batch["parsed"]:
            key = (label, code)
            if key not in merged:
                merged[key] = {}
                order.append(key)
            merged[key].update(series)
    parsed = [(label, code, merged[(label, code)]) for label, code in order]
    return title, peer_group, parsed


def fetch_peer_group_section(
    peergroupid: int,
    section: str,
    *,
    periods: int = 5,
    all_periods: bool = False,
) -> dict[str, Any]:
    """Fetch one peer group report section as wide rows across recent periods.

    Returns ``{section, peer_group, rows}`` where each row is ``{label,
    is_header, <ISO date>}`` carrying the peer group average for that period.

    Parameters
    ----------
    peergroupid : int
        The report URL's internal peer group id.
    section : str
        The report section (page) title to render.
    periods : int, default 5
        The number of recent reporting cycles to include when not requesting
        every period.
    all_periods : bool, default False
        When True, include every reporting cycle the report supports instead of
        only the most recent ``periods``. The source renders at most five cycles
        per request, so the full history is fetched in five-cycle batches and
        merged.
    """
    from openbb_federal_reserve.utils.concepts import (
        clean_name,
        concept_index,
        indented_name,
    )
    from openbb_federal_reserve.utils.guide import fetch_guide_concepts
    from openbb_federal_reserve.utils.ubpr_report import rectangularize, report_cycles

    cap = None if all_periods else periods
    cycles = report_cycles()[:cap]
    cycle_id_list = [cycle["reportingcycleid"] for cycle in cycles]
    batch_ids = [
        ",".join(cycle_id_list[start : start + _MAX_CYCLES_PER_REQUEST])
        for start in range(0, len(cycle_id_list), _MAX_CYCLES_PER_REQUEST)
    ]
    batches = [
        _fetch_section_batch(peergroupid, section, cycle_ids) for cycle_ids in batch_ids
    ]
    title, peer_group, parsed = _merge_batches(batches)

    period_cols: list[str] = []
    seen: set[str] = set()
    for _, _, series in parsed:
        for col in sorted(series, key=_date_key, reverse=True):
            if col not in seen:
                seen.add(col)
                period_cols.append(col)
    period_cols = sorted(period_cols, key=_date_key, reverse=True)[:cap]
    iso = {col: _iso(col) for col in period_cols}
    index = concept_index("ubpr_ratio_single")
    guide = fetch_guide_concepts(
        list({code for _, code, _ in parsed if code}),
    )

    rows: list[dict[str, Any]] = []
    for label, code, series in parsed:
        if not label.strip():
            continue
        is_header = not series or all(series.get(col) is None for col in period_cols)
        caption = _caption(label)
        if is_header:
            rows.append({"label": caption, "is_header": True, "narrative": None})
            continue
        meta = index.get(code or "", {})
        monetary = bool(meta.get("monetary"))
        guide_concept = guide.get(code or "", {})
        label_name = clean_name(guide_concept.get("description")) or meta.get("name")
        record: dict[str, Any] = {
            "label": indented_name(caption, label_name),
            "is_header": False,
            "narrative": guide_concept.get("narrative") or meta.get("narrative"),
        }
        for col in period_cols:
            value = series.get(col)
            scale = 1000 if monetary else 1
            record[iso[col]] = value * scale if value is not None else None
        rows.append(record)

    from openbb_federal_reserve.utils.ubpr_pages import UBPR_PAGE_DESCRIPTIONS

    rectangular = rectangularize(rows)
    for row in rectangular:
        if row.get("is_header") and all(
            row.get(iso[col]) is None for col in period_cols
        ):
            row["narrative"] = UBPR_PAGE_DESCRIPTIONS.get(section)
            break

    return {
        "section": title,
        "peer_group": peer_group,
        "rows": rectangular,
    }
