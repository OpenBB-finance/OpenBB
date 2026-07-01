"""FFIEC CDR report-router client for the UBPR report family.

Fetches the full UBPR report (BANK, peer-group and percentile, every period, in
the report's own section layout) from ``POST /Public/router/Search`` — the only
public source that carries the peer-group and percentile columns.
"""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

_ROUTER = "https://cdr.ffiec.gov/Public/router/Search"
_HEADERS = {
    "Content-Type": "application/json;charset=UTF-8",
    "Accept": "*/*",
    "Referer": "https://cdr.ffiec.gov/Public/Reports/UbprReport.html",
}
_PERIOD = re.compile(r"^\d\d_\d\d_\d{4}$")


def no_bank_report_error(rssd_id: str, report: str):
    """Build the error for a report requested on a non-bank RSSD.

    Parameters
    ----------
    rssd_id : str
        The RSSD identifier that carries no Call-Report-derived data.
    report : str
        The report name, used verbatim in the message (for example, ``"UBPR"``).

    Returns
    -------
    OpenBBError
        An actionable error explaining that the report only covers institutions
        that file the FFIEC Call Report.
    """
    from openbb_core.app.model.abstract.error import OpenBBError

    return OpenBBError(
        f"No {report} data for RSSD {rssd_id}. {report} covers institutions that"
        " file the FFIEC Call Report (commercial banks and savings institutions);"
        " bank holding companies and non-bank entities have none. Supply a"
        " subsidiary bank's RSSD, or use FR Y-9C (financial_statements) for a"
        " holding company."
    )


def _post(requestor_id: str, criteria: dict[str, Any]) -> Any:
    """POST a router request and return the parsed JSON body."""
    from openbb_federal_reserve.utils.cdr import _get_session

    body = json.dumps({"RequestorID": requestor_id, "Criteria": criteria})
    response = _get_session().post(_ROUTER, data=body, headers=_HEADERS, timeout=90)
    return response.json()


def report_cycles() -> list[dict[str, str]]:
    """Return the reporting cycles, newest first, as id/date records."""
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> list[dict[str, str]]:
        """Fetch and sort the reporting-cycle list newest first."""
        from datetime import datetime

        rows = [
            row
            for row in _post("PeriodsEndDateList", {})
            if isinstance(row, dict) and row.get("reportingcycleid")
        ]
        rows.sort(
            key=lambda row: datetime.strptime(row["enddateformatted"], "%m/%d/%Y"),
            reverse=True,
        )
        return rows

    return cached(
        "ubpr_cycles", lambda: seconds_until_next_release("quarterly"), _producer
    )


def report_sections(report_type_id: int = 283) -> list[dict[str, str]]:
    """Return the report's section table-of-contents (pageid + title)."""
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> list[dict[str, str]]:
        """Fetch the page list for the report type."""
        return [
            row
            for row in _post("UbprReportPagesList", {"ReportTypeID": report_type_id})
            if isinstance(row, dict) and row.get("pageid")
        ]

    return cached(
        ("ubpr_sections", report_type_id),
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )


def _section_id(section: str | None, report_type_id: int) -> tuple[str, str]:
    """Resolve a section title (or pageid) to its (pageid, title)."""
    sections = report_sections(report_type_id)
    if not sections:
        raise ValueError("The report section list could not be retrieved.")
    target = (section or "").strip().lower()
    for row in sections:
        if not target or row["pageid"] == target or row["pagetitle"].lower() == target:
            return row["pageid"], row["pagetitle"]
    raise ValueError(f"Unknown report section '{section}'.")


def _cell_parts(cell: str | None) -> list[tuple[float | None, str | None]]:
    """Split a period cell into its ``(value, concept-code)`` parts.

    Each part is ``"<value>;<code>;<fmt>;<dec>;''"``; the value parses to a float
    (``None`` when blank or non-numeric) and the code is the part's concept.
    """
    parts: list[tuple[float | None, str | None]] = []
    for part in (cell or "").split(", "):
        fields = part.split(";")
        token = fields[0].strip().strip("'")
        try:
            value: float | None = float(token)
        except (TypeError, ValueError):
            value = None
        code = fields[1].strip().strip("'") if len(fields) > 1 else None
        parts.append((value, code or None))
    return parts


