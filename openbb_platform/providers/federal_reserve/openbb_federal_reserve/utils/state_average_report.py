"""FFIEC CDR report-router client for the UBPR State Average report."""

from __future__ import annotations

import html as _html
import re
from typing import Any

_ROOT = "https://cdr.ffiec.gov/Public/Reports/UbprReport.aspx"
_REPORT_TYPE_ID = 286
_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "*/*",
    "Referer": "https://cdr.ffiec.gov/Public/Reports/UbprReport.html",
}
_DATE = re.compile(r"^\d{1,2}/\d{1,2}/\d{4}$")
_MAX_COLUMNS = 5

_STATES: dict[str, tuple[int, str]] = {
    "AL": (236, "Alabama"),
    "AK": (237, "Alaska"),
    "AS": (238, "American Samoa"),
    "AZ": (239, "Arizona"),
    "AR": (240, "Arkansas"),
    "CA": (241, "California"),
    "CO": (242, "Colorado"),
    "CT": (243, "Connecticut"),
    "DE": (244, "Delaware"),
    "DC": (245, "District of Columbia"),
    "FL": (246, "Florida"),
    "GA": (247, "Georgia"),
    "GU": (248, "Guam"),
    "HI": (249, "Hawaii"),
    "ID": (250, "Idaho"),
    "IL": (251, "Illinois"),
    "IN": (252, "Indiana"),
    "IA": (253, "Iowa"),
    "KS": (254, "Kansas"),
    "KY": (255, "Kentucky"),
    "LA": (256, "Louisiana"),
    "ME": (257, "Maine"),
    "MD": (258, "Maryland"),
    "MA": (259, "Massachusetts"),
    "MI": (260, "Michigan"),
    "FM": (261, "Micronesia"),
    "MN": (262, "Minnesota"),
    "MS": (263, "Mississippi"),
    "MO": (264, "Missouri"),
    "MT": (265, "Montana"),
    "NE": (266, "Nebraska"),
    "NV": (267, "Nevada"),
    "NH": (268, "New Hampshire"),
    "NJ": (269, "New Jersey"),
    "NM": (270, "New Mexico"),
    "NY": (271, "New York"),
    "NC": (272, "North Carolina"),
    "ND": (273, "North Dakota"),
    "OH": (274, "Ohio"),
    "OK": (275, "Oklahoma"),
    "OR": (276, "Oregon"),
    "PA": (277, "Pennsylvania"),
    "PR": (278, "Puerto Rico"),
    "RI": (279, "Rhode Island"),
    "SC": (280, "South Carolina"),
    "SD": (281, "South Dakota"),
    "TN": (282, "Tennessee"),
    "TX": (283, "Texas"),
    "UT": (284, "Utah"),
    "VT": (285, "Vermont"),
    "VI": (286, "Virgin Islands"),
    "VA": (287, "Virginia"),
    "WA": (288, "Washington"),
    "WV": (289, "West Virginia"),
    "WI": (290, "Wisconsin"),
    "WY": (291, "Wyoming"),
}
STATE_OPTIONS = [{"label": name, "value": code} for code, (_, name) in _STATES.items()]
GROUP_TYPES = ["commercial", "savings"]
_GROUP_SUFFIX = {"commercial": "COM", "savings": "SVG"}


def peer_group_id(state: str, group_type: str = "commercial") -> int:
    """Resolve a state code and group type to its State Average peer-group id."""
    from openbb_federal_reserve.utils.peer_groups import (
        resolve_peer_group_id as _resolve,
    )
    from openbb_federal_reserve.utils.ubpr_report import report_cycles

    code = (state or "").strip().upper()
    if code not in _STATES:
        raise ValueError(f"Unknown state '{state}'.")
    name = f"{code}{_GROUP_SUFFIX[group_type]}"
    cycles = report_cycles()
    cycle_id = cycles[0]["reportingcycleid"] if cycles else None
    return _resolve(name, cycle_id=cycle_id)


