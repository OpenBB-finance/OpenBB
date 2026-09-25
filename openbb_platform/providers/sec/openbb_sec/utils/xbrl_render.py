"""Render an XBRL instance document as its as-filed statement tables.

Parsing is delegated to ``XBRLParser.parse_instance`` (the project's XBRL
helper), which resolves facts against the filing's label and presentation
linkbases. Facts are grouped by their presentation table (Cover, Balance
Sheets, Statements of Operations, notes, ...) and pivoted into period columns.
"""

from html import escape

from openbb_sec.utils.xml_render import _humanize

_HEADER_LABELS = ("Entity Registrant Name", "Document Type", "Document Period End Date")


def _looks_xbrl(xml_bytes: bytes) -> bool:
    """Cheap check for an XBRL instance before invoking the full parser."""
    head = xml_bytes[:4000].lower()
    return b"xbrl.org/2003/instance" in head or b"<xbrl" in head


def _strip_prefix(value: str) -> str:
    """Drop a ``prefix:`` qualifier from a QName-like string."""
    return value.rsplit(":", 1)[-1] if value and ":" in value else (value or "")


def _clean_member(value: str) -> str:
    """Humanize a dimension member, dropping a trailing ``[Member]``/``Member``."""
    local = _strip_prefix(value).strip()
    if local.endswith("[Member]"):
        local = local[: -len("[Member]")].strip()
    elif local.endswith("Member"):
        local = local[:-6]
    return _humanize(local)


def _dims_str(dims) -> str:
    """Render a fact's dimensional members (``parse_instance`` axis->member map)."""
    if not isinstance(dims, dict) or not dims:
        return ""
    members = []
    for member in dims.values():
        if isinstance(member, dict):
            text = member.get("label") or member.get("member") or ""
        else:
            text = str(member)
        cleaned = _clean_member(text)
        if cleaned:
            members.append(cleaned)
    return "; ".join(members)


def _period_label(fact: dict) -> str:
    """Human label for a fact's reporting period."""
    start, end = fact.get("start") or "", fact.get("end") or ""
    if fact.get("period_type") == "instant" or not start:
        return end
    return f"{start} – {end}"


def _period_sort_key(label: str) -> str:
    """Sort periods by their end date (the trailing ``YYYY-MM-DD``)."""
    return label[-10:] if len(label) >= 10 else label


def _is_text_block(fact: dict) -> bool:
    """Whether a fact carries an HTML disclosure rather than a data point."""
    if (fact.get("tag") or "").endswith("TextBlock"):
        return True
    value = fact.get("value")
    return isinstance(value, str) and value.lstrip()[:1] == "<"


def _format_value(value) -> str:
    """Format a numeric fact with thousands separators; pass text through."""
    if value in (None, ""):
        return ""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{int(number):,}" if number == int(number) else f"{number:,}"


def _pivot_table(entries: list, units: dict) -> str:
    """Pivot one presentation table's facts into period columns."""
    periods: list = []
    rows: dict = {}
    row_unit: dict = {}
    for fact, pres in entries:
        period = _period_label(fact)
        if period and period not in periods:
            periods.append(period)
        label = fact.get("label") or fact.get("tag")
        dims = _dims_str(fact.get("dimensions"))
        key = (pres.get("order") or 0.0, label, dims)
        rows.setdefault(key, {})[period] = fact.get("value")
        if fact.get("unit"):
            row_unit[key] = units.get(fact["unit"], fact["unit"])
    periods = sorted(periods, key=_period_sort_key, reverse=True)

    head = (
        "<th>Line item</th>"
        + "".join(f"<th>{escape(p)}</th>" for p in periods)
        + "<th>Unit</th>"
    )
    body = []
    for key in sorted(rows, key=lambda k: (k[0], k[1])):
        _, label, dims = key
        display = f"{label} — {dims}" if dims else label
        cells = "".join(
            f"<td class=num>{escape(_format_value(rows[key].get(p)))}</td>"
            for p in periods
        )
        body.append(
            f"<tr><td>{escape(display)}</td>{cells}"
            f"<td>{escape(row_unit.get(key, ''))}</td></tr>"
        )
    return (
        f"<table class=ob-tbl><thead><tr>{head}</tr></thead>"
        f"<tbody>{''.join(body)}</tbody></table>"
    )


