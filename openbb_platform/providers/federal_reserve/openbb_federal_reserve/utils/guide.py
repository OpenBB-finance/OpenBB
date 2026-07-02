"""FFIEC UBPR Interactive User's Guide concept client."""

from __future__ import annotations

import re

GUIDE_URL = "https://cdr.ffiec.gov/Public/Reports/InteractiveUserGuide.aspx"
_GUIDE_RSSD = "451965"

_BLOCK_BREAK = re.compile(
    r"(?is)<\s*/?\s*(?:br|div|p|li|tr|td|th|h[1-6]|ul|ol|table)\b[^>]*>"
)
_INLINE_TAG = re.compile(r"<[^>]+>")
_DIV_TAG = re.compile(r"(?is)<\s*(/?)div\b[^>]*>")


def _field(segment: str, label: str) -> str:
    """Pull one labelled field's full text out of a guide concept block."""
    import html as html_lib

    header = re.search(r"<b>" + re.escape(label) + r"</b></div>", segment)
    if not header:
        return ""
    rest = segment[header.end() :]
    opener = re.match(r"\s*<div[^>]*>", rest)
    if not opener:
        return ""
    body = rest[opener.end() :]
    depth = 1
    end = len(body)
    for tag in _DIV_TAG.finditer(body):
        depth += -1 if tag.group(1) else 1
        if depth == 0:
            end = tag.start()
            break
    inner = _BLOCK_BREAK.sub(" ", body[:end])
    inner = html_lib.unescape(_INLINE_TAG.sub("", inner))
    return re.sub(r"\s+", " ", inner).strip()


def _parse_guide(html: str) -> dict[str, dict[str, str]]:
    """Parse a guide page into ``{concept: {"description", "narrative"}}``."""
    concepts: dict[str, dict[str, str]] = {}
    for segment in re.split(r"<b>Concept</b>", html)[1:]:
        match = re.search(r'id="content(\w+)-label"[^>]*>\s*(\w+)\s*<', segment)
        if not match:
            continue
        code = match.group(2)
        if code not in concepts:
            concepts[code] = {
                "description": _field(segment, "Description"),
                "narrative": _field(segment, "Narrative"),
            }
    return concepts


def _report_date() -> str:
    """Return the latest reporting cycle end date as ``MM/DD/YYYY`` for the guide URL."""
    from openbb_federal_reserve.utils.ubpr_report import report_cycles

    cycles = report_cycles()
    return cycles[0]["enddateformatted"] if cycles else ""


def ubpr_concept_lines() -> dict[str, str]:
    """Return a cached map of every UBPR concept code to a report line id."""
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> dict[str, str]:
        """Collect concept-to-line-id pairs across every UBPR report section."""
        from openbb_federal_reserve.utils.ubpr_report import (
            _PERIOD,
            _post,
            report_cycles,
            report_sections,
        )

        cycles = report_cycles()
        if not cycles:
            return {}
        cycle = str(cycles[0]["reportingcycleid"])
        mapping: dict[str, str] = {}
        for page in report_sections(283):
            rows = _post(
                "MyUbprLinesData",
                {
                    "ID_RSSD": _GUIDE_RSSD,
                    "ScheduleID": page["pageid"],
                    "ReportingCycleIdList": cycle,
                    "PeerDefinition": "",
                },
            )
            for line in rows if isinstance(rows, list) else []:
                line_id = line.get("lineid")
                if not line_id:
                    continue
                for key, value in line.items():
                    if _PERIOD.match(key) and value and ";" in str(value):
                        code = str(value).split(", ")[0].split(";")[1]
                        if code:
                            mapping.setdefault(code, str(line_id))
                        break
        return mapping

    return cached(
        "ubpr_concept_lines",
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )


def _concept_guide(concept: str, line_id: str, report_date: str) -> dict[str, str]:
    """Fetch and cache one concept's guide Description and Narrative for a line."""
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    def _producer() -> dict[str, str]:
        """Request the guide page for the line and parse the concept's fields."""
        from openbb_federal_reserve.utils.cdr import _get_session

        url = (
            f"{GUIDE_URL}?Report=uppr&LineID={line_id}&Rssd={_GUIDE_RSSD}"
            f"&Concept={concept}&ReportDate={report_date}"
        )
        html = _get_session().get(url, timeout=60).text
        return _parse_guide(html).get(concept) or {"description": "", "narrative": ""}

    return cached(
        ("ubpr_guide_concept", concept, str(line_id), report_date),
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )


def fetch_guide_concepts(
    concepts: list[str], lines: dict[str, str] | None = None
) -> dict[str, dict[str, str]]:
    """Return ``{concept: {"description", "narrative"}}`` for UBPR concepts via the guide.

    Parameters
    ----------
    concepts : list[str]
        The concept codes to resolve.
    lines : dict[str, str] | None
        An optional concept-to-line-id map (e.g. one already parsed from the
        section being rendered); falls back to :func:`ubpr_concept_lines`.
    """
    from concurrent.futures import ThreadPoolExecutor

    resolved = lines or ubpr_concept_lines()
    report_date = _report_date()
    pairs = sorted({(c, resolved[c]) for c in concepts if c in resolved})
    if not pairs or not report_date:
        return {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = pool.map(
            lambda pair: _concept_guide(pair[0], pair[1], report_date), pairs
        )
    return {concept: data for (concept, _), data in zip(pairs, results) if data}


def fetch_guide_narratives(
    concepts: list[str], lines: dict[str, str] | None = None
) -> dict[str, str]:
    """Return ``{concept: narrative}`` for UBPR concepts via the guide."""
    return {
        concept: data["narrative"]
        for concept, data in fetch_guide_concepts(concepts, lines).items()
        if data.get("narrative")
    }
