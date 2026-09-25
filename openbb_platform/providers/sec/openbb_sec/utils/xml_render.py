"""Render SEC XML documents as structured HTML for the filing viewer.

Repeating records (e.g. ABS-EE asset data) are presented as tables, single
elements as key/value pairs, and document-level comments as collapsible notes.
"""

import re
from html import escape

MAX_ROWS = 1000
MAX_DEPTH = 6


def _local(tag) -> "str | None":
    """Return an element's local name, or None for comments and PIs."""
    if not isinstance(tag, str):
        return None
    return tag.rsplit("}", 1)[-1]


def _humanize(name: str) -> str:
    """Turn ``camelCase``/``snake_case`` element names into ``Title Case``."""
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", (name or "").replace("_", " "))
    return spaced[:1].upper() + spaced[1:] if spaced else spaced


def _is_leaf(elem) -> bool:
    """Whether an element has no child elements."""
    return len(elem) == 0


def _is_record(elem) -> bool:
    """Whether an element is a record: has children, all of them leaves."""
    kids = [c for c in elem if isinstance(c.tag, str)]
    return bool(kids) and all(_is_leaf(c) for c in kids)


def is_asset_data_root(tag) -> bool:
    """Whether a root tag denotes ABS-EE asset data (vs XBRL or other XML).

    The record-to-table rendering is meaningful only for ABS-EE asset data;
    applied to an XBRL instance it would tabulate ``context``/``unit``
    internals. Gate on the ABS-EE root element/namespace instead.
    """
    if not isinstance(tag, str):
        return False
    return (_local(tag) or "").lower() == "assetdata" or "absee" in tag.lower()


def _text(elem) -> str:
    """Trimmed text content of a leaf element."""
    return (elem.text or "").strip()


def _tail_text(elem) -> str:
    """Trimmed tail text that follows an element (e.g., CDATA notes)."""
    return (elem.tail or "").strip()