def _header_line(facts: dict) -> str:
    """Entity / document context line from the cover facts."""
    found: dict = {}
    for fact_list in facts.values():
        for fact in fact_list:
            label = fact.get("label")
            if label in _HEADER_LABELS and label not in found:
                found[label] = fact.get("value")
    bits = [found[label] for label in _HEADER_LABELS if found.get(label)]
    return " · ".join(str(b) for b in bits)


def render_xbrl_facts(
    xml_bytes: bytes, source_url: str = "", truncated: bool = False
) -> "str | None":
    """Render an XBRL instance as as-filed statement tables; None if not XBRL."""
    if not _looks_xbrl(xml_bytes):
        return None

    import io

    from openbb_sec.utils.xbrl_taxonomy_helper import XBRLParser

    base_url = source_url.rsplit("/", 1)[0] + "/" if source_url else None
    try:
        _contexts, units, facts = XBRLParser().parse_instance(
            io.BytesIO(xml_bytes), base_url=base_url
        )
    except Exception:  # noqa: BLE001
        return None
    if not facts:
        return None

    tables: dict = {}
    for fact_list in facts.values():
        for fact in fact_list:
            for pres in fact.get("presentation") or []:
                tables.setdefault(pres.get("table") or "Other", []).append((fact, pres))
    if not tables:
        return None

    ordered = sorted(tables, key=lambda name: (name != "Cover", name))

    parts = ["<h1>XBRL Facts</h1>"]
    header = _header_line(facts)
    if header:
        parts.append(f"<p class=ob-meta>{escape(header)}</p>")
    if truncated:
        link = (
            f' — <a href="{escape(source_url)}" target=_blank rel=noopener>'
            "open the full document</a>."
            if source_url
            else "."
        )
        parts.append(f"<p class=ob-trunc>Showing a preview of a large file{link}</p>")
    for name in ordered:
        human = _humanize(name)
        text_blocks, data_entries = [], []
        for fact, pres in tables[name]:
            (text_blocks if _is_text_block(fact) else data_entries).append((fact, pres))
        body = _pivot_table(data_entries, units) if data_entries else ""
        seen: set = set()
        for fact, _pres in text_blocks:
            value = (fact.get("value") or "").strip()
            if value and value not in seen:
                seen.add(value)
                # Disclosure text blocks are as-filed HTML (same trust model as
                # the filing HTML the viewer already renders); inject verbatim.
                body += f"<div class=ob-textblock>{value}</div>"
        parts.append(
            f'<section class=ob-sec data-name="{escape(human)}">'
            f"<h2>{escape(human)}</h2>{body}</section>"
        )

    return _STYLE + "<div class=ob-xbrl>" + "".join(parts) + "</div>"


_STYLE = (
    "<style>"
    ".ob-xbrl{font:13px system-ui,-apple-system,sans-serif;color:#111;padding:2px}"
    ".ob-xbrl h1{font-size:17px;margin:6px 0 4px}"
    ".ob-xbrl h2{font-size:14px;margin:16px 0 6px;color:#222}"
    ".ob-meta{color:#555;font-size:12.5px;margin:0 0 10px}"
    ".ob-tbl{border-collapse:collapse;margin:6px 0 14px;font-size:12px;width:100%}"
    ".ob-tbl th,.ob-tbl td{border:1px solid #d4d4dc;padding:3px 8px;"
    "text-align:left;vertical-align:top}"
    ".ob-tbl thead th{position:sticky;top:0;background:#f2f2f5;font-weight:600}"
    ".ob-tbl td.num{text-align:right;font-variant-numeric:tabular-nums;"
    "white-space:nowrap}"
    ".ob-textblock{margin:8px 0 16px;overflow-x:auto}"
    ".ob-textblock table{border-collapse:collapse}"
    ".ob-trunc{color:#a15c00;font-size:12px;margin:6px 0;font-weight:600}"
    "</style>"
)
