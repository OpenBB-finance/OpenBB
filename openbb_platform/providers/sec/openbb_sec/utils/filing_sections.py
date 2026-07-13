"""Extract SEC filing item sections from filing markdown and HTML."""

import re

_ITEM_HEADER = re.compile(
    r"^(?:#{1,4}\s*)?\*{0,2}\s*"
    r"(?:Part\s+(?:I{1,3}|[1-4])[.\s,\-–—]*)?"
    r"(?:ITEM|Item)\s*(1[0-5]?|[2-9])([A-Ca-c])?"
    r"[.\s\-–—:)]*\s*(.*)$",
    re.IGNORECASE,
)
_PART_HEADER = re.compile(
    r"^(?:#{1,4}\s*)?\*{0,2}\s*Part\s+(I{1,3}|IV|[1-4])\b",
    re.IGNORECASE,
)
_ANY_ITEM_TEXT = re.compile(
    r"^(?:Part\s+(?:I{1,3}|IV|[1-4])[.\s,\-–—]*)?(?:ITEM|Item)\s*(1[0-5]?|[2-9])([A-Ca-c])?\b",
    re.IGNORECASE,
)


def strip_markdown_footers(text: str) -> str:
    """Remove page footers (e.g. 'Apple Inc. | 2025 Form 10-K | 3') and page numbers."""
    if not text:
        return ""
    text = re.sub(
        r"(?im)^[ \t]*[A-Za-z][^|\n]{0,60}?\|\s*(?:\d{2,4}\s+)?(?:form\s+)?10-[kq]\s*\|\s*\d{1,4}[ \t]*",
        "",
        text,
    )
    kept: list = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped and len(stripped) < 100:
            if re.match(r"^\d{1,4}$", stripped):
                continue
            if re.search(r"(?i)\bform\s+10-[kq]\b", stripped) and any(
                ch.isdigit() for ch in stripped
            ):
                continue
        kept.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(kept)).strip()


_NEEDS_REFLOW = re.compile(r"(?m)^ {4}\S|\S {3,}\S")
_COLUMN_GAP = re.compile(r"(?<=\S) {3,}(?=\S)")
_VALUE_TOKEN = re.compile(
    r"\(\s*\$?\s*[\d,]+(?:\.\d+)?\s*\)|\$\s*[\d,]+(?:\.\d+)?|[\d,]+(?:\.\d+)?|--+|\*"
)


def _value_tokens(line: str) -> list:
    """Return (start, end, text) for each numeric value token in a line."""
    return [
        (m.start(), m.end(), m.group().strip()) for m in _VALUE_TOKEN.finditer(line)
    ]


def _nearest(position: int, columns: list) -> int:
    """Index of the value column whose right edge is closest to ``position``."""
    return min(range(len(columns)), key=lambda k: abs(position - columns[k]))