def state_name(state: str) -> str:
    """Return the full state name for a state code."""
    return _STATES[(state or "").strip().upper()][1]


def report_sections() -> list[dict[str, str]]:
    """Return the State Average report's section table of contents."""
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release
    from openbb_federal_reserve.utils.ubpr_report import _post

    def _producer() -> list[dict[str, str]]:
        """Fetch the page list for the State Average report type."""
        return [
            {"pageid": row["pageid"], "pagetitle": row["pagetitle"]}
            for row in _post("UbprReportPagesList", {"ReportTypeID": _REPORT_TYPE_ID})
            if isinstance(row, dict) and row.get("pageid")
        ]

    return cached(
        ("state_average_sections", _REPORT_TYPE_ID),
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )


def _field(html: str, name: str) -> str:
    """Extract an ASP.NET hidden-field value from the report page."""
    match = re.search(rf'id="{name}"[^>]*value="([^"]*)"', html)
    return match.group(1) if match else ""


def _toc_targets(html: str) -> dict[str, str]:
    """Map each table-of-contents section title to its postback target."""
    targets: dict[str, str] = {}
    for target, label in re.findall(
        r"__doPostBack\(&#39;(rptTOC\$rptTOC\$ctl\d+\$lbItem)&#39;[^>]*>([^<]+)</a>",
        html,
    ):
        targets.setdefault(label.strip(), target)
    return targets


def _caption(raw: str) -> str:
    """Guard a line item's leading indentation with a ``>`` for the workspace."""
    body = raw.lstrip(" ")
    indent = len(raw) - len(body)
    return (">" + " " * indent + body) if indent else body


def _number(text: str) -> float | None:
    """Parse a grid value, dropping thousands separators; blanks are ``None``."""
    token = text.replace(",", "").strip()
    try:
        return float(token)
    except (TypeError, ValueError):
        return None


def _concept_code(block: str) -> str | None:
    """Extract a row's concept code from its cell ``graph_descriptor`` payload."""
    match = re.search(r'data-graph_descriptor="([^"]*)"', block)
    if not match:
        return None
    name = re.search(r"&quot;conceptname&quot;:&quot;([^&]*)&quot;", match.group(1))
    return name.group(1).strip() or None if name else None


def _parse_grid(html: str) -> tuple[list[str], list[dict[str, Any]]]:
    """Parse the rendered report grid into period dates and line-item rows."""
    anchor = html.find("UbprReportDateRow")
    if anchor < 0:
        return [], []
    grid = html[anchor - 400 :].split("<script", maxsplit=1)[0]
    dates: list[str] = []
    rows: list[dict[str, Any]] = []
    for block in re.findall(r"<tr>(.*?)</tr>", grid, re.DOTALL):
        code = _concept_code(block)
        stripped = re.sub(r'\sdata-[\w-]+="[^"]*"', "", block)
        cells = [
            re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", "", cell))).rstrip()
            for cell in re.findall(r"<td[^>]*>(.*?)</td>", stripped, re.DOTALL)
        ]
        cells = [cell.replace("\xa0", " ") for cell in cells]
        present = [cell for cell in cells if cell.strip()]
        if not present:
            continue
        if not dates and _DATE.match(present[0]):
            dates = [_iso(date) for date in present]
            continue
        label = cells[0].rstrip()
        values = [cell for cell in cells[1:] if cell.strip()]
        rows.append({"label": label, "values": values, "concept": code})
    return dates, rows


def _iso(date: str) -> str:
    """Convert an ``M/D/YYYY`` grid date to an ISO ``YYYY-MM-DD`` string."""
    month, day, year = date.split("/")
    return f"{year}-{int(month):02d}-{int(day):02d}"