def _triplet(
    cell: str | None,
) -> tuple[float | None, float | None, float | None]:
    """Resolve a period cell to its ``(bank, peer-group, percentile)`` values.

    The bank value is part 0; the peer-group value is the part whose concept code
    begins with ``UBPS`` and the percentile the part whose code begins with
    ``UBPK`` (each ``None`` when absent). The dollar pages carry no ``UBPS`` part,
    so their peer-group and percentile are ``None``.
    """
    parts = _cell_parts(cell)
    bank = parts[0][0] if parts else None
    pg = next((v for v, code in parts if code and code.startswith("UBPS")), None)
    pct = next((v for v, code in parts if code and code.startswith("UBPK")), None)
    return bank, pg, pct


def _pg_code(line: dict, period_cols: list[str]) -> str | None:
    """Return the line's peer-group (``UBPS``) concept code, if any."""
    for key in period_cols:
        for _, code in _cell_parts(line.get(key)):
            if code and code.startswith("UBPS"):
                return code
    return None


def _section_has_pg(lines: list[dict], period_cols: list[str]) -> bool:
    """Return whether any line in the section carries a ``UBPS`` peer-group part."""
    for line in lines:
        for key in period_cols:
            if any(
                code and code.startswith("UBPS")
                for _, code in _cell_parts(line.get(key))
            ):
                return True
    return False


def _concept_code(cell: str | None) -> str | None:
    """Extract the line's concept code from a period cell's bank token."""
    parts = (cell or "").split(", ")
    if not parts:  # pragma: no cover - str.split always yields a non-empty list
        return None
    bank = parts[0].split(";")
    return bank[1].strip().strip("'") if len(bank) > 1 else None


def _caption(raw: str) -> str:
    """Strip UBPR markup and guard the leading indentation with a ``>``."""
    text = (
        raw.replace("#SectionTitle#", "").replace("#Bold#", "").replace("#Italic#", "")
    )
    body = text.lstrip(" ")
    indent = len(text) - len(body)
    return (">" + " " * indent + body) if indent else body