def _fixed_width_table_to_markdown(lines: list) -> str | None:
    """Convert a fixed-width ASCII table block into a markdown table."""
    body = [line.rstrip() for line in lines if line.strip()]
    if len(body) < 2:
        return None

    edges: dict = {}
    for line in body:
        tokens = _value_tokens(line)
        if len(tokens) >= 3:
            for _start, end, _text in tokens:
                edges[end] = edges.get(end, 0) + 1
    if not edges:
        return None

    clusters: list = []
    for end in sorted(edges):
        if clusters and end - clusters[-1][0] <= 4:
            clusters[-1] = (end, clusters[-1][1] + edges[end])
        else:
            clusters.append((end, edges[end]))
    cols = [end for end, count in clusters if count >= 3]
    if len(cols) < 2:
        return None

    boundary = min(
        start
        for line in body
        for start, end, _text in _value_tokens(line)
        if any(abs(end - c) <= 4 for c in cols)
    )

    def numeric_tail(line: str) -> bool:
        tail = line[boundary:]
        return bool(tail.strip()) and not re.search(r"[A-Za-z]{2,}", tail)

    first = next((i for i, line in enumerate(body) if numeric_tail(line)), None)
    if first is None:
        return None

    label_header = ""
    headers = [""] * len(cols)
    for line in body[:first]:
        for token in re.finditer(r"\S+(?: \S+)*?(?=\s{2,}|$)", line):
            text = token.group().strip()
            if token.end() <= boundary:
                label_header = f"{label_header} {text}".strip()
            else:
                index = _nearest(token.end(), cols)
                headers[index] = f"{headers[index]} {text}".strip()

    def row_values(line: str) -> list:
        out = [""] * len(cols)
        for start, end, text in _value_tokens(line):
            if start < boundary:
                continue
            index = _nearest(end, cols)
            out[index] = f"{out[index]} {text}".strip()
        return out

    rows: list = []
    pending = ""
    for line in body[first:]:
        if numeric_tail(line):
            label = f"{pending} {line[:boundary].strip()}".strip()
            pending = ""
            rows.append([label, *row_values(line)])
        else:
            pending = f"{pending} {line.strip()}".strip()

    def clean(value: str) -> str:
        value = re.sub(r"\.{2,}", "", value)
        return re.sub(r"\s+", " ", value).strip().replace("|", r"\|")

    out_lines = [
        "| " + " | ".join(clean(h) for h in [label_header, *headers]) + " |",
        "|" + "|".join(["---"] * (len(cols) + 1)) + "|",
    ]
    out_lines += ["| " + " | ".join(clean(c) for c in row) + " |" for row in rows]
    return "\n".join(out_lines)


def _column_gaps(line: str) -> int:
    """Count 3+ space column gaps between non-space characters in a line."""
    return len(_COLUMN_GAP.findall(line))


def _is_heading(line: str) -> bool:
    """Return True for a short, standalone line that reads as a section heading."""
    return (
        3 <= len(line) <= 60
        and line[0].isupper()
        and line[-1] not in ".,;:"
        and "  " not in line
    )


def reflow_plain_text(text: str, force: bool = False) -> str:
    """Reflow fixed-width plain-text filing prose into clean markdown."""
    if not text or (not force and not _NEEDS_REFLOW.search(text)):
        return text

    out: list = []
    paragraph: list = []
    table: list = []
    md_table: list = []
    in_table = False

    def flush_paragraph() -> None:
        if not paragraph:
            return
        if len(paragraph) == 1 and _is_heading(paragraph[0].strip()):
            out.append(f"**{paragraph[0].strip()}**")
        else:
            joined = re.sub(
                r"\s+", " ", " ".join(line.strip() for line in paragraph)
            ).strip()
            if (
                out
                and out[-1][:1] not in ("*", "|", "#")
                and out[-1][-1:] not in (".", ";", ":", "!", "?", ")", '"', "'")
                and joined[:1].islower()
            ):
                out[-1] = f"{out[-1]} {joined}"
            else:
                out.append(joined)
        paragraph.clear()

    def flush_table() -> None:
        nonlocal in_table
        block = [line for line in table if line.strip()]
        if block:
            markdown = _fixed_width_table_to_markdown(table)
            out.append(markdown or re.sub(r"\s+", " ", " ".join(block)).strip())
        table.clear()
        in_table = False

    def flush_md_table() -> None:
        if md_table:
            out.append("\n".join(md_table))
            md_table.clear()

    for raw in text.split("\n"):
        stripped = raw.strip()
        if re.fullmatch(r"<PAGE>|\d{1,4}", stripped):
            continue
        if stripped.startswith("|"):
            flush_paragraph()
            flush_table()
            md_table.append(stripped)
            continue
        flush_md_table()
        if in_table:
            if stripped and _column_gaps(raw) == 0 and len(stripped) > 50:
                flush_table()
                paragraph.append(raw)
            else:
                table.append(raw)
            continue
        if not stripped:
            flush_paragraph()
            continue
        if _column_gaps(raw) >= 2 and any(ch.isdigit() for ch in raw):
            header: list = []
            while paragraph and _column_gaps(paragraph[-1]) >= 1:
                header.insert(0, paragraph.pop())
            flush_paragraph()
            table.extend(header)
            table.append(raw)
            in_table = True
            continue
        paragraph.append(raw)
    flush_paragraph()
    flush_table()
    flush_md_table()

    if len(out) == 1 and out[0].startswith("**") and out[0].endswith("**"):
        out[0] = out[0][2:-2]

    return "\n\n".join(out)