def fetch_state_average_section(
    state: str,
    section: str = "Summary Ratios",
    *,
    group_type: str = "commercial",
    periods: int = 5,
    all_periods: bool = False,
) -> dict[str, Any]:
    """Fetch one State Average report section as wide rows across recent periods."""
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release
    from openbb_federal_reserve.utils.cdr import _get_session
    from openbb_federal_reserve.utils.concepts import (
        clean_name,
        concept_index,
        indented_name,
    )
    from openbb_federal_reserve.utils.guide import fetch_guide_concepts
    from openbb_federal_reserve.utils.ubpr_pages import UBPR_PAGE_DESCRIPTIONS
    from openbb_federal_reserve.utils.ubpr_report import rectangularize, report_cycles

    sections = report_sections()
    titles = {row["pagetitle"] for row in sections}
    if section not in titles:
        raise ValueError(f"Unknown report section '{section}'.")
    pg_id = peer_group_id(state, group_type)
    all_cycles = report_cycles()
    windows = (
        [
            all_cycles[start : start + _MAX_COLUMNS]
            for start in range(0, len(all_cycles), _MAX_COLUMNS)
        ]
        if all_periods
        else [all_cycles[:periods]]
    )

    def _producer_for(cycle_ids: str):
        """Build a cached producer for one cycle window."""

        def _producer() -> dict[str, Any]:
            """Run the report postback and parse the section grid."""
            session = _get_session()
            url = (
                f"{_ROOT}?rptCycleIds={cycle_ids}"
                f"&rptid={_REPORT_TYPE_ID}&peergroupid={pg_id}&isTest=False"
            )
            page = session.get(url, timeout=90).text
            target = _toc_targets(page).get(section)
            if not target:
                return {"dates": [], "rows": []}
            form = {
                "__EVENTTARGET": target,
                "__EVENTARGUMENT": "",
                "__VIEWSTATE": _field(page, "__VIEWSTATE"),
                "__VIEWSTATEGENERATOR": _field(page, "__VIEWSTATEGENERATOR"),
            }
            rendered = session.post(url, data=form, headers=_HEADERS, timeout=120).text
            dates, raw_rows = _parse_grid(rendered)
            return {"dates": dates, "rows": raw_rows}

        return cached(
            ("state_average_lines", pg_id, section, cycle_ids),
            lambda: seconds_until_next_release("quarterly"),
            _producer,
        )

    by_label: dict[str, dict[str, Any]] = {}
    index = concept_index("ubpr_ratio_single")
    rows: list[dict[str, Any]] = []
    parsed_windows = []
    for window in windows:
        cycle_ids = ",".join(c["reportingcycleid"] for c in window)
        parsed = _producer_for(cycle_ids)
        parsed_windows.append((parsed, parsed["dates"]))
    concepts = {
        line["concept"]
        for parsed, _dates in parsed_windows
        for line in parsed["rows"]
        if line.get("values") and line.get("concept")
    }
    guide = fetch_guide_concepts(list(concepts))
    for parsed, dates in parsed_windows:
        for line in parsed["rows"]:
            values = line["values"]
            is_header = not values
            caption = _caption(line["label"])
            code = line.get("concept") or ""
            meta = index.get(code, {})
            g = guide.get(code, {})
            label_name = clean_name(g.get("description")) or meta.get("name")
            label = str(caption if is_header else indented_name(caption, label_name))
            record: dict[str, Any] | None = by_label.get(label)
            if record is None:
                record = {
                    "label": label,
                    "is_header": is_header,
                    "narrative": None
                    if is_header
                    else (g.get("narrative") or meta.get("narrative")),
                }
                by_label[label] = record
                rows.append(record)
            if not is_header:
                scale = 1000 if meta.get("monetary") else 1
                for position, date in enumerate(dates):
                    value = (
                        _number(values[position]) if position < len(values) else None
                    )
                    record[date] = value * scale if value is not None else None
    for row in rows:
        if row.get("is_header") and not any(
            key not in ("label", "is_header", "narrative") and row.get(key) is not None
            for key in row
        ):
            row["narrative"] = UBPR_PAGE_DESCRIPTIONS.get(section)
            break
    return {
        "section": section,
        "state": state_name(state),
        "rows": rectangularize(rows),
    }