def _records_table(members: list) -> str:
    """Render a list of like records as an HTML table (columns = fields)."""
    members = members[:MAX_ROWS]
    cols: list = []
    seen: set = set()
    for member in members:
        for child in member:
            name = _local(child.tag)
            if name and name not in seen:
                seen.add(name)
                cols.append(name)
    if not cols:
        return ""
    head = "".join(f"<th>{escape(_humanize(c))}</th>" for c in cols)
    rows = []
    for member in members:
        values = {
            _local(child.tag): _text(child)
            for child in member
            if _local(child.tag) is not None
        }
        cells = "".join(f"<td>{escape(values.get(c, ''))}</td>" for c in cols)
        rows.append(f"<tr>{cells}</tr>")
    return (
        f"<table class=ob-tbl><thead><tr>{head}</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def _kv_table(pairs: list) -> str:
    """Render single elements as a key/value table."""
    rows = "".join(
        f"<tr><th>{escape(_humanize(k))}</th><td>{escape(v)}</td></tr>"
        for k, v in pairs
    )
    return f"<table class=ob-kv><tbody>{rows}</tbody></table>"


def _render_element(elem, parts: list, depth: int) -> None:
    """Walk an element, appending HTML fragments for its child structure."""
    groups: dict = {}
    order: list = []
    pending_comments: list = []
    for child in elem:
        name = _local(child.tag)
        if name is None:
            note = (child.text or "").strip()
            if note:
                pending_comments.append(note)
            continue
        if name not in groups:
            groups[name] = []
            order.append(name)
        groups[name].append(child)

    pending: list = []

    def flush() -> None:
        if pending:
            parts.append(_kv_table(list(pending)))
            pending.clear()

    for i, note in enumerate(pending_comments, start=1):
        pending.append((f"comment{i}", note))

    for name in order:
        members = groups[name]
        records = [m for m in members if _is_record(m)]
        if len(members) >= 2 and len(records) == len(members):
            flush()
            parts.append(f"<h2>{escape(_humanize(name))}</h2>")
            parts.append(_records_table(members))
            if len(members) > MAX_ROWS:
                parts.append(
                    f"<p class=ob-trunc>Showing the first {MAX_ROWS} of "
                    f"{len(members)} records.</p>"
                )
        elif len(members) >= 2 and all(_is_leaf(m) for m in members):
            flush()
            parts.append(f"<h2>{escape(_humanize(name))}</h2>")
            cells = "".join(
                f"<tr><td>{escape(_text(m))}</td></tr>" for m in members[:MAX_ROWS]
            )
            parts.append(f"<table class=ob-tbl><tbody>{cells}</tbody></table>")
        elif len(members) == 1 and _is_leaf(members[0]):
            value = _text(members[0])
            tail = _tail_text(members[0])
            if tail and value:
                pending.append((value, tail))
            elif tail:
                pending.append((name, tail))
            else:
                pending.append((name, value))
        elif depth < MAX_DEPTH:
            flush()
            for member in members[:MAX_ROWS]:
                parts.append(f"<h2>{escape(_humanize(name))}</h2>")
                _render_element(member, parts, depth + 1)
    flush()


def render_xml_as_html(
    xml_bytes: bytes, source_url: str = "", truncated: bool = False
) -> "str | None":
    """Render XML bytes as HTML reflecting the document's actual structure.

    Parameters
    ----------
    xml_bytes : bytes
        Raw XML, possibly a truncated head of a large document.
    source_url : str
        Original document URL, linked when the rendering is a partial preview.
    truncated : bool
        Whether ``xml_bytes`` is a bounded head of a larger file.

    Returns
    -------
    str | None
        HTML rendering, or None when the bytes cannot be parsed.
    """
    from lxml import etree

    parser = etree.XMLParser(
        recover=True, huge_tree=True, resolve_entities=False, no_network=True
    )
    try:
        root = etree.fromstring(xml_bytes, parser=parser)
    except Exception:  # noqa: BLE001
        return None

    if root is None or not isinstance(root.tag, str):
        return None

    if not (
        is_asset_data_root(root.tag) or (_local(root.tag) or "").lower() == "comments"
    ):
        return None

    legend = [
        (c.text or "").strip()
        for c in root
        if c.tag is etree.Comment and (c.text or "").strip()
    ]
    parts: list = []
    _render_element(root, parts, 0)
    if not parts and not legend:
        return None

    has_table = any("ob-tbl" in p for p in parts)
    title = _humanize(_local(root.tag) or "")
    head = f"<h1>{escape(title)}</h1>" if title else ""

    notes = ""
    if legend:
        open_attr = "" if has_table else " open"
        body = "".join(f"<p>{escape(c)}</p>" for c in legend)
        notes = (
            f"<details class=ob-note{open_attr}>"
            f"<summary>Document notes ({len(legend)})</summary>{body}</details>"
        )

    preview = ""
    if truncated:
        link = (
            f' — <a href="{escape(source_url)}" target=_blank rel=noopener>'
            "open the full document</a>."
            if source_url
            else "."
        )
        preview = f"<p class=ob-trunc>Showing a preview of a large file{link}</p>"

    return (
        _STYLE
        + "<div class=ob-xml>"
        + head
        + preview
        + notes
        + "".join(parts)
        + "</div>"
    )


_STYLE = (
    "<style>"
    ".ob-xml{font:13px system-ui,-apple-system,sans-serif;color:#111;padding:2px}"
    ".ob-xml h1{font-size:17px;margin:6px 0 10px}"
    ".ob-xml h2{font-size:14px;margin:16px 0 6px;color:#222}"
    ".ob-tbl{border-collapse:collapse;margin:6px 0 14px;font-size:12px}"
    ".ob-tbl th,.ob-tbl td{border:1px solid #d4d4dc;padding:3px 8px;"
    "text-align:left;white-space:nowrap}"
    ".ob-tbl thead th{position:sticky;top:0;background:#f2f2f5;font-weight:600}"
    ".ob-kv{border-collapse:collapse;margin:6px 0 14px;font-size:12.5px}"
    ".ob-kv th{text-align:left;padding:2px 14px 2px 0;color:#555;"
    "font-weight:600;vertical-align:top;white-space:nowrap}"
    ".ob-kv td{padding:2px 0}"
    ".ob-note{margin:8px 0}.ob-note summary{cursor:pointer;color:#555;"
    "font-size:12px}.ob-note p{margin:4px 0;font-size:12px;"
    "line-height:1.5;color:#333}"
    ".ob-trunc{color:#a15c00;font-size:12px;margin:6px 0;font-weight:600}"
    "</style>"
)