def extract_section_html(html: str, item_num: str) -> str:
    """Return the raw HTML of an item section, located by its short item header."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")

    line_starts: list = [0]
    for line in html.split("\n"):
        line_starts.append(line_starts[-1] + len(line) + 1)

    def _offset(element) -> int:
        line = element.sourceline or 1
        return line_starts[line - 1] + (element.sourcepos or 0)

    candidates: list = []
    seen: set = set()
    for element in soup.find_all(["div", "p", "td"]):
        pos = _offset(element)
        text = element.get_text(" ", strip=True).replace("\xa0", " ")
        if len(text) > 80:
            continue
        match = _ANY_ITEM_TEXT.match(text)
        if not match:
            continue
        remainder = text[match.end() :].strip(" .:)-—–\t")
        if remainder and not re.match(r"^[A-Z&(]", remainder):
            continue
        num = f"{match.group(1)}{(match.group(2) or '').upper()}"
        key = (num, pos // 64)
        if key in seen:
            continue
        seen.add(key)
        candidates.append((pos, num, bool(remainder)))

    candidates.sort()
    target = item_num.upper()
    titled = [pos for pos, num, has_title in candidates if num == target and has_title]
    untitled = [pos for pos, num, _ in candidates if num == target]
    if titled:
        start = titled[0]
    elif untitled:
        start = untitled[-1]
    else:
        return ""
    end = next(
        (pos for pos, num, _ in candidates if pos > start and num != target), len(html)
    )
    return html[start:end]


def _is_bold_paragraph(element) -> bool:
    """Return True if a block element's text is predominantly bold."""
    text = element.get_text(" ", strip=True)
    if not text:
        return False
    bold = 0
    for tag in element.find_all(["b", "strong"]):
        bold += len(tag.get_text(strip=True))
    for span in element.find_all("span"):
        style = (span.get("style") or "").replace(" ", "").lower()
        if re.search(r"font-weight:(?:bold|bolder|[6-9]00)", style):
            bold += len(span.get_text(strip=True))
    return bold >= 0.6 * len(re.sub(r"\s", "", text))


def split_bold_sections(section_html: str, heading_key: str) -> list:
    """Split a section's HTML into blocks at bold sub-headings."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(section_html, "html.parser")
    item_header = re.compile(r"(?i)^(?:part\s+\w+[\s.,:-]*)?item\s+\d")
    skip = re.compile(r"(?i)^table\s+of\s+contents$")
    blocks: list = []
    current: dict = {heading_key: None, "text": ""}
    for para in soup.find_all(["div", "p"]):
        if para.find(["div", "p"]) or para.find_parent("table"):
            continue
        text = re.sub(
            r"\s+", " ", para.get_text(" ", strip=True).replace("\xa0", " ")
        ).strip()
        if (
            not text
            or item_header.match(text)
            or skip.match(text)
            or not strip_markdown_footers(text)
        ):
            continue
        if _is_bold_paragraph(para):
            if current[heading_key] or current["text"].strip():
                blocks.append(current)
            current = {heading_key: text, "text": ""}
        else:
            current["text"] = (
                current["text"] + "\n\n" + text if current["text"] else text
            )
    if current[heading_key] or current["text"].strip():
        blocks.append(current)
    for block in blocks:
        block["text"] = block["text"].strip()
    return [b for b in blocks if b["text"] or b[heading_key]]


def _clean_markdown(markdown: str) -> str:
    """Strip leftover anchor tags and table-of-contents breadcrumb links."""
    markdown = re.sub(r"<a\s[^>]*>\s*</a>", "", markdown)
    return re.sub(r"^(?:\[[^\]]*\]\(#[^)]*\)\s*)+", "", markdown, flags=re.MULTILINE)


def _part_label(value: str) -> str:
    """Normalize a Part marker to a Roman numeral."""
    value = value.upper()
    return {"1": "I", "2": "II", "3": "III", "4": "IV"}.get(value, value)


def extract_item_sections(markdown: str) -> dict:
    """Extract item sections from a filing's markdown, keyed by item id."""
    if not markdown:
        return {}

    lines = _clean_markdown(markdown).splitlines()

    headers: list = []
    part = "I"
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        part_match = _PART_HEADER.match(stripped)
        if part_match:
            part = _part_label(part_match.group(1))
        item_match = _ITEM_HEADER.match(stripped)
        if not item_match:
            continue
        num = f"{item_match.group(1)}{(item_match.group(2) or '').upper()}"
        title = item_match.group(3).strip()[:120]
        headers.append((index, num, title, part))

    if not headers:
        return {}

    items: dict = {}
    for position, (line_index, num, title, item_part) in enumerate(headers):
        end = headers[position + 1][0] if position + 1 < len(headers) else len(lines)
        text = "\n".join(lines[line_index:end]).strip()

        name = title
        if not name:
            for offset in range(line_index + 1, min(line_index + 4, len(lines))):
                candidate = lines[offset].strip()
                if candidate:
                    name = re.sub(r"^#+\s*|\*+", "", candidate).strip()[:120]
                    break

        key = f"item_II_{num}" if item_part not in ("I", "") else f"item_{num}"
        items.setdefault(
            key,
            {
                "name": name or f"Item {num}",
                "item_num": num,
                "part": item_part,
                "text": text,
            },
        )
    return items