def rectangularize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Give every row the union of all columns (None-filled).

    Header rows carry only ``label``/``is_header``; without this the table derives
    its columns from the leading header row and never shows the period columns the
    line-item rows carry.
    """
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    for row in rows:
        for key in keys:
            row.setdefault(key, None)
    return rows


_LIST_OF_BANKS_FIELDS = {
    "rssd9001": "rssd_id",
    "rssd9050": "fdic_cert",
    "ubpr9346": "charter_class",
    "rssd9017": "name",
    "rssd9130": "city",
    "rssd9200": "state",
    "statename": "state_name",
    "ubprd218": "offices",
    "ubprd659": "average_assets",
    "ubpr4340": "net_income",
    "latitude": "latitude",
    "longitude": "longitude",
}


def _number(value: Any) -> float | int | None:
    """Parse a numeric cell, returning an int when the value is whole."""
    try:
        parsed = float(str(value).strip())
    except (TypeError, ValueError):
        return None
    return int(parsed) if parsed.is_integer() else parsed


def fetch_list_of_banks(peer_group: str, cycle_id: str) -> list[dict[str, Any]]:
    """Fetch the roster of banks in a peer group for one reporting cycle.

    Each record carries the bank's RSSD id, FDIC certificate, charter class,
    name, city/state, office count, average assets and quarterly net income
    (both in thousands of dollars), and map coordinates.
    """
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> list[dict[str, Any]]:
        """Fetch and normalize the peer-group roster for the cycle."""
        raw = _post(
            "LlistOfBanks",
            {
                "ReportingCycleID": str(cycle_id),
                "PeerGroupName": str(peer_group),
                "MaxRows": 0,
            },
        )
        rows: list[dict[str, Any]] = []
        for record in raw if isinstance(raw, list) else []:
            row: dict[str, Any] = {}
            for source, name in _LIST_OF_BANKS_FIELDS.items():
                value = record.get(source)
                if isinstance(value, str):
                    value = value.strip()
                if name in (
                    "offices",
                    "average_assets",
                    "net_income",
                    "latitude",
                    "longitude",
                ):
                    value = _number(value)
                row[name] = value or None
            rows.append(row)
        return rows

    return cached(
        ("ubpr_list_of_banks", str(peer_group), str(cycle_id)),
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )


def fetch_ubpr_section(
    rssd_id: str,
    section: str | None = "Summary Ratios",
    *,
    report_type_id: int = 283,
    periods: int = 5,
    peer_definition: str = "",
    all_periods: bool = False,
) -> dict[str, Any]:
    """Fetch one report section as wide rows across reporting periods.

    Parameters
    ----------
    all_periods : bool
        When False (default), return the most recent ``periods`` cycles. Ratio
        pages, which carry a peer group, use ``"<ISO date> Bank|PG|PCT"`` columns;
        dollar pages, which do not, use one ``"<ISO date>"`` bank column per
        period. When True, return every reported cycle as the bank's own time
        series, one ``"<ISO date>"`` column per period (peer-group and percentile
        columns omitted), newest first.

    Returns
    -------
    dict
        ``{section, rows}`` where each row is ``{label, is_header, <period cols>}``.
    """
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    page_id, title = _section_id(section, report_type_id)
    cycles = report_cycles() if all_periods else report_cycles()[:periods]
    cycle_ids = ",".join(c["reportingcycleid"] for c in cycles)

    def _producer() -> list[dict]:
        """Fetch the section's raw line rows for the period set."""
        return _post(
            "MyUbprLinesData",
            {
                "ID_RSSD": str(rssd_id),
                "ScheduleID": page_id,
                "ReportingCycleIdList": cycle_ids,
                "PeerDefinition": peer_definition,
            },
        )

    raw = cached(
        (
            "ubpr_lines",
            report_type_id,
            str(rssd_id),
            page_id,
            cycle_ids,
            peer_definition,
        ),
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )
    if not raw:
        return {"section": title, "rows": []}

    from openbb_federal_reserve.utils.concepts import (
        clean_name,
        concept_index,
        indented_name,
    )
    from openbb_federal_reserve.utils.guide import fetch_guide_concepts

    index = concept_index("ubpr_ratio_single")
    period_cols = sorted(
        (k for k in raw[0] if _PERIOD.match(k)),
        key=lambda k: (k[6:], k[:2], k[3:5]),
        reverse=True,
    )
    iso = {k: f"{k[6:]}-{k[:2]}-{k[3:5]}" for k in period_cols}
    ordered = sorted(raw, key=lambda r: int(r.get("linedisplayorder") or 0))
    line_ids: dict[str, str] = {}
    for line in ordered:
        for key in period_cols:
            code = _concept_code(line.get(key))
            if code:
                line_id = line.get("lineid")
                if line_id:
                    line_ids.setdefault(code, str(line_id))
                break
    guide = fetch_guide_concepts(list(line_ids), lines=line_ids)
    has_pg = not all_periods and _section_has_pg(ordered, period_cols)
    rows: list[dict] = []
    for line in ordered:
        caption = str(line.get("linecaption", ""))
        if caption == "#BlankLine#":
            continue
        is_header = (
            caption.startswith("#SectionTitle#")
            or not period_cols
            or all(_triplet(line.get(k))[0] is None for k in period_cols)
        )
        if is_header:
            rows.append(
                {"label": _caption(caption), "is_header": True, "narrative": None}
            )
            continue
        code = None
        for key in period_cols:
            code = _concept_code(line.get(key))
            if code:
                break
        meta = index.get(code or "", {})
        g = guide.get(code or "", {})
        label_name = clean_name(g.get("description")) or meta.get("name")
        bank_monetary = bool(meta.get("monetary"))
        pg_monetary = bool(
            index.get(_pg_code(line, period_cols) or "", {}).get("monetary")
        )
        record: dict[str, Any] = {
            "label": indented_name(_caption(caption), label_name),
            "is_header": False,
            "narrative": g.get("narrative") or meta.get("narrative"),
        }
        for key in period_cols:
            bank, pg, pct = _triplet(line.get(key))
            if bank is not None and bank_monetary:
                bank *= 1000
            if pg is not None and pg_monetary:
                pg *= 1000
            if all_periods:
                record[iso[key]] = bank
            elif has_pg:
                record[f"{iso[key]} Bank"] = bank
                record[f"{iso[key]} PG"] = pg
                record[f"{iso[key]} PCT"] = pct
            else:
                record[iso[key]] = bank
        rows.append(record)
    rows = rectangularize(rows)
    if (
        rows
        and rows[0].get("is_header")
        and all(rows[0].get(key) is None for key in iso.values())
    ):
        from openbb_federal_reserve.utils.ubpr_pages import UBPR_PAGE_DESCRIPTIONS

        rows[0]["narrative"] = UBPR_PAGE_DESCRIPTIONS.get(title)
    return {"section": title, "rows": rows}