_XREF_PART_LINE = re.compile(r"^\s*\|\s*Part\s+(I{1,3}|IV|[1-4])\s*\|", re.IGNORECASE)
_XREF_ITEM_LINE = re.compile(
    r"^\s*\|\s*Item\s+(1[0-5]?|[2-9])([A-Ca-c])?\s*\|"
    r"\s*([^|]+?)\s*\|"
    r"\s*([^|]*?)\s*\|\s*$",
    re.IGNORECASE,
)
_XREF_ANCHOR_HREF = re.compile(r"\[\d+\]\(#([^)]+)\)")
_HTML_ANCHOR_ID = re.compile(
    r"""<a\s+(?:[^>]*\s+)?id\s*=\s*["']([^"']+)["'][^>]*>\s*</a>"""
)


def extract_via_cross_reference(markdown: str) -> dict:
    """Build item sections from a 'Form 10-K Cross-Reference Index' anchor table.

    Some issuers (e.g. McDonald's) restructure their 10-K with custom headings
    like "About McDonald's" instead of "Item 1. Business", and include an
    end-of-document table mapping each Item number to an in-document anchor.
    This walks those anchors in document order and slices section content
    between consecutive item anchors.
    """
    if not markdown:
        return {}

    anchor_positions: dict = {}
    for match in _HTML_ANCHOR_ID.finditer(markdown):
        anchor_positions.setdefault(match.group(1), match.start())
    if not anchor_positions:
        return {}

    rows: list = []
    current_part = "I"
    for line in markdown.splitlines():
        part_match = _XREF_PART_LINE.match(line)
        if part_match:
            current_part = _part_label(part_match.group(1))
            continue
        item_match = _XREF_ITEM_LINE.match(line)
        if not item_match:
            continue
        anchor_match = _XREF_ANCHOR_HREF.search(item_match.group(4))
        if not anchor_match:
            continue
        pos = anchor_positions.get(anchor_match.group(1))
        if pos is None:
            continue
        num = f"{item_match.group(1)}{(item_match.group(2) or '').upper()}"
        name = item_match.group(3).strip()[:120]
        rows.append((pos, num, name, current_part))

    if not rows:
        return {}

    rows.sort(key=lambda r: r[0])
    items: dict = {}
    for index, (pos, num, name, item_part) in enumerate(rows):
        end = rows[index + 1][0] if index + 1 < len(rows) else len(markdown)
        text = _HTML_ANCHOR_ID.sub("", markdown[pos:end]).strip()
        key = f"item_II_{num}" if item_part not in ("I", "") else f"item_{num}"
        items.setdefault(
            key,
            {
                "name": name,
                "item_num": num,
                "part": item_part,
                "text": text,
            },
        )
    return items
