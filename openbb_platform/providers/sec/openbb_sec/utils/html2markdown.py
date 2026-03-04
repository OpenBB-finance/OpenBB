"""General purpose HTML to Markdown conversion for SEC Filings."""

# pylint: disable=C0103, C0200, C0301, C0302, R0911, R0912, R0913, R0914, R0915, R0916, R0917, R1702, W0130
# flake8: noqa: PLR0911, PLR0912, PLR0913, PLR0914, PLR0915, PLR0916, PLR0917, PLR1702

import re
import warnings
from collections import Counter
from copy import copy
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Comment, XMLParsedAsHTMLWarning
from bs4.element import NavigableString, Tag

# Suppress XML-as-HTML warnings (SEC files are often XML-like HTML)
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


# ============================================================================
# PUNCTUATION RULES FOR TEXT JOINING
# ============================================================================

NO_SPACE_BEFORE = {
    ".",
    ",",
    ":",
    ";",
    "!",
    "?",
    ")",
    "]",
    "}",
    '"',
    "'",
    "\u201c",
    "\u201d",
    "\u2018",
    "\u2019",
    "%",
}
# Characters that shouldn't have space AFTER them
NO_SPACE_AFTER = {"(", "[", "{", '"', "'", "\u201c", "\u201d", "\u2018", "\u2019", "$"}

# Bullet characters used in SEC filings (superset of all variants)
BULLET_CHARS = {"•", "\x95", "·", "○", "►", "●", "Ø", "\u00d8", "-", "–", "—"}

# Invisible/whitespace characters to strip
INVISIBLE_CHARS = "\u200b\u200c\u200d\ufeff\xa0"

# Month names pattern for date parsing (full names and standard 3-letter abbreviations)
MONTHS_PATTERN = (
    r"(?:January|February|March|April|May|June|July|August|"
    r"September|October|November|December|"
    r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
)

# Windows-1252 character mappings (both entity and byte forms)
WIN1252_MAP = {
    # Entity form (&#NNN;)
    "&#128;": "€",
    "&#130;": "‚",
    "&#131;": "ƒ",
    "&#132;": "„",
    "&#133;": "…",
    "&#134;": "†",
    "&#135;": "‡",
    "&#136;": "ˆ",
    "&#137;": "‰",
    "&#138;": "Š",
    "&#139;": "‹",
    "&#140;": "Œ",
    "&#142;": "Ž",
    "&#145;": "'",
    "&#146;": "'",
    "&#147;": '"',
    "&#148;": '"',
    "&#149;": "•",
    "&#150;": "–",
    "&#151;": "—",
    "&#152;": "˜",
    "&#153;": "™",
    "&#154;": "š",
    "&#155;": "›",
    "&#156;": "œ",
    "&#158;": "ž",
    "&#159;": "Ÿ",
    # Byte form (raw bytes decoded as Latin-1)
    chr(0x80): "€",
    chr(0x82): "‚",
    chr(0x83): "ƒ",
    chr(0x84): "„",
    chr(0x85): "…",
    chr(0x86): "†",
    chr(0x87): "‡",
    chr(0x88): "ˆ",
    chr(0x89): "‰",
    chr(0x8A): "Š",
    chr(0x8B): "‹",
    chr(0x8C): "Œ",
    chr(0x8E): "Ž",
    chr(0x91): "'",
    chr(0x92): "'",
    chr(0x93): """, chr(0x94): """,
    chr(0x95): "•",
    chr(0x96): "–",
    chr(0x97): "—",
    chr(0x98): "˜",
    chr(0x99): "™",
    chr(0x9A): "š",
    chr(0x9B): "›",
    chr(0x9C): "œ",
    chr(0x9E): "ž",
    chr(0x9F): "Ÿ",
}

_FINANCIAL_SPACE_RE = re.compile(
    r"^"
    r"(\$?)"  # optional $
    r"\s*"
    r"(\(?)"  # optional (
    r"\s*"
    r"(\$?)"  # optional $ after (
    r"\s*"
    r"([\d,]+\.?\d*)"  # the number
    r"\s*"
    r"(\)?)"  # optional )
    r"\s*"
    r"([%*]*(?:pts)?)"  # optional % or pts suffix
    r"$"
)
_DOLLAR_DASH_RE = re.compile(r"^\$\s*([\u2014\u2013\-])\s*(%?)$")
_DASH_PERCENT_RE = re.compile(r"^([\u2014\u2013\-])\s+(%)\s*$")


def strip_all(s):
    """Strip all whitespace and invisible characters from a string."""
    return s.strip().strip(INVISIBLE_CHARS).strip()


def _normalize_financial_cell(cell):
    """Normalize one cell value to compact financial format.

    '$ 1,787'     -> '$1,787'
    '( 135 )'     -> '(135)'
    '$ ( 471 )'   -> '$(471)'
    '( 0.2 ) %'   -> '(0.2)%'
    '$ —'         -> '$—'
    '— %'         -> '—%'
    """
    s = cell.strip()
    if not s:
        return cell
    # Dollar-dash patterns: $ — -> $—
    m = _DOLLAR_DASH_RE.match(s)
    if m:
        return "$" + m.group(1) + m.group(2)
    # Dash-percent patterns: — % -> —%
    m = _DASH_PERCENT_RE.match(s)
    if m:
        return m.group(1) + m.group(2)
    # Numeric values with optional $, parens, %
    m = _FINANCIAL_SPACE_RE.match(s)
    if m:
        dollar1, oparen, dollar2, number, cparen, suffix = m.groups()
        # Only normalize if there were extraneous spaces in the original
        compact = dollar1 + oparen + dollar2 + number + cparen + suffix
        if compact != s:
            return compact
    return cell


def _normalize_financial_rows(rows):
    """Normalize all cells in all rows."""
    return [[_normalize_financial_cell(c) for c in row] for row in rows]


def remove_empty_columns(rows):
    """Remove columns that are empty across all rows."""
    if not rows:
        return rows
    num_cols = max(len(row) for row in rows)
    cols_to_keep = []
    for col_idx in range(num_cols):
        has_any_content = any(
            col_idx < len(row) and row[col_idx].strip().strip(INVISIBLE_CHARS)
            for row in rows
        )
        if has_any_content:
            cols_to_keep.append(col_idx)
    result = [[row[i] if i < len(row) else "" for i in cols_to_keep] for row in rows]
    return result


def is_data_row_header(row):
    """Check if a row from data array is a header/title row that should be skipped."""
    non_empty = [c.strip() for c in row if c.strip()]
    if not non_empty:
        return True  # Empty row - skip

    row_text = " ".join(non_empty)

    # Title rows: "For the Years Ended...", "Unaudited", etc.
    # BUT only if the row has NO numeric data values.  Rows like
    # "Three months ended April 30, | 10 | $273.42 | $2,681" are DATA
    # rows whose first cell happens to contain "months ended" as a
    # label — they must NOT be skipped.
    if re.search(
        r"(years?\s+ended|months?\s+ended|weeks?\s+ended|unaudited|as of)",
        row_text,
        re.I,
    ):
        has_numeric_data = any(
            re.match(
                r"^[+\-]?[\$]?\(?\$?\s*[\d,]+\.?\d*\s*\)?%?$",
                c.strip(),
            )
            for c in non_empty
            if not re.match(r"^(19|20)\d{2}$", c.strip())  # Exclude years
        )
        if not has_numeric_data:
            return True

    # Check if this is a category header row (ALL CAPS words, no numbers)
    # EQUIPMENT, OPERATIONS, FINANCIAL, SERVICES, ELIMINATIONS, CONSOLIDATED
    all_caps_count = sum(1 for c in non_empty if re.match(r"^[A-Z]{2,}$", c))

    if all_caps_count >= 2 and not any(re.search(r"\d", c) for c in non_empty):
        return True

    # Year-only rows: just years like 2025, 2024, 2023
    year_count = sum(1 for c in non_empty if re.match(r"^(19|20)\d{2}$", c))

    if year_count >= 2 and year_count == len(non_empty):
        return True

    # Period rows: "May 1999", "November 1998", "Q1 2024",
    # "September 26, 2025", "Oct 27, 2024", etc.
    # These are date/period headers that should be skipped if they're ALL dates
    period_pattern = (
        r"^(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December|"
        r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|"
        r"Q[1-4]|H[12])"
        r"[\s.,]*(?:\d{1,2}[\s,]*)?\d{4}$"
    )
    period_count = sum(1 for c in non_empty if re.match(period_pattern, c, re.I))

    return bool(period_count >= 2 and period_count == len(non_empty))


def _convert_image_to_html(img, base_url: str = "") -> str:
    """Convert an img element to HTML with size preservation.

    Uses HTML <img> tag when size information is present to preserve
    consistent rendering of checkmarks and icons.
    """
    src = img.get("src", "")
    alt = img.get("alt", "Image")
    if not src:
        return ""

    # Resolve relative URLs
    if base_url and not str(src).startswith(("http://", "https://", "data:")):
        src = urljoin(base_url, str(src))

    # Check for size information in style attribute
    style = img.get("style", "")
    width = None
    height = None

    if style:
        # Parse width and height from style like "width:0.0950528in;height:0.0894847in"
        width_match = re.search(r"width:\s*([0-9.]+(?:in|px|em|pt|%))", style)
        height_match = re.search(r"height:\s*([0-9.]+(?:in|px|em|pt|%))", style)
        if width_match:
            width = width_match.group(1)
        if height_match:
            height = height_match.group(1)

    # Also check for explicit width/height attributes
    if not width and img.get("width"):
        width = img.get("width")
        if not any(c.isalpha() for c in str(width)):
            width = f"{width}px"
    if not height and img.get("height"):
        height = img.get("height")
        if not any(c.isalpha() for c in str(height)):
            height = f"{height}px"

    # If we have size info, use HTML img tag to preserve it
    if width or height:
        style_parts = []
        if width:
            style_parts.append(f"width:{width}")
        if height:
            style_parts.append(f"height:{height}")
        style_str = ";".join(style_parts)
        return f'<img src="{src}" alt="{alt}" style="{style_str}"/>'

    # No size info, use standard markdown
    return f"![{alt}]({src})"


def _count_data_columns(table):
    """Count the number of data columns in a table (from header row with years)."""
    rows = table.find_all("tr")
    for row in rows[:5]:
        cells = row.find_all(["td", "th"])
        non_empty = []
        for cell in cells:
            text = cell.get_text().replace("\u200b", "").replace("\xa0", " ").strip()
            if text:
                non_empty.append(text)
        # Look for rows with multiple years
        year_count = sum(1 for t in non_empty if re.match(r"^(19|20)\d{2}$", t))
        if year_count >= 1:
            return year_count
    return 0


def _is_continuation_table(table, prev_table=None):
    """Check if this table is a continuation of a previous table.

    Returns True if the table's first non-empty row is just a year like "2024" or "2023"
    AND the column count matches the previous table (if provided).

    Also returns True for "headerless continuations": tables that have no header
    rows (no years), start directly with data rows (containing dollar/numeric values),
    have the same expanded column count as prev_table, and are immediate DOM siblings.
    """
    rows = table.find_all("tr")
    is_year_only_start = False
    for row in rows[:3]:  # Check first 3 rows
        cells = row.find_all(["td", "th"])
        non_empty = []
        for cell in cells:
            text = cell.get_text().replace("\u200b", "").replace("\xa0", " ").strip()
            if text:
                non_empty.append(text)
        if not non_empty:
            continue
        # If first non-empty row has just one cell and it's a year
        if len(non_empty) == 1 and re.match(r"^(19|20)\d{2}$", non_empty[0]):
            is_year_only_start = True
            break
        # If has multiple cells but first is a year and rest are empty/whitespace
        break

    if is_year_only_start:
        # Original year-only continuation check
        if prev_table is not None:
            prev_cols = _count_data_columns(prev_table)
            this_cols = _count_data_columns(table)
            if prev_cols > 0 and this_cols > 0 and prev_cols != this_cols:
                return False
        return True

    # ── Headerless continuation detection ──────────────────────────────
    # A table that has NO header rows but matching column structure is
    # likely a page-break continuation of the previous table.
    if prev_table is None:
        return False

    # 1. Check that they are immediate DOM siblings (no significant content between)
    if not _are_immediate_sibling_tables(prev_table, table):
        return False

    # 2. Must have matching expanded column counts
    prev_width = _expanded_col_count(prev_table)
    this_width = _expanded_col_count(table)
    if prev_width == 0 or this_width == 0 or prev_width != this_width:
        return False

    # 3. Must have NO header row (no years or period phrases in the first
    #    non-empty row that would indicate an independent table)
    for row in rows[:3]:
        cells = row.find_all(["td", "th"])
        non_empty = []
        for cell in cells:
            text = cell.get_text().replace("\u200b", "").replace("\xa0", " ").strip()
            if text:
                non_empty.append(text)
        if not non_empty:
            continue
        # If ANY cell is a year or period phrase, it has its own header
        for t in non_empty:
            if re.match(r"^(19|20)\d{2}$", t):
                return False
            if re.search(
                r"(months?\s+ended|year\s+ended|quarter\s+ended|weeks?\s+ended)",
                t,
                re.I,
            ):
                return False
        break

    # 4. At least one of the first several rows must look like a data row
    #    (contains a dollar sign, or 2+ numeric/percentage cells).
    #    This allows section label rows (e.g., "Investment banking fees")
    #    to precede the actual data without blocking detection,
    #    while avoiding false merges on TOC tables (single page-number cells).
    for row in rows[:10]:
        cells = row.find_all(["td", "th"])
        texts = []
        for cell in cells:
            text = cell.get_text().replace("\u200b", "").replace("\xa0", " ").strip()
            if text:
                texts.append(text)
        if not texts:
            continue
        has_dollar = any("$" in t for t in texts)
        if has_dollar:
            return True
        numeric_count = sum(
            1
            for t in texts
            if t not in ("—", "-", "–")
            and re.match(r"^[\$\(\)]?\s*[\d,]+\.?\d*\s*[\)\%]?$", t)
        )
        if numeric_count >= 2:
            return True

    return False


def _are_immediate_sibling_tables(table_a, table_b):
    """Check if two tables are nearby in the DOM with no significant content between.

    Tables may be in different wrapper divs (e.g. page-break divs) — walk
    upward to find the containers, then check siblings between them.
    """
    # Simple case: same parent
    if table_a.parent is table_b.parent:
        node = table_a.next_sibling
        while node is not None and node is not table_b:
            if hasattr(node, "name") and node.name:
                text = node.get_text(strip=True)
                if text and len(text) > 2:
                    return False
            elif isinstance(node, str) and len(node.strip()) > 2:
                return False
            node = node.next_sibling  # type: ignore[assignment]
        return node is table_b

    # Different parents: walk up to find wrapper containers and check
    # that the gap between them contains no significant content.
    # Typical pattern: <div><table17/></div><hr/><div><table18/></div>
    container_a = table_a.parent
    container_b = table_b.parent
    if container_a is None or container_b is None:
        return False
    # Both containers must share the same grandparent
    if container_a.parent is not container_b.parent:
        return False
    # Table must be the last element in its container
    # (no significant content after the table within the div)
    node = table_a.next_sibling
    while node is not None:
        if hasattr(node, "name") and node.name:
            text = node.get_text(strip=True)
            if text and len(text) > 2:
                return False
        elif isinstance(node, str) and len(node.strip()) > 2:
            return False
        node = node.next_sibling  # type: ignore[assignment]
    # Table_b must be the first significant element in its container
    node = table_b.previous_sibling
    while node is not None:
        if hasattr(node, "name") and node.name:
            text = node.get_text(strip=True)
            if text and len(text) > 2:
                return False
        elif isinstance(node, str) and len(node.strip()) > 2:
            return False
        node = node.previous_sibling  # type: ignore[assignment]
    # Check gap between the two containers (page number, hr, etc. are ok)
    node = container_a.next_sibling
    while node is not None and node is not container_b:
        if hasattr(node, "name") and node.name:
            text = node.get_text(strip=True)
            # Allow page numbers, empty divs, <hr> separators
            if node.name == "hr":
                node = node.next_sibling  # type: ignore[assignment]
                continue
            if text and len(text) > 10:
                # Substantial content between containers — not a continuation
                return False
        elif isinstance(node, str) and len(node.strip()) > 10:
            return False
        node = node.next_sibling  # type: ignore[assignment]
    return node is container_b


def _expanded_col_count(table):
    """Get the expanded column count (sum of colspans) of a table's widest row."""
    max_cols = 0
    for row in table.find_all("tr")[:10]:
        cells = row.find_all(["td", "th"])
        total = sum(int(c.get("colspan", 1)) for c in cells)
        max_cols = max(max_cols, total)
    return max_cols


def _merge_continuation_tables(soup):
    """Merge consecutive tables where later ones are continuations."""
    tables = soup.find_all("table", recursive=True)
    tables_to_remove = set()

    i = 0
    while i < len(tables):
        table = tables[i]
        if table in tables_to_remove:
            i += 1
            continue

        # Find consecutive continuation tables.
        # Track last_ref so the proximity check is always between
        # adjacent tables (not base-vs-distant) when chaining
        # across multiple page-break boundaries.
        continuations = []
        j = i + 1
        last_ref = table
        while j < len(tables):
            next_table = tables[j]
            if next_table in tables_to_remove:
                j += 1
                continue
            # Check if next_table immediately follows (no significant content between)
            # and is a continuation table
            if _is_continuation_table(next_table, last_ref):
                continuations.append(next_table)
                last_ref = next_table
                j += 1
            else:
                break

        if continuations:
            # For each continuation, prepend header copies and append to main table
            for cont_table in continuations:
                # Get all rows from continuation table
                cont_rows = cont_table.find_all("tr")
                # Find the main table's tbody or create one
                tbody = table.find("tbody")

                if tbody is None:
                    tbody = table

                # Append continuation rows to main table
                for cont_row in cont_rows:
                    # Clone the row and append
                    tbody.append(cont_row.extract())

                # Mark for removal
                tables_to_remove.add(cont_table)

        i += 1

    # Remove merged tables
    for table in tables_to_remove:
        table.decompose()


def is_header_element(tag) -> bool:
    """Check if element looks like a section header."""
    if tag.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        return True

    # Elements explicitly marked as body text by the reflow engine
    # should never be promoted to headings.
    if tag.get("data-body-text"):
        return False

    # Check for TOC section headers - elements with toc* anchor IDs
    element_id = tag.get("id", "")

    if element_id and element_id.startswith("toc"):
        # Check if it contains bold/styled text indicating a section header
        bold_child = tag.find(["b", "strong"]) or tag.find(
            style=re.compile(r"font-weight:\s*bold", re.IGNORECASE)
        )
        if bold_child:
            text = tag.get_text().strip()

            if text and len(text) < 150:
                return True

    # Check for divs/paragraphs styled as headers (large font-size)
    if tag.name in ["div", "p"]:
        # Positioned layouts (Workiva) nest tables inside styled divs
        # whose font-size or bold spans would otherwise false-positive.
        if tag.find("table"):
            return False

        style = tag.get("style", "")
        # Look for font-size in style attribute
        font_match = re.search(r"font-size:\s*(\d+)(?:pt|px)", style)

        if font_match:
            font_size = int(font_match.group(1))
            # Check if child spans have a SMALLER font size — if so, the
            # container font-size is just a fallback/default (common in
            # position-based layouts) and should NOT trigger header detection.
            child_font = None

            for span in tag.find_all("span", recursive=True):
                s = span.get("style", "")
                cm = re.search(r"font-size:\s*(\d+)(?:pt|px)", s)

                if cm:
                    child_font = int(cm.group(1))
                    break

            effective_font = child_font if child_font is not None else font_size
            # 11pt+ is typically header-sized in SEC filings
            if effective_font >= 11:
                text = tag.get_text().strip()
                # Should be reasonably short and have content
                if text and len(text) < 150:
                    return True

        # Only trigger when the div has no bare text nodes — positioned divs always wrap text in spans.
        has_bare_text = any(
            isinstance(c, NavigableString) and c.strip() for c in tag.children
        )
        if not has_bare_text:
            # Check for <p>/<div> whose only children are <b>/<strong> tags
            non_ws_children = [
                c
                for c in tag.children
                if not (isinstance(c, NavigableString) and not c.strip())
            ]
            all_bold_tags = (
                non_ws_children
                and all(
                    (hasattr(c, "name") and c.name in ("b", "strong"))
                    or (
                        hasattr(c, "name")
                        and c.name == "span"
                        and not c.get_text(strip=True)
                    )
                    for c in non_ws_children
                )
                # At least one child must be <b>/<strong>
                and any(
                    hasattr(c, "name") and c.name in ("b", "strong")
                    for c in non_ws_children
                )
            )
            if all_bold_tags and not tag.find("img"):
                text = tag.get_text().strip()
                if text and len(text) < 100 and re.search(r"[a-zA-Z]", text):
                    return True

            text_spans = [
                s
                for s in tag.find_all("span", recursive=True)
                if any(isinstance(c, NavigableString) and c.strip() for c in s.children)
                and "display:inline-block" not in s.get("style", "").replace(" ", "")
            ]
            if text_spans:
                # Count bold vs total characters across text spans.
                bold_chars = 0
                total_chars = 0

                for s in text_spans:
                    sty = s.get("style", "")
                    is_b = bool(
                        re.search(
                            r"font-weight:\s*(bold|bolder|[6-9]00)",
                            sty,
                            re.I,
                        )
                    )
                    for c in s.children:
                        if isinstance(c, NavigableString) and c.strip():
                            n = len(c.strip())
                            total_chars += n
                            if is_b:
                                bold_chars += n

                mostly_bold = total_chars > 0 and bold_chars / total_chars >= 0.8

                if mostly_bold:
                    text = tag.get_text().strip()

                    if text and len(text) < 80 and re.search(r"[a-zA-Z]", text):
                        return True

    if tag.name in ["b", "strong"]:
        text = tag.get_text().strip()

        if re.match(r"^ITEM\s+\d", text, re.IGNORECASE):
            return True

        if re.match(r"^PART\s+[IVX]+", text, re.IGNORECASE):
            return True

        words = text.split()

        if len(words) >= 2 and len(text) < 80 and text.isupper():
            return True
        # Single uppercase words that look like section titles
        if len(words) == 1 and text.isupper() and len(text) >= 4:
            return True

    return False


def get_header_level(tag) -> int:
    """Determine header level."""
    text = tag.get_text().strip()
    if re.match(r"^PART\s+[IVX]+", text, re.IGNORECASE):
        return 1
    if re.match(r"^ITEM\s+\d", text, re.IGNORECASE):
        return 2
    if tag.name == "h1":
        return 1
    if tag.name == "h2":
        return 2
    if tag.name == "h3":
        return 3

    # Check font-size for styled divs/paragraphs
    if tag.name in ["div", "p"]:
        style = tag.get("style", "")
        font_match = re.search(r"font-size:\s*(\d+)(?:pt|px)", style)
        if font_match:
            font_size = int(font_match.group(1))
            if font_size >= 15:
                return 2  # Large headers (15-16pt)
            if font_size >= 11:
                return 3  # Subsection headers (11-14pt)
    return 3


# ============================================================================
# CONVERT_TABLE HELPER FUNCTIONS (extracted from convert_table)
# ============================================================================


def clean_table_cells(rows):
    """Merge currency symbols and parentheses with values.

    Handles common SEC filing table patterns:
    - $ in one cell, value in next: "$" + "12,211" → "$12,211"
    - Opening paren with value: "(" + "2,257" + ")" → "(2,257)"
    - Split negative with note: "(2,257" + ")(b)" → "(2,257)(b)"
    - Value + trailing note: "7" + "(a)" → "7 (a)"
    """
    cleaned = []
    for row in rows:
        new_row = list(row)

        # Pass 1: Merge $ or ( prefix with following value
        i = 0
        while i < len(new_row):
            cell = new_row[i].strip()
            if cell in ["$", "(", "$(", "($"] and i + 1 < len(new_row):
                for j in range(i + 1, min(i + 4, len(new_row))):
                    next_val = new_row[j].strip()
                    if next_val and next_val not in ["$", ")", "%", ""]:
                        new_row[i] = cell + next_val
                        for k in range(i + 1, j + 1):
                            new_row[k] = ""
                        break
                    if next_val in [")", "%"]:
                        break
            i += 1

        # Pass 2: Merge split negatives like "(2,257" + ")(b)" or "(2,257" + ")"
        # Also handle "(2,257" + close paren in any form
        # And handle "$(171" + ")" patterns (currency + open paren)
        i = 0
        while i < len(new_row):
            cell = new_row[i].strip()
            # Check if cell has an open paren that isn't closed
            # Handles both "(2,257" and "$(171" patterns
            has_open_paren = "(" in cell and not cell.endswith(")")
            if has_open_paren and i + 1 < len(new_row):
                # Look for closing paren in following cells
                for j in range(i + 1, min(i + 3, len(new_row))):
                    next_val = new_row[j].strip()
                    if next_val.startswith(")"):
                        # Merge: "(2,257" + ")(b)" → "(2,257)(b)"
                        new_row[i] = cell + next_val
                        new_row[j] = ""
                        break
                    if next_val == "":
                        continue
                    break
            i += 1

        # Pass 3: Merge value with trailing ), %, pts., footnote markers (*, **)
        # SEC tables often split suffixes into narrow separate columns
        i = 0
        while i < len(new_row):
            cell = new_row[i].strip()
            if cell and i + 1 < len(new_row):
                for j in range(i + 1, min(i + 4, len(new_row))):
                    next_val = new_row[j].strip()
                    # Match suffix patterns: ), %, )%, %*, )pts., pts., *, **, etc.
                    if next_val and re.match(r"^[)%]*(?:pts\.?)?[*]*$", next_val):
                        new_row[i] = cell + next_val
                        for k in range(i + 1, j + 1):
                            new_row[k] = ""
                        break

                    if next_val and next_val not in ["", " "]:
                        break

            i += 1

        # Pass 4: Merge numeric value with following note like "(a)", "(b)"
        # Pattern: "7" + "(a)" → "7 (a)" or "5,754" + "(a)" → "5,754 (a)"
        i = 0

        while i < len(new_row):
            cell = new_row[i].strip()
            # Check if cell is a numeric value
            if (
                cell
                and re.match(r"^[\d,.$()-]+$", cell.replace(" ", ""))
                and i + 1 < len(new_row)
            ):
                next_val = new_row[i + 1].strip()
                # Check if next cell is a note reference like "(a)", "(b)"
                if next_val and re.match(r"^\([a-z]\)$", next_val):
                    new_row[i] = cell + " " + next_val
                    new_row[i + 1] = ""
            i += 1

        new_row = [c.strip() for c in new_row]
        cleaned.append(new_row)

    return cleaned


def merge_split_rows(rows, rows_with_colspan):
    """Merge consecutive rows that are continuations of split text."""
    merged_data = []
    merged_colspan = []
    i = 0
    while i < len(rows):
        row = rows[i]
        row_cs = rows_with_colspan[i] if i < len(rows_with_colspan) else []
        row_text = " ".join(c.strip() for c in row if c.strip())

        # ── New: label-continuation merge ──────────────────────────────────
        # Detect rows whose label cell (col 0) has text but all other cells
        # are empty, AND the next row's label starts with a lowercase word
        # (i.e. it is a sentence continuation, e.g.
        #   Row A: "Level 3 assets for which we do not"
        #   Row B: "bear economic exposure (7)" | (14,437) | …
        # → Merge to: "Level 3 assets for which we do not bear economic exposure (7)"
        # and take the data values from Row B.
        non_empty_cols = [j for j, c in enumerate(row) if c.strip()]
        if len(non_empty_cols) == 1 and non_empty_cols[0] == 0 and i + 1 < len(rows):
            next_row = rows[i + 1]
            next_label = next_row[0].strip() if next_row else ""
            # Continuation: next label starts with a lowercase letter
            if next_label and next_label[0].islower():
                label_a = row[0].strip()
                merged_label = label_a + " " + next_label
                # Build merged row: combined label, then data columns from next row
                new_row = [merged_label] + list(next_row[1:])
                next_cs = (
                    rows_with_colspan[i + 1] if i + 1 < len(rows_with_colspan) else []
                )
                merged_data.append(new_row)
                merged_colspan.append(next_cs)
                i += 2
                continue
        # ───────────────────────────────────────────────────────────────────

        # Check if this row starts an incomplete parenthetical
        # Pattern: starts with ( but doesn't end with )
        # BUT only if the first non-empty cell itself has an unbalanced paren.
        # e.g., "(in millions, except per" is incomplete → merge with "share amounts)"
        # but "(in millions)" is complete → do NOT merge even if other cells follow.
        # Also "(Benefit from) provision for taxes" has balanced parens even
        # though it doesn't end with ")" — still complete, don't merge.
        if row_text.startswith("(") and not row_text.endswith(")"):
            # Check if the first non-empty cell has balanced parentheses
            first_cell = ""
            for c in row:
                if c.strip():
                    first_cell = c.strip()
                    break
            first_cell_balanced = first_cell.count("(") == first_cell.count(")")
            if first_cell_balanced:
                # First cell has balanced parens like "(in millions)" or
                # "(Benefit from) provision for income taxes" —
                # don't try to merge with subsequent rows
                merged_data.append(row)
                merged_colspan.append(row_cs)
                i += 1
                continue

            # If non-label columns have content, this is a header row
            # where the descriptor sits at col 0 alongside date/year
            # columns.  Don't merge — the unbalanced paren is just the
            # descriptor wrapping across the HTML row, and the data in
            # other columns must be preserved.
            non_label_content = any(c.strip() for c in row[1:])
            if non_label_content:
                merged_data.append(row)
                merged_colspan.append(row_cs)
                i += 1
                continue

            # Look ahead for continuation
            merged_text = row_text
            j = i + 1
            while j < len(rows):
                next_row = rows[j]
                next_text = " ".join(c.strip() for c in next_row if c.strip())
                # Check if next row is continuation (ends with ) or has amounts/share text)
                if next_text and (
                    next_text.endswith(")")
                    or "amount" in next_text.lower()
                    or "share" in next_text.lower()
                    or next_text.startswith("and ")
                ):
                    merged_text += " " + next_text
                    j += 1
                    if next_text.endswith(")"):
                        break
                else:
                    break

            if j > i + 1:
                # We merged rows - create single row with combined text
                new_row = [merged_text] + [""] * (len(row) - 1)
                merged_data.append(new_row)
                # For colspan, just use first row's structure
                merged_colspan.append(row_cs)
                i = j
                continue

        merged_data.append(row)
        merged_colspan.append(row_cs)
        i += 1

    return merged_data, merged_colspan


def merge_split_cells(rows):
    """Merge cells that contain parts of the same value.

    IMPORTANT: When merging, we add an empty placeholder to maintain column
    alignment across all rows. Otherwise, rows with merged cells would have
    fewer columns than rows without merges, causing misalignment.
    """
    result = []
    for row in rows:
        merged_row = []
        i = 0
        while i < len(row):
            cell = row[i]
            cell_stripped = cell.strip()

            # Look ahead to see if next cell should be merged
            if i + 1 < len(row):
                next_cell = row[i + 1].strip()

                # Case 1: Cell ends with "(" and next cell is just ")"
                # e.g., "(306" + ")" → "(306)"
                if cell_stripped.endswith("(") and next_cell == ")":
                    merged_row.append(cell_stripped + ")")
                    merged_row.append("")  # Placeholder to maintain column count
                    i += 2
                    continue

                # Case 2: Cell is a number and next cell is just a closing paren
                # e.g., "(306" in cell, ")" in next cell for alignment
                # This handles negative numbers where open paren is with number
                if re.match(r"^\([\d,\.]+$", cell_stripped) and next_cell == ")":
                    merged_row.append(cell_stripped + ")")
                    merged_row.append("")  # Placeholder to maintain column count
                    i += 2
                    continue

                # Case 3: Cell is a number and next cell is a footnote marker
                # e.g., "2,264" + "(1)" → "2,264 (1)"
                # Only merge footnotes with 1-2 digits; 3+ digits like
                # "(193)" are negative financial values, not footnotes.
                if re.match(r"^[\$]?[\d,\.]+$", cell_stripped) and re.match(
                    r"^\(\d{1,2}\)$", next_cell
                ):
                    merged_row.append(cell_stripped + " " + next_cell)
                    merged_row.append("")  # Placeholder to maintain column count
                    i += 2
                    continue

                # Case 4: Cell is a number and a nearby cell is "%" or "pts"
                # SEC tables split "22%" across cells: "22"[cs=2] + "%"[cs=1]
                # After colspan expansion this becomes: "22", "", "%"
                # Also handles: "(1.2)" + "" + "pts" → "(1.2)pts"
                if re.match(r"^[\(\)]?[\d,\.]+[\)]?$", cell_stripped):
                    # Look for "%" or "pts" up to 2 cells ahead (skipping empties)
                    suffix_offset = None
                    for look in range(1, min(3, len(row) - i)):
                        look_cell = row[i + look].strip()
                        if look_cell in ("%", "pts"):
                            suffix_offset = look
                            break
                        if look_cell != "":
                            break  # Non-empty, non-suffix cell - stop

                    if suffix_offset is not None:
                        suffix = row[i + suffix_offset].strip()
                        merged_row.append(cell_stripped + suffix)
                        # Add empty placeholders for all consumed cells
                        for _ in range(suffix_offset):
                            merged_row.append("")
                        i += suffix_offset + 1
                        continue

            merged_row.append(cell)
            i += 1

        result.append(merged_row)
    return result


def collapse_repeated_headers(rows):
    """Collapse adjacent duplicate header cells from colspan expansion.

    When header cells have colspan>1, they get expanded to multiple cells
    with the same text. Data cells in those spans typically only fill one
    position. After remove_empty_columns, we may have:
      Header: ["Name", "Fiscal Year", "", "Salary", "", "Bonus", ...]
      Data:   ["Ellison", "", "2025", "", "950,000", "", ...]

    This function collapses repeated adjacent headers and shifts data to align:
      Header: ["Name", "Fiscal Year", "Salary", "Bonus", ...]
      Data:   ["Ellison", "2025", "950,000", ...]
    """
    if not rows or len(rows) < 2:
        return rows

    header = rows[0]
    if len(header) < 2:
        return rows

    # Identify positions to collapse: where header[i] == header[i-1] and both non-empty
    # OR where header[i] is empty but header[i-1] is not (empty trailing from colspan)
    cols_to_remove = set()
    for i in range(1, len(header)):
        prev = header[i - 1].strip() if header[i - 1] else ""
        curr = header[i].strip() if header[i] else ""

        # If current is duplicate of previous OR empty with non-empty prev
        # AND the data rows mostly have content in current (not prev)
        if prev and (curr == prev or not curr):
            # Check if data rows have content in THIS column vs PREV column
            # If data is in current column, keep current and remove previous
            # If data is in previous column, remove current
            prev_has_data = any(
                i - 1 < len(row) and row[i - 1].strip() for row in rows[1:]
            )
            curr_has_data = any(i < len(row) and row[i].strip() for row in rows[1:])

            if curr_has_data and not prev_has_data:
                # Data is in current column, remove the previous header duplicate
                # and copy header text to current
                header[i] = prev  # Copy header to data position
                cols_to_remove.add(i - 1)
            elif not curr_has_data and prev_has_data:
                # Data is in previous column, just remove current empty
                cols_to_remove.add(i)
            elif not curr_has_data and not prev_has_data:
                # Neither has data, remove the empty trailing
                if not curr:
                    cols_to_remove.add(i)
            elif curr_has_data and prev_has_data and not curr:
                # Both have data, but header is only in prev (curr is empty).
                # Check if data is complementary: no row has data in BOTH columns.
                # This happens with $ prefix columns in SEC tables where dollar rows
                # put merged $+value at a different position than non-dollar rows.
                is_complementary = True
                for row in rows[1:]:
                    p = row[i - 1].strip() if i - 1 < len(row) else ""
                    c = row[i].strip() if i < len(row) else ""
                    if p and c:
                        is_complementary = False
                        break
                if is_complementary:
                    # Merge: move curr's data into prev's empty slots, remove curr
                    for row in rows[1:]:
                        c = row[i].strip() if i < len(row) else ""
                        p = row[i - 1].strip() if i - 1 < len(row) else ""
                        if c and not p:
                            row[i - 1] = row[i]
                    cols_to_remove.add(i)

    if not cols_to_remove:
        # Still check for trailing empty columns
        pass

    # Second pass: detect complementary adjacent columns caused by
    # $ prefix merging offset. When $ is in a separate cell, the merged
    # $+value lands at a different expanded position than non-dollar values.
    # Result: adjacent columns with complementary data (never both non-empty
    # in the same row). Merge the smaller into the larger regardless of
    # whether rows[0] has header text.
    for i in range(1, len(header)):
        if i in cols_to_remove or (i - 1) in cols_to_remove:
            continue  # Already handled

        # Check if columns i-1 and i are strictly complementary across ALL rows
        is_complementary = True
        col_prev_count = 0
        col_curr_count = 0
        for row in rows:
            p = row[i - 1].strip() if i - 1 < len(row) else ""
            c = row[i].strip() if i < len(row) else ""
            if p and c:
                is_complementary = False
                break
            if p:
                col_prev_count += 1
            if c:
                col_curr_count += 1

        if not is_complementary:
            continue
        if col_curr_count == 0:
            continue  # col i is fully empty, remove_empty_columns handles it

        # Merge smaller into larger (by count of non-empty rows)
        if col_prev_count >= col_curr_count:
            # Merge col i data into col i-1
            for row in rows:
                c = row[i].strip() if i < len(row) else ""
                p = row[i - 1].strip() if i - 1 < len(row) else ""
                if c and not p:
                    row[i - 1] = row[i]
            cols_to_remove.add(i)
        else:
            # Merge col i-1 data into col i
            for row in rows:
                p = row[i - 1].strip() if i - 1 < len(row) else ""
                c = row[i].strip() if i < len(row) else ""
                if p and not c:
                    row[i] = row[i - 1]
            cols_to_remove.add(i - 1)

    # Also remove trailing empty columns (both header and all data empty)
    num_cols = len(header)
    for col_idx in range(num_cols - 1, -1, -1):
        header_empty = not (header[col_idx].strip() if col_idx < len(header) else "")
        data_empty = all(
            not (row[col_idx].strip() if col_idx < len(row) else "") for row in rows[1:]
        )
        if header_empty and data_empty:
            cols_to_remove.add(col_idx)
        else:
            break  # Stop at first non-empty column from the right

    if not cols_to_remove:
        return rows

    # Rebuild all rows without the collapsed columns
    cols_to_keep = [i for i in range(len(header)) if i not in cols_to_remove]
    result = []
    for row in rows:
        new_row = [row[i] if i < len(row) else "" for i in cols_to_keep]
        result.append(new_row)

    return result


def parse_row_semantic(row, num_expected_cols=0):
    """Parse a row into (label, values) like non_xbrl_parser does."""
    label = None
    values = []
    additional_text = []  # Text that might be values if no numeric values found

    for cell in row:
        c = cell.strip()

        if not c or c == "$":
            continue

        # Em dashes represent "not applicable" - they're values
        # Handle plain dashes AND dollar+dash like "$—" or "$ —" (spaced)
        if c in ("—", "–", "-") and len(c) == 1 or re.match(r"^\$\s*[—–\-]$", c):
            values.append(c)
        # Check if this is a number (with optional $ prefix, commas, parens for negative)

        elif re.match(
            r"^[+\-]?[\$]?\s*\(?[\$]?\s*\d[\d,]*\.?\d*\s*\)?\s*%?(?:pts\.?)?\s*\*{0,2}\s*(\(\d+\)|\([a-z]\))?$",
            c.replace(",", ""),
        ):
            # It's a number (possibly with footnote) - it's a value
            values.append(c)
        elif label is None:
            label = c
        else:
            # Additional text - might be a text value (like credit ratings)
            # Keep it separate so we can decide later
            additional_text.append(c)

    # If we found no numeric values but have additional text, and we expect columns,
    # treat the additional text as values (e.g., credit ratings like "P-1", "A1")
    if not values and additional_text and num_expected_cols > 0:
        # Use additional text as values (up to expected count)
        values = additional_text[:num_expected_cols]
    elif not values and additional_text:
        # No expected columns info - append to label as before
        label = (label or "") + " " + " ".join(additional_text)
    elif (
        values
        and additional_text
        and len(values) < num_expected_cols
        and num_expected_cols > 0
    ):
        # We have some numeric values but fewer than expected. Fill remaining
        # slots with extra text items — e.g., a "Valuation Technique" text
        # column that appears alongside a numeric "Fair Value" column.
        needed = num_expected_cols - len(values)
        values.extend(additional_text[:needed])

    # If we have values but no label, it's likely a total row
    # Use "Total" as the label if values look like currency totals
    if values and not label:
        # Check if values contain dollar amounts (start with $ or have commas)
        has_currency = any(
            v.startswith("$") or re.match(r"^\(?\d{1,3}(,\d{3})+", v) for v in values
        )
        if has_currency:
            label = "Total"

    return label, values


def detect_and_merge_multiindex_headers(data_rows):
    """Detect and merge multi-index column headers from data rows.

    Returns (header_rows, data_start_index, num_value_cols) where:
        header_rows: list of COMPRESSED header rows [label_col, val1, val2, ...]
        data_start_index: index into data_rows where actual data begins
        num_value_cols: number of value columns (for data extraction)
    """
    if not data_rows or len(data_rows) < 3:
        return None, 0, 0

    def is_year(t):
        # Strip trailing footnote markers like *, **, †, ‡, §
        t_clean = re.sub(r"[*†‡§+]+$", "", t.strip())
        return bool(re.match(r"^(19|20)\d{2}$", t_clean))

    def is_all_caps_word(t):
        t = t.strip()
        return bool(re.match(r"^[A-Z]{2,}$", t)) and len(t) > 1

    def is_numeric(t):
        t = t.strip()
        return bool(re.match(r"^[\$]?\s*[\(\)]?\s*[\d,]+\.?\d*\s*[\)\%]?$", t)) and any(
            c.isdigit() for c in t
        )

    def row_has_years(row):
        non_empty = [c.strip() for c in row if c.strip()]
        year_count = sum(1 for c in non_empty if is_year(c))
        return year_count >= 3  # At least 3 years

    def row_is_all_caps_categories(row):
        non_empty = [c.strip() for c in row if c.strip()]
        if len(non_empty) < 2:
            return False
        caps_count = sum(1 for c in non_empty if is_all_caps_word(c))
        return caps_count >= 2 and caps_count >= len(non_empty) * 0.5

    def row_has_data(row):
        return any(is_numeric(c) for c in row)

    def row_is_title(row):
        non_empty = [c.strip() for c in row if c.strip()]

        if not non_empty:
            return True

        row_text = " ".join(non_empty)

        return bool(
            re.search(
                r"(years?\s+ended|months?\s+ended|weeks?\s+ended|unaudited|as\s+of|income\s+statement|balance\s+sheet|statement\s+of)",
                row_text,
                re.I,
            )
        )

    # Scan for header structure
    category_rows_data = []  # List of (row_idx, [cat_texts])
    year_row_idx = None
    years_list = []  # Actual year values in order
    data_start = 0

    for i, row in enumerate(data_rows):
        # Check for year row FIRST (before data check, since years look numeric)
        if row_has_years(row):
            year_row_idx = i
            years_list = [c.strip() for c in row if c.strip() and is_year(c.strip())]
            data_start = i + 1
            continue  # Keep scanning to find where data actually starts

        if row_has_data(row):
            data_start = i
            break

        if row_is_title(row):
            continue

        if row_is_all_caps_categories(row):
            # Extract category texts
            cats = [c.strip() for c in row if c.strip() and is_all_caps_word(c.strip())]
            category_rows_data.append((i, cats))

    if year_row_idx is None or not years_list:
        return None, 0, 0

    num_years = len(years_list)

    # Merge category rows vertically
    # EQUIPMENT + OPERATIONS = "EQUIPMENT OPERATIONS"
    # FINANCIAL + SERVICES = "FINANCIAL SERVICES"
    # Build categories by position (first row gives base, subsequent rows add)
    if category_rows_data:
        # Use max categories from any row
        max_cats = max(len(cats) for _, cats in category_rows_data)
        merged_categories = [""] * max_cats

        for _, cats in category_rows_data:
            for j, cat in enumerate(cats):
                if j < len(merged_categories):
                    if merged_categories[j]:
                        merged_categories[j] += " " + cat
                    else:
                        merged_categories[j] = cat
                else:
                    merged_categories.append(cat)

        num_categories = len(merged_categories)
    else:
        # No ALL CAPS categories found - return None to use fallback
        # which can detect Title Case categories like "Pensions", "OPEB"
        # via colspan analysis in extract_periods_from_rows
        return None, 0, 0

    # Calculate years per category
    years_per_cat = num_years // num_categories
    if years_per_cat == 0:
        years_per_cat = 1

    # Build COMPRESSED headers
    # Format: ["", "CAT1", "", "", "CAT2", "", "", ...]  (category in first cell of span)
    # Format: ["", "2025", "2024", "2023", "2025", "2024", "2023", ...]

    cat_row = [""]  # Label column
    year_row = [""]  # Label column

    year_idx = 0
    for cat in merged_categories:
        # Category name in first cell
        cat_row.append(cat)
        # Empty cells for remaining years under this category
        for _ in range(years_per_cat - 1):
            cat_row.append("")

        # Years for this category
        for _ in range(years_per_cat):
            if year_idx < num_years:
                year_row.append(years_list[year_idx])
                year_idx += 1
            else:
                year_row.append("")

    header_rows = [cat_row, year_row]
    num_value_cols = num_categories * years_per_cat

    # Find actual data start
    for i in range(data_start, len(data_rows)):
        row = data_rows[i]
        if row_has_data(row):
            data_start = i
            break
        if (
            not row_is_title(row)
            and not row_is_all_caps_categories(row)
            and not row_has_years(row)
        ):
            data_start = i
            break

    return header_rows, data_start, num_value_cols


def is_equity_statement_table(rows):
    """Detect if this is an equity statement with stacked column headers."""
    if len(rows) < 5:
        return False

    equity_keywords = {
        "stockholders",
        "common",
        "treasury",
        "retained",
        "accumulated",
        "comprehensive",
        "noncontrolling",
        "redeemable",
        "equity",
    }
    keyword_count = 0
    for row in rows[:10]:
        row_text = " ".join(c.strip().lower() for c in row if c.strip())
        for kw in equity_keywords:
            if kw in row_text:
                keyword_count += 1
    return keyword_count >= 4  # Need multiple equity-related headers


def process_equity_statement_table(rows, rows_with_colspan):
    """Process equity statement table with stacked vertical headers.

    Returns (processed_rows, header_count) or (None, 0) if not applicable.
    """
    # Step 1: Find first data row (row with actual numeric values)
    data_start_idx = 0

    for i, row in enumerate(rows):
        non_empty = [c.strip() for c in row if c.strip()]
        if not non_empty:
            continue

        row_text_lower = " ".join(c.lower() for c in non_empty)

        # Check for $ followed by number pattern (indicates data row)
        # Look for actual balance/value data with $ prefix
        has_balance_data = False
        for j, cell in enumerate(row):
            c = cell.strip()
            next_c = row[j + 1].strip() if j + 1 < len(row) else ""

            # Pattern 1: Combined dollar amounts like "$21,789" or "$5,303"
            if (
                (c.startswith("$") and len(c) > 1 and any(ch.isdigit() for ch in c))
                or c == "$"
                and next_c
                and any(ch.isdigit() for ch in next_c)
            ) and "balance" in row_text_lower:
                has_balance_data = True
                break

        if has_balance_data:
            data_start_idx = i
            break

    if data_start_idx == 0 or data_start_idx >= len(rows):
        return None, 0

    # Step 2: Analyze a data row to find the column structure
    # Each logical value column has: possibly spacer + $ cell + number cell
    # Find all columns that directly contain $ + number format
    sample_row = rows[data_start_idx]
    value_positions = []  # (col_index, value_with_$)

    for j, cell in enumerate(sample_row):
        c = cell.strip()
        # Match "$21,789" or "$(24,094)" or "$5,165" patterns
        if c and re.match(r"^[\$][\(\)]?[\d,]+[\)]?$", c):
            value_positions.append(j)

    # If $ and value are in separate cells, find pairs
    if not value_positions:
        for j, cell in enumerate(sample_row[:-1]):
            c = cell.strip()
            next_c = sample_row[j + 1].strip() if j + 1 < len(sample_row) else ""
            # $ in current cell, number in next
            if c == "$" and next_c and re.match(r"^[\(\)]?[\d,]+[\)]?$", next_c):
                value_positions.append(j)  # Use the $ cell position as anchor
            elif c in ["$(", "($"] and next_c and re.match(r"^[\d,]+\)?$", next_c):
                value_positions.append(j)

    num_value_cols = len(value_positions)
    if num_value_cols < 2:
        return None, 0

    # Step 3: Build headers from header rows (rows before data_start_idx)
    # For each value position, find the corresponding header by looking at
    # which header text appears above or near that column

    def is_title_row(row_idx):
        """Identify if a row is a title/descriptor row that should be skipped from headers."""
        if row_idx >= len(rows):
            return False
        row = rows[row_idx]
        non_empty = [c.strip() for c in row if c.strip()]

        if not non_empty:
            return True  # Empty row - skip it

        if len(non_empty) == 1 and row_idx < len(rows_with_colspan):
            # Single non-empty cell - check if it spans most of the row
            # Also check rows_with_colspan for actual colspan info
            cs_row = rows_with_colspan[row_idx]
            cs_non_empty = [(t, cs) for t, cs in cs_row if t.strip()]

            if len(cs_non_empty) == 1:
                _, colspan = cs_non_empty[0]
                total_span = sum(cs for _, cs in cs_row)

                if colspan >= total_span * 0.4:  # Title spans 40%+ of table
                    return True

        return False

    # Filter header rows to exclude title rows
    header_rows = [i for i in range(data_start_idx) if not is_title_row(i)]
    # Build column boundaries: each value column "owns" cells from its position
    # back to the previous value's position (or start of row)
    col_boundaries = []

    for idx, v_pos in enumerate(value_positions):
        start = (
            0 if idx == 0 else value_positions[idx - 1] + 2
        )  # Skip to after previous value
        col_boundaries.append((start, v_pos + 1))  # inclusive range

    # First, find all unique header column positions from header rows
    header_positions: dict = {}  # col_idx -> [text1, text2, ...]

    for row_idx in header_rows:
        row = rows[row_idx]
        for col_idx, cell in enumerate(row):
            text = cell.strip()
            if text and not re.match(r"^[\$\d,\.\(\)]+$", text):
                if col_idx not in header_positions:
                    header_positions[col_idx] = []
                if text not in header_positions[col_idx]:
                    header_positions[col_idx].append(text)

    # Get unique header columns in sorted order (by position)
    sorted_header_cols = sorted(header_positions.keys())
    # Build headers from the stacked text at each position
    stacked_headers = []

    for h_pos in sorted_header_cols:
        parts = header_positions[h_pos]
        header_text = " ".join(parts)
        stacked_headers.append(header_text)

    # Match headers to values by sequence
    # If we have N values and M headers, match them by index
    final_headers = []

    for idx, v_pos in enumerate(value_positions):
        if idx < len(stacked_headers):
            final_headers.append(stacked_headers[idx])
        else:
            final_headers.append(f"Column {idx + 1}")

    # Step 4: Build output table
    result = []

    # Add header row (empty label + column headers)
    result.append([""] + final_headers)

    # Process each data row
    for row in rows[data_start_idx:]:
        # Extract label (first cell, or first non-$ non-empty cell)
        label = ""
        for cell in row[:3]:  # Label is usually in first few cells
            c = cell.strip()
            if (
                c
                and not c.startswith("$")
                and not re.match(r"^\s*[\(\)]?\s*[\d,]+\.?\d*\s*[\)\%]?$", c)
            ) and c not in [
                "$",
                "(",
                ")",
                "%",
                "—",
                "–",
                "-",
            ]:
                label = c
                break

        # Extract values from value positions
        values = []
        for v_pos in value_positions:
            val = ""
            if v_pos < len(row):
                c = row[v_pos].strip()
                # Check if this cell has the complete value ($ + number)
                if c and (c.startswith("$") or re.match(r"^[\(\)]?[\d,]+", c)):
                    val = c
                    # If it's just $, look at next cell
                    if c in ["$", "$(", "($"] and v_pos + 1 < len(row):
                        next_c = row[v_pos + 1].strip()
                        if next_c:
                            val = c + next_c
                elif v_pos + 1 < len(row):
                    # Value might be in next cell
                    next_c = row[v_pos + 1].strip()
                    if next_c and re.match(r"^[\(\)]?[\d,]+", next_c):
                        val = next_c
            values.append(val)

        # Skip rows with no label and no values
        if not label and not any(v.strip() for v in values):
            continue

        result.append([label] + values)

    return result, 1  # 1 header row


def build_column_headers_from_colspan(rows_with_colspan, _year_pos_shift):
    """Build proper multi-index column headers.

    For tables with stacked category headers like:
        Row 0: [Title spanning all columns - SKIP]
        Row 1: "" | "EQUIPMENT" (colspan=8) | "FINANCIAL" (colspan=8) | ...
        Row 2: "" | "OPERATIONS" (colspan=8) | "SERVICES" (colspan=8) | "ELIMINATIONS" | "CONSOLIDATED"
        Row 3: "" | "2025" | "2024" | "2023" | "2025" | "2024" | "2023" | ...

    Output multi-index format:
        Row 1: ["", "EQUIPMENT OPERATIONS", "", "", "FINANCIAL SERVICES", "", "", ...]
        Row 2: ["", "2025", "2024", "2023", "2025", "2024", "2023", ...]

    POSITION-BASED vertical merge: if row N and row N+1 both have text at same
    column position with large colspan, merge them into one category name.
    Category name appears ONLY in the first cell of its span, not repeated.

    Returns (header_layers, header_row_count)

    ``_year_pos_shift`` is a one-element list used as a mutable output
    parameter so the caller can read back the computed shift value.  When
    called outside of ``convert_table`` (e.g. in tests) it may be ``None``; in
    that case a local list is used so the function still works correctly.

    """
    if not rows_with_colspan:
        return None, 0

    # Extract colspan structure and text for each row
    # Structure: list of (text, colspan, start_col) tuples
    parsed_rows = []
    for row in rows_with_colspan:
        parsed = []
        col_pos = 0
        for text, colspan in row:
            stripped_text = text.strip()
            parsed.append((stripped_text, colspan, col_pos))
            col_pos += colspan
        parsed_rows.append(parsed)

    if not parsed_rows:
        return None, 0

    def is_year(t):
        # Strip trailing footnote markers like *, **, †, ‡, §
        t_clean = re.sub(r"[*†‡§+]+$", "", t.strip())
        return bool(re.match(r"^(19|20)\d{2}$", t_clean))

    def is_category_text(t):
        """Check if text looks like a category header (not a year, not data)."""
        if not t or is_year(t):
            return False
        # Remove <br> tags before checking patterns (multi-line headers)
        t_clean = re.sub(r"<[Bb][Rr]\s*/?>", " ", t).strip()
        t_clean = re.sub(r"\s+", " ", t_clean)  # Collapse whitespace
        # Remove trailing footnote markers like *, **, *+, **+
        t_clean = re.sub(r"\s*[\*+]+$", "", t_clean)
        # Remove trailing superscript footnote numbers like "1,2,3" or "4"
        # These come from <sup> tags concatenated with the text
        t_clean = re.sub(r"\s+\d+(?:,\d+)*$", "", t_clean)
        # Also strip footnote digits directly attached to words (no whitespace)
        # e.g., "Net Interest2" → "Net Interest", "All Other3" → "All Other"
        t_clean = re.sub(r"(?<=[A-Za-z])\d+$", "", t_clean)
        if re.match(r"^[\$]?\s*[\(\)]?\s*[\d,]+\.?\d*\s*[\)\%]?$", t_clean):
            return False  # It's data
        # Title Case: "Equipment Operations", "Operating Income/(Loss)"
        # Strip /()\- before checking to avoid catastrophic backtracking
        t_stripped = re.sub(r"[/()\-]", " ", t_clean)
        t_stripped = re.sub(r"\s+", " ", t_stripped).strip()
        # Also prepare a variant with leading symbol prefixes removed
        # so that headers like "% Average rate" or "# of Shares" are
        # recognized after stripping the leading punctuation.
        t_no_prefix = re.sub(r"^[%#$&*~!@^]+\s*", "", t_stripped)
        if (
            re.match(r"^[A-Z][A-Za-z]*(\s+[A-Za-z&]+)*$", t_stripped)
            and len(t_clean) > 2
        ):
            return True
        if (
            t_no_prefix != t_stripped
            and re.match(r"^[A-Z][A-Za-z]*(\s+[A-Za-z&]+)*$", t_no_prefix)
            and len(t_no_prefix) > 2
        ):
            return True
        # ALL CAPS: "EQUIPMENT", "FINANCIAL SERVICES", "LONG-LIVED ASSETS"
        if re.match(r"^[A-Z]{2,}(-[A-Z]+)?(\s+[A-Z]+(-[A-Z]+)?)*$", t_clean):
            return True
        # ALL CAPS with periods/abbreviations: "WTD. AVG. EXERCISE PRICE", "NO. OF SHARES"
        # Pattern: uppercase word (optionally with period) followed by more words
        if (
            re.match(r"^[A-Z]{2,}\.?(\s+[A-Z]{2,}\.?)*(\s+[A-Z]+)*$", t_clean)
            and len(t_clean) > 3
        ):
            return True
        # Abbreviated ALL-CAPS with dots and dashes: "YR.-TO-YR."
        if re.match(r"^[A-Z]{2,}\.(-[A-Z]{2,}\.?)+$", t_clean):
            return True
        # Abbreviations like "U.S.", "NON-U.S.", "U.K." - single letters with periods
        # Pattern: optional prefix (NON-), then letter-period pairs
        if re.match(r"^([A-Z]+-)?[A-Z]\.[A-Z]\.?$", t_clean):
            return True
        # Abbreviations followed by words: "U.S. PLANS", "NON-U.S. PLANS"
        if re.match(r"^([A-Z]+-)?[A-Z]\.[A-Z]\.?(\s+[A-Z]+)+$", t_clean):
            return True
        # Hyphenated categories: "NON-GAAP", "PRE-TAX"
        if re.match(r"^[A-Z]+-[A-Z]+$", t_clean):
            return True
        # Hyphenated words followed by more words: "PPP-QUALIFIED PORTION"
        return bool(re.match(r"^[A-Z]+-[A-Z]+(\s+[A-Z]+)+$", t_clean))

    def is_header_row(parsed):
        """Check if this row is a header row (years or categories)."""

        # Filter truly empty cells and cells with only whitespace/invisible chars
        # Zero-width spaces (\u200b) and similar should be skipped
        def has_visible_content(t):
            # Remove zero-width spaces, zero-width non-joiners, etc.
            cleaned = (
                t.replace("\u200b", "")
                .replace("\u200c", "")
                .replace("\u200d", "")
                .replace("\ufeff", "")
                .strip()
            )
            return bool(cleaned)

        non_empty = [(t, c, s) for t, c, s in parsed if t and has_visible_content(t)]
        if not non_empty:
            return False, False  # empty, not header

        # Check if title row (one text spans >=80%)
        total_span = sum(c for t, c, s in parsed)
        max_span = max((c for t, c, s in non_empty), default=0)
        if max_span >= total_span * 0.8:
            # Don't classify date/year super-headers as title rows — even if a
            # date like "As of November 2007" spans ≥80% of the table width it
            # should still be treated as a year super-header row, not skipped.
            _spanning_text = next((t for t, c, s in non_empty if c == max_span), None)
            _is_date_span = _spanning_text and bool(
                re.search(
                    rf"(?:As\s+of\s+)?(?:{MONTHS_PATTERN}\s+)?(?:\d{{1,2}},?\s*)?(19|20)\d{{2}}\b",
                    _spanning_text,
                    re.I,
                )
            )
            if not _is_date_span:
                return False, True  # title row - skip but count

        # Check for period description rows like "For the Three Months Ended..."
        # These are single-cell descriptions that should be treated as title rows
        if len(non_empty) == 1:
            text, colspan, start = non_empty[0]
            # Period descriptions in first column with phrases like "For the X Months/Weeks/Years Ended"
            if start == 0 and re.search(
                r"for\s+the\s+(\w+\s+)?(months?|weeks?|quarters?|years?|period)\s+ended",
                text,
                re.I,
            ):
                return False, True  # title row - skip but count

            # A single non-empty cell at position 0 that does NOT
            # reference any year or date is a table title / section
            # label (e.g. "Financial performance of JPMorganChase"),
            # NOT a category header.  Category headers appear at
            # start > 0 spanning data columns, typically with multiple
            # cells per row.  Mis-classifying titles as categories
            # breaks the header scan — it causes the scanner to stop
            # at the very next non-header row, never reaching the
            # actual year/period row further down.
            if (
                start == 0
                and not re.search(r"\b(19|20)\d{2}\b", text)
                and not re.search(
                    rf"(months?\s+ended|year\s+ended|weeks?\s+ended"
                    rf"|{MONTHS_PATTERN}\s+\d{{1,2}})",
                    text,
                    re.I,
                )
            ):
                return False, True  # title row - skip but count

        has_year = False
        has_category = False
        has_data = False
        has_label = False  # Line item label (text in col 0/1 with small colspan)

        for t, colspan, start in non_empty:
            if t.startswith("(") and ("million" in t.lower() or "except" in t.lower()):
                continue

            # Check for year before checking for numeric data
            if is_year(t):
                has_year = True
            elif re.match(r"^[\$]?\s*[\(\)]?\s*[\d,]+\.?\d*\s*[\)\%]?$", t):
                # At position 0 (label column), a bare small number
                # (1-3 digits with no financial formatting) may be a
                # rendering artifact rather than a data value.
                if start == 0 and re.match(r"^\d{1,3}$", t):
                    continue
                has_data = True
                break
            elif start > 0 and re.search(
                rf"(months?\s+ended|year\s+ended|weeks?\s+ended|quarters?\s+ended"
                rf"|ended\s+{MONTHS_PATTERN}|{MONTHS_PATTERN}\s+\d{{1,2}}\s*,?(?:\s*(?:19|20)\d{{2}})?"
                rf"|(?:As\s+of\s+)?{MONTHS_PATTERN}\s+(19|20)\d{{2}}\b)",
                t,
                re.I,
            ):
                # Catches "Three Months Ended May 31" / "January 26, 2025" / "Ended November"
                # / "November 2007" / "As of November 2007" / "October 31," (bare date fragment)
                # but NOT standalone unit labels like "Months", "Years", "10 Years"
                has_year = True
            elif is_category_text(t) and colspan >= 2:
                # Category headers can have colspan >= 2
                has_category = True
            elif is_category_text(t) and colspan == 1:
                # Category text with colspan=1 can also be a header
                # (e.g., "NUMBER OF SHARES UNDER OPTION" at start > 1)
                if start > 1:
                    has_category = True
            elif start <= 1 and colspan == 1 and len(t) > 3:
                # Text in first column with small colspan = line item label (data row)
                # Unless it's a very short text that could be a spacer
                has_label = True
            elif t.endswith(":"):
                # Section labels like "Assets:", "Liabilities:", "Revenues:" indicate data rows
                has_label = True

        # Data rows always stop header scanning
        if has_data:
            return False, False

        # If has_year or has_category, the label is just a row dimension header (e.g., "Risk Categories")
        if has_label and not (has_year or has_category):
            return False, False

        # Staircase top-row: all non-empty cells in data columns (start > 0) with
        # uniform small colspan and no financial data.  Catches maturity-range
        # labels like "0 - 6", "6 - 12", "10 Years" that fail every single-cell
        # test but are clearly split column headers when they appear together with
        # equal colspan (e.g., all colspan=2 spanning gutter+value pairs).
        if not has_year and not has_category and not has_label:
            data_col_cells = [(t, c, s) for t, c, s in non_empty if s > 0]
            if (
                len(data_col_cells) >= 2
                and len({c for _, c, _ in data_col_cells}) == 1  # uniform colspan
                and data_col_cells[0][1] >= 2  # not colspan-1 label cells
            ):
                has_category = True

        return (has_year or has_category), False

    # First pass: identify all header rows and classify them
    header_info: list = []  # (row_idx, parsed, is_year_row, is_category_row)
    header_row_count = 0

    def has_visible_text(t):
        cleaned = (
            t.replace("\u200b", "")
            .replace("\u200c", "")
            .replace("\u200d", "")
            .replace("\ufeff", "")
            .strip()
        )
        return bool(cleaned)

    title_period_texts = []  # Track period titles for super-header use

    for row_idx, parsed in enumerate(parsed_rows):
        is_header, is_title = is_header_row(parsed)
        # Check if this row is completely empty (all cells empty after stripping)
        non_empty_cells = [(t, c, s) for t, c, s in parsed if has_visible_text(t)]

        if not non_empty_cells:
            # Empty row - skip it but count it toward header_row_count
            header_row_count = row_idx + 1
            continue

        if is_title:
            # Save period/date titles for potential use as super-headers
            for _tt, _tc, _ts in parsed:
                if (
                    _tt
                    and has_visible_text(_tt)
                    and re.search(
                        rf"(months?|quarters?|years?|weeks?|period)\s+ended|ended\s+{MONTHS_PATTERN}|{MONTHS_PATTERN}\s+\d{{1,2}}",
                        _tt,
                        re.I,
                    )
                ):
                    title_period_texts.append(_tt)
            header_row_count = row_idx + 1
            continue

        if not is_header:
            # Before breaking, check if this is a pre-header title row.
            # SEC filings often have company names and statement titles
            # in single cells at position 0 without large colspan.
            # These should be skipped before any real headers are found.
            if not header_info:  # No headers found yet
                non_empty_check = [
                    (t, c, s) for t, c, s in parsed if has_visible_text(t)
                ]
                if len(non_empty_check) <= 1 and (
                    not non_empty_check
                    or non_empty_check[0][2] == 0
                    or non_empty_check[0][1]
                    > 2  # Large colspan = title at any position
                ):
                    # Single text at position 0 (or empty) or with large colspan before headers → title row
                    header_row_count = row_idx + 1
                    continue
            break  # Hit actual data row

        # After year rows have been found, a single-cell row at position 0
        # is a section header (e.g., "Assets", "Liabilities"), not a column
        # category. Stop scanning for headers.
        if header_info:
            has_year_already = any(is_yr for _, _, is_yr, _ in header_info)
            if (
                has_year_already
                and len(non_empty_cells) == 1
                and non_empty_cells[0][2] == 0
            ):
                break

        # Classify: year row or category row?
        non_empty = [(t, c, s) for t, c, s in parsed if has_visible_text(t)]

        # Check if this row has large-colspan period phrases (super-headers)
        # E.g., "Three Months Ended May"[cs=7] is a category spanning year columns
        has_large_colspan_period = any(
            colspan > 2
            and re.search(
                rf"(months?|quarters?|years?|weeks?)\s+ended|ended\s+{MONTHS_PATTERN}",
                t,
                re.I,
            )
            for t, colspan, s in non_empty
        )

        has_year = any(
            is_year(t)
            or (
                re.search(rf"(ended|{MONTHS_PATTERN})", t, re.I)
                and colspan <= 2
                and s > 0  # Skip first column (row labels like "AT DECEMBER 31:")
            )
            or (
                # Full dates like "January 26, 2025", "September 26,2025",
                # or "September 26,<br>2025" (with <br> tag) are year indicators
                re.search(
                    rf"({MONTHS_PATTERN})\s+\d{{1,2}},?\s*(19|20)\d{{2}}",
                    re.sub(r"<[Bb][Rr]\s*/?>", " ", t),
                    re.I,
                )
                and s > 0
            )
            or (
                # "Month YYYY" (no day) or "As of Month YYYY" — period super-headers
                # with any colspan (e.g. "As of November 2007" cs=22 spans whole table)
                re.search(
                    rf"(?:As\s+of\s+)?{MONTHS_PATTERN}\s+(19|20)\d{{2}}\b",
                    t,
                    re.I,
                )
                and s > 0
            )
            for t, colspan, s in non_empty
        )
        has_category = any(
            is_category_text(t) and not is_year(t) for t, c, s in non_empty
        )

        # Large-colspan period phrases are treated as categories
        if has_large_colspan_period:
            period_phrases_have_year = any(
                colspan > 2
                and re.search(
                    rf"(months?|quarters?|years?|weeks?)\s+ended|ended\s+{MONTHS_PATTERN}",
                    t,
                    re.I,
                )
                and re.search(
                    r"\b(19|20)\d{2}\b",
                    re.sub(r"<[Bb][Rr]\s*/?>", " ", t),
                )
                for t, colspan, s in non_empty
            )
            if not period_phrases_have_year:
                has_year = False
            has_category = True

        header_info.append((row_idx, parsed, has_year, has_category))
        header_row_count = row_idx + 1

    if not header_info:
        return None, 0

    # A valid financial table must have at least one data row after
    # the header region, so bail out and let the caller fall back to
    # simple non-financial table processing.
    if header_row_count >= len(parsed_rows):
        return None, 0

    # Separate category rows and year rows
    category_rows = [
        (idx, p) for idx, p, is_yr, is_cat in header_info if is_cat and not is_yr
    ]
    year_rows = [(idx, p) for idx, p, is_yr, is_cat in header_info if is_yr]

    # Extract column headers from year rows
    column_headers_list = []
    column_headers_positions = []

    for row_idx, parsed in year_rows:
        for text, colspan, start in parsed:
            if not text:
                continue

            if start == 0 and not is_year(text):
                continue

            # Skip notes/descriptors in parentheses
            if text.startswith("(") and (
                "million" in text.lower() or "except" in text.lower()
            ):
                continue

            column_headers_list.append(text)
            column_headers_positions.append(start)

    # When the first year header is at position 0 (occupying the label
    # column), it means the year sub-header row lacks a separate label
    # cell — years start from the very first cell.  Data rows DO have
    # a label at position 0, so data values start at a later position.
    # Shift all year header positions right by the label column width
    # (= first category position) to align them with data columns.
    # ``_year_pos_shift`` may be None when the function is called outside
    # of convert_table (e.g. in tests); in that case use a local list.
    if _year_pos_shift is None:
        _year_pos_shift = [0]
    _year_pos_shift[0] = 0
    if column_headers_positions and column_headers_positions[0] == 0 and category_rows:
        # Use first category's start position as the label width
        for _, cat_parsed in category_rows:
            for _ct, _cc, _cs in cat_parsed:
                if _cs > 0:
                    _year_pos_shift[0] = _cs
                    break
            break
        if _year_pos_shift[0] > 0:
            column_headers_positions = [
                p + _year_pos_shift[0] for p in column_headers_positions
            ]

    # Check for stacked date + year header pattern:
    # Row A: "January 26," "October 27," "January 28," (dates with months)
    # Row B: "2025" "2024" "2024" (years)
    # Should combine to: "January 26, 2025", "October 27, 2024", etc.
    # Also handles extra non-month/non-year items at different positions:
    # Row A: "January 26" "January 28" "%"
    # Row B: "2025" "2024" "Change"
    # -> "January 26, 2025" "January 28, 2024" "% Change"
    if len(year_rows) >= 2:

        def _row_headers(parsed_row):
            result = []
            for text, _, start in parsed_row:
                t = text.strip()
                if not t:
                    continue
                # Skip first-column labels but allow years at position 0
                if start == 0 and not is_year(t):
                    continue
                if t.startswith("(") and (
                    "million" in t.lower() or "except" in t.lower()
                ):
                    continue
                result.append((t, start))
            return result

        def _try_position_merge(hdrs_a, hdrs_b):
            """Try to merge two header rows by matching positions.
            Returns (merged_texts, merged_positions) sorted by position,
            or (None, None) if no month+year merges found.
            """
            # Build position maps
            pos_a = {s: t for t, s in hdrs_a}
            pos_b = {s: t for t, s in hdrs_b}
            all_positions = sorted(set(pos_a.keys()) | set(pos_b.keys()))

            merged = []
            merged_pos = []
            month_year_merges = 0
            for pos in all_positions:
                text_a = pos_a.get(pos)
                text_b = pos_b.get(pos)
                if text_a and text_b:
                    a_is_month = bool(re.search(MONTHS_PATTERN, text_a, re.I))
                    b_is_year = is_year(text_b)
                    a_is_year = is_year(text_a)
                    b_is_month = bool(re.search(MONTHS_PATTERN, text_b, re.I))
                    if a_is_month and b_is_year:
                        merged.append(f"{text_a.rstrip(',').strip()}, {text_b}")
                        month_year_merges += 1
                    elif a_is_year and b_is_month:
                        merged.append(f"{text_b.rstrip(',').strip()}, {text_a}")
                        month_year_merges += 1
                    else:
                        # Generic vertical merge (e.g., "%" + "Change" -> "% Change")
                        merged.append(f"{text_a} {text_b}".strip())
                elif text_a:
                    merged.append(text_a)
                elif text_b:
                    merged.append(text_b)
                merged_pos.append(pos)

            if month_year_merges > 0:
                return merged, merged_pos
            return None, None

        for i in range(len(year_rows)):
            for j in range(i + 1, len(year_rows)):
                _, row_a = year_rows[i]
                _, row_b = year_rows[j]
                hdrs_a = _row_headers(row_a)
                hdrs_b = _row_headers(row_b)

                if len(hdrs_a) == 0 or len(hdrs_b) == 0:
                    continue

                # Check that at least one row has months and at least one has years
                a_has_months = any(
                    re.search(MONTHS_PATTERN, h, re.I) for h, _ in hdrs_a
                )
                b_has_months = any(
                    re.search(MONTHS_PATTERN, h, re.I) for h, _ in hdrs_b
                )
                a_has_years = any(is_year(h) for h, _ in hdrs_a)
                b_has_years = any(is_year(h) for h, _ in hdrs_b)

                if (a_has_months and b_has_years) or (a_has_years and b_has_months):
                    result, result_positions = _try_position_merge(hdrs_a, hdrs_b)
                    if result:
                        column_headers_list = result
                        column_headers_positions = result_positions
                        break
            else:
                continue
            break

    if not column_headers_list:
        # No year row headers found
        # Check for date-super-header pattern: one category row is a single
        # large-colspan date/period phrase spanning everything, and remaining
        # category rows have vertically-stacked text sub-column headers.
        # Example:
        #   Row 0: "Three Months Ended January 26, 2025" cs=11  (super-header)
        #   Row 1: "Retail Notes" cs=2, "Revolving" cs=2
        #   Row 2: "& Financing" cs=2, "Charge" cs=2, "Wholesale" cs=2
        #   Row 3: "Leases" cs=2, "Accounts" cs=2, "Receivables" cs=2, "Total" cs=2
        #   → merge sub-columns: "Retail Notes & Financing Leases", etc.
        if len(category_rows) >= 2:
            _, first_parsed = category_rows[0]
            first_ne = [(t, c, s) for t, c, s in first_parsed if has_visible_text(t)]
            is_date_super = False
            super_text = ""
            if len(first_ne) == 1:
                super_text, super_cs, _ = first_ne[0]
                if super_cs > 2 and re.search(
                    rf"(months?|quarters?|years?|weeks?|period)\s+ended|ended\s+{MONTHS_PATTERN}|{MONTHS_PATTERN}\s+\d{{1,2}}",
                    super_text,
                    re.I,
                ):
                    is_date_super = True

            if is_date_super:
                # Vertically merge remaining category rows by position
                pos_texts: dict = {}  # col_pos -> [text1, text2, ...]
                for cat_idx in range(1, len(category_rows)):
                    _, sub_parsed = category_rows[cat_idx]
                    for sub_text, _, sub_start in sub_parsed:
                        if (
                            not sub_text
                            or not has_visible_text(sub_text)
                            or sub_start == 0
                        ):
                            continue
                        if sub_start not in pos_texts:
                            pos_texts[sub_start] = []
                        pos_texts[sub_start].append(sub_text)

                if pos_texts:
                    sorted_pos = sorted(pos_texts.keys())
                    merged_sub_headers = [" ".join(pos_texts[p]) for p in sorted_pos]
                    n_cols = len(merged_sub_headers)
                    # Build 2-layer header
                    super_row = ["", super_text]
                    for _ in range(n_cols - 1):
                        super_row.append("")
                    sub_row = [""] + merged_sub_headers
                    header_layers = [super_row, sub_row]
                    return header_layers, header_row_count

        # Fallback: check if category rows can serve as column headers (flat header table)
        # Merge by POSITION across all category rows.  When two rows
        # have text at the same position, the WIDER row (more total
        # columns) wins — it placed its header at an explicit position
        # in a full-width row.  The displaced text from the shorter
        # row is appended at the end (first uncovered position).
        # Example (MS 10-Q):
        #   R2 (18 cols): Net Interest2@9, All Other3@12
        #   R3 (12 cols): Trading@3, Fees1@6, Total@9
        #   → pos 9 conflict: R2 wins (wider), "Total" displaced to end
        #   → result: Trading | Fees1 | Net Interest2 | All Other3 | Total
        if category_rows:
            first_col_label = ""
            for _, cat_parsed in category_rows:
                for text, colspan, start in cat_parsed:
                    if start == 0 and text and not first_col_label:
                        first_col_label = text

            # Compute each row's total column span
            row_widths = []
            for _, cat_parsed in category_rows:
                total = sum(cs for _, cs, _ in cat_parsed)
                row_widths.append(total)

            # Build position -> (text, row_width) map.
            # Wider row wins at conflicts.
            pos_map = {}  # pos -> (text, row_width)
            displaced = []  # texts displaced from conflicts
            for cr_idx, (_, cat_parsed) in enumerate(category_rows):
                w = row_widths[cr_idx]
                for text, colspan, start in cat_parsed:
                    if start == 0 or not text:
                        continue
                    if start not in pos_map:
                        pos_map[start] = (text, w)
                    else:
                        existing_text, existing_w = pos_map[start]
                        if w > existing_w:
                            # New row is wider, it wins
                            displaced.append(existing_text)
                            pos_map[start] = (text, w)
                        elif w < existing_w:
                            # Existing row is wider, it keeps the position
                            displaced.append(text)
                        else:
                            # Same width — later row overrides (more specific)
                            displaced.append(existing_text)
                            pos_map[start] = (text, w)

            if pos_map:
                # Collect headers in position order
                final_headers = [pos_map[p][0] for p in sorted(pos_map.keys())]
                # Append displaced texts at the end
                final_headers.extend(displaced)

                n_cols = len(final_headers)
                header_layers = []

                if title_period_texts:
                    super_row = ["", title_period_texts[-1]] + [""] * (n_cols - 1)
                    header_layers.append(super_row)

                header_row = [first_col_label] + final_headers
                header_layers.append(header_row)
                return header_layers, header_row_count

        if not column_headers_list:
            # No year rows. If ≥ 2 category rows form a staircase (first row has
            # all cells in data columns with uniform colspan, like "0 - 6" / "6 - 12"
            # split from "Months" / "Months" below), merge them into one header row.
            if len(category_rows) >= 2:
                first_cat_parsed = category_rows[0][1]
                first_ne = [(t, c, s) for t, c, s in first_cat_parsed if t.strip()]
                first_is_staircase_top = (
                    first_ne
                    and all(s > 0 for _, _, s in first_ne)
                    and len({c for _, c, _ in first_ne}) == 1  # uniform colspan
                    and first_ne[0][1] >= 2  # colspan >= 2, not single-col labels
                )
                if first_is_staircase_top:
                    _sm_rows = []
                    for _, cat_parsed in category_rows:
                        sm: dict = {}
                        for text, colspan, start in cat_parsed:
                            t = (
                                text.replace("\u200b", "")
                                .replace("\u200c", "")
                                .replace("\ufeff", "")
                                .strip()
                            )
                            if t:
                                sm[start] = (t, start + colspan - 1)
                        if sm:
                            _sm_rows.append(sm)
                    if _sm_rows:
                        _leaf_pos = sorted(
                            p
                            for p in set().union(*[set(sm.keys()) for sm in _sm_rows])
                            if p > 0
                        )
                        if len(_leaf_pos) >= 1:
                            merged_cols = []
                            for lp in _leaf_pos:
                                parts: list = []
                                last_part: str | None = None
                                for sm in _sm_rows:
                                    for s, (txt, end) in sm.items():
                                        if s <= lp <= end:
                                            if txt != last_part:
                                                parts.append(txt)
                                                last_part = txt
                                            break
                                merged_cols.append(" ".join(parts) if parts else "")
                            # Label column: staircase-merge texts at position 0
                            first_col_parts: list = []
                            last_fc: str | None = None
                            for sm in _sm_rows:
                                if 0 in sm:
                                    txt, _ = sm[0]
                                    if txt != last_fc:
                                        first_col_parts.append(txt)
                                        last_fc = txt
                            first_col = " ".join(first_col_parts)
                            return [[first_col] + merged_cols], header_row_count
            # Still no headers — fall back
            return None, 0

    num_headers = len(column_headers_list)

    # Check for "year-as-super-header" pattern:
    # Row 0: years with LARGE colspan (e.g., "2003" cs=5, "2002" cs=5)
    #   OR full dates with LARGE colspan (e.g., "January 26, 2025" cs=5)
    # Row 1: sub-headers with smaller colspan (e.g., "BENEFIT OBLIGATION" cs=2)
    # Result: merge year/date + sub-header -> "2003 BENEFIT OBLIGATION", etc.
    year_super_headers = []  # [(year_text, start_col, end_col), ...]
    for row_idx, parsed in year_rows:
        for text, colspan, start in parsed:
            if not text:
                continue
            # Skip first-column labels, but allow years at position 0
            if start == 0 and not is_year(text):
                continue
            _text_clean = re.sub(r"<[Bb][Rr]\s*/?>", " ", text)
            # Bare year (e.g. "2007") OR full date (e.g. "November 26, 2007")
            _is_strong_date = is_year(text) or bool(
                re.search(
                    rf"({MONTHS_PATTERN})\s+\d{{1,2}},?\s*(19|20)\d{{2}}",
                    _text_clean,
                    re.I,
                )
            )
            # "Month YYYY" (no day) or "As of Month YYYY" — also a date
            _is_month_year = bool(
                re.search(
                    rf"(As\s+of\s+)?({MONTHS_PATTERN})\s+(19|20)\d{{2}}\b",
                    _text_clean,
                    re.I,
                )
            )
            # Require colspan > 2 for bare dates; >= 2 is enough when the
            # match is explicit (month+year or full date) since gutter tables
            # pack one data column into cs=2.
            if (_is_strong_date and colspan > 2) or (
                (_is_strong_date or _is_month_year) and colspan >= 2
            ):
                year_super_headers.append((text, start, start + colspan))

    # Guard: if category rows have LARGER colspans than the year
    # super-headers, then years are children of the categories, not
    # super-headers.  E.g. "Three Months Ended May" cs=7 contains
    # "1999" cs=3 and "1998" cs=3.  The standard category-distribution
    # path handles this correctly.
    # Check ALL non-empty cells in category rows (not just those passing
    # is_category_text), since period phrases like "Three Months Ended
    # October 31," are valid category headers but may fail the strict
    # is_category_text check due to trailing numbers/punctuation.
    if year_super_headers and category_rows:
        max_year_cs = max((end - start) for _, start, end in year_super_headers)
        max_cat_cs = 0
        for _, cat_parsed in category_rows:
            for _t, _c, _s in cat_parsed:
                if _t and _s > 0 and _c > max_cat_cs:
                    max_cat_cs = _c
        if max_cat_cs > max_year_cs:
            year_super_headers = []  # Not really super-headers

    # Allow the path even when header_info has only the year row itself
    # (no other rows classified as headers) — the lookahead block below will
    # discover staircase rows that failed is_header_row (e.g. "Assets / 0-6 / 6-12"
    # which has a label at col 0 and non-category column text).
    if year_super_headers and len(header_info) >= 1:
        year_row_indices = {idx for idx, _ in year_rows}

        # Pattern for words that are just date-label fragments (not real sub-headers).
        # A row made entirely of these is a continuation of a year label split
        # across two HTML rows (e.g., "As of" in row N, "November 2007" in row N+1).
        _date_frag_re = re.compile(
            rf"^(as(\s+of)?|of|through|ended|and|or)$"
            rf"|^{MONTHS_PATTERN}$"
            rf"|^(19|20)\d{{2}}$",
            re.I,
        )

        def _is_year_label_frag_row(parsed_row):
            """Return True if every non-empty text cell is a bare date word fragment."""
            text_vals = [
                txt.strip()
                for txt, _cs, _st in parsed_row
                if txt and txt.strip() and re.search(r"[A-Za-z]", txt)
            ]
            if not text_vals:
                return False
            return all(_date_frag_re.match(v) for v in text_vals)

        # Collect all non-year header rows found during the initial scan,
        # also excluding rows that are purely year-label fragment rows.
        sub_rows = [
            (idx, parsed)
            for idx, parsed, is_yr, is_cat in header_info
            if idx not in year_row_indices and not _is_year_label_frag_row(parsed)
        ]

        # Look ahead past header_row_count for additional staircase rows that
        # is_category_text() missed (e.g. "Owned, at", "Purchased, at" contain
        # commas which break the category-text regex).  Stop at first data row.
        lookahead_count = header_row_count
        for extra_idx in range(
            header_row_count, min(header_row_count + 10, len(parsed_rows))
        ):
            extra_parsed = parsed_rows[extra_idx]
            extra_ne = [(t, c, s) for t, c, s in extra_parsed if t and t.strip()]
            if not extra_ne:
                continue  # blank spacer row — keep looking
            # Any purely numeric cell means we have hit a data row
            has_numeric = any(
                re.match(r"^[\$]?\s*[\(\)]?\s*[\d,]+\.?\d*\s*[\)\%]?$", t)
                for t, c, s in extra_ne
            )
            if has_numeric:
                break
            # Credit-rating / status values at data columns (start > 0) also
            # signal a data row.  These are short alphanumeric codes like F1,
            # A+, AA-, P-1, Stable, N/A that appear in ratings tables but are
            # NOT recognized by the numeric pattern above.
            _rating_re = re.compile(
                r"^(?:"
                r"[A-Z]{1,3}[+-]"  # A+, AA-, BBB+  (S&P/Fitch style)
                r"|[A-Z]{1,2}-\d"  # P-1, F-2       (Moody's/Fitch CP)
                r"|F\d[+-]?"  # F1, F1+        (Fitch specific)
                r"|[A-Z][a-z]{1,3}\d"  # Aa1, Baa2      (Moody's long-term)
                r"|Prime-\d"  # Prime-1
                r")$"
            )
            _status_words = {
                "stable",
                "positive",
                "negative",
                "watch",
                "developing",
                "n/a",
                "nm",
                "nr",
                "wd",
            }
            has_rating_data = any(
                (
                    _rating_re.match(t)
                    or t.upper() in ("N/A", "NM", "NR", "WD")
                    or t.lower() in _status_words
                )
                for t, c, s in extra_ne
                if s > 0  # only data columns, not the label column
            )
            if has_rating_data:
                break
            # Skip year-label fragment rows in the lookahead too
            if _is_year_label_frag_row(extra_parsed):
                continue
            # Must contain at least some letter-bearing cells (not just blanks/punct)
            text_cells = [
                (t, c, s) for t, c, s in extra_ne if re.search(r"[A-Za-z]", t)
            ]
            if text_cells:
                sub_rows.append((extra_idx, extra_parsed))
                lookahead_count = extra_idx + 1

        if sub_rows:
            # Build per-row start-maps: col_start -> (text, inclusive_end)
            row_start_maps: list = []
            for _, sub_parsed_row in sub_rows:
                sm = {}
                for text, colspan, start in sub_parsed_row:
                    t = (
                        text.replace("\u200b", "")
                        .replace("\u200c", "")
                        .replace("\u200d", "")
                        .replace("\ufeff", "")
                        .strip()
                    )
                    if t and re.search(r"[A-Za-z]", t):
                        sm[start] = (t, start + colspan - 1)
                    elif t and not re.match(
                        r"^[\$]?\s*[\(\)]?\s*[\d,]+\.?\d*\s*[\)\%]?$", t
                    ):
                        # Also include non-alpha cells that are NOT plain financial
                        # data — e.g. maturity-range labels like "0 - 6", "1 - 5".
                        sm[start] = (t, start + colspan - 1)
                if sm:
                    row_start_maps.append(sm)

            if row_start_maps:
                # Leaf positions = union of all non-empty cell starts across
                # every staircase row — ensures cells that only appear in one
                # row (e.g. "Total" in the bottom leaf row) are not missed.
                # Always exclude position 0: it is the label/row-header column.
                leaf_positions_sub: list = sorted(
                    p
                    for p in set().union(*[set(sm.keys()) for sm in row_start_maps])
                    if p > 0
                )

                if len(leaf_positions_sub) >= 2:
                    # For each leaf position, walk every staircase row top-to-
                    # bottom collecting the cell that covers that position.
                    # Consecutive duplicates are suppressed so parent "2007"
                    # spanning both sub-columns doesn't repeat within a column.
                    # Date-fragment words (bare month names, "As of", "of" etc.)
                    # are skipped — they are split pieces of the year super-header
                    # label and must not contaminate sub-column names.
                    merged_subs: list = []
                    for leaf_pos in leaf_positions_sub:
                        parts = []
                        last_text = None
                        for sm in row_start_maps:
                            for start, (text, end) in sm.items():
                                if start <= leaf_pos <= end:
                                    if (
                                        not _date_frag_re.match(text)
                                        and text != last_text
                                    ):
                                        parts.append(text)
                                        last_text = text
                                    break
                        merged_subs.append(" ".join(parts) if parts else "")

                    # Determine whether position 0 is a label column.
                    # Merge staircase texts at position 0 the same way
                    # data columns do — e.g. "Assets" / "Contract Type"
                    # across two rows → "Assets Contract Type".
                    first_col_parts = []
                    last_first_col: str | None = None
                    for sm in row_start_maps:
                        if 0 in sm:
                            _fc_text, _fc_end = sm[0]
                            if (
                                not _date_frag_re.match(_fc_text)
                                and _fc_text != last_first_col
                            ):
                                first_col_parts.append(_fc_text)
                                last_first_col = _fc_text
                    first_col_label = (
                        " ".join(first_col_parts) if first_col_parts else ""
                    )

                    # Build year layer using position-based assignment:
                    # assign the year label to the FIRST leaf under each span,
                    # and "" for subsequent leaves under the same span.
                    # This correctly handles uneven splits like 4+1 rather
                    # than assuming equal distribution.

                    # Check whether this is a one-to-one mapping: every year
                    # span covers exactly ONE leaf position.  In that case the
                    # year cell and the sub-header cell at the same position
                    # together form ONE column name (e.g. "As of" + "November
                    # 2007" → "As of November 2007").  Producing a two-layer
                    # structure would split them inappropriately.
                    _leaves_per_span = {
                        (ys, ye): sum(1 for lp in leaf_positions_sub if ys <= lp < ye)
                        for _yt, ys, ye in year_super_headers
                    }
                    _all_one_to_one = all(v == 1 for v in _leaves_per_span.values())

                    if _all_one_to_one:
                        # Single-layer mode: merge ALL staircase rows (sub-rows
                        # AND the year row) vertically per column position,
                        # without filtering date-fragment words — they are
                        # legitimate parts of the column label here.
                        _all_staircase = sorted(
                            sub_rows + list(year_rows),
                            key=lambda x: x[0],
                        )
                        flat_maps: list = []
                        for _, _row_parsed in _all_staircase:
                            _sm: dict = {}
                            for _txt, _cs, _st in _row_parsed:
                                _t = (
                                    _txt.replace("\u200b", "")
                                    .replace("\u200c", "")
                                    .replace("\ufeff", "")
                                    .strip()
                                )
                                if _t and (
                                    re.search(r"[A-Za-z0-9]", _t)
                                    and not re.match(
                                        r"^[\$]?\s*[\(\)]?\s*[\d,]+\.?\d*\s*[\)\%]?$",
                                        _t,
                                    )
                                ):
                                    _sm[_st] = (_t, _st + _cs - 1)
                            if _sm:
                                flat_maps.append(_sm)

                        flat_subs: list = []
                        for leaf_pos in leaf_positions_sub:
                            _parts: list = []
                            _last: str | None = None
                            for _sm in flat_maps:
                                for _s, (_t, _end) in _sm.items():
                                    if _s <= leaf_pos <= _end:
                                        if _t != _last:
                                            _parts.append(_t)
                                            _last = _t
                                        break
                            flat_subs.append(" ".join(_parts) if _parts else "")

                        # Label column: merge position-0 texts from all rows
                        _fc_parts: list = []
                        _last_fc: str | None = None
                        for _sm in flat_maps:
                            if 0 in _sm:
                                _t, _ = _sm[0]
                                if _t != _last_fc:
                                    _fc_parts.append(_t)
                                    _last_fc = _t
                        _first_col = " ".join(_fc_parts)

                        return (
                            [[_first_col] + flat_subs],
                            max(header_row_count, lookahead_count),
                        )

                    year_row = [first_col_label]
                    seen_years: set = set()
                    for leaf_pos in leaf_positions_sub:
                        assigned_year = ""
                        for year_text, year_start, year_end in year_super_headers:
                            if year_start <= leaf_pos < year_end:
                                if year_text not in seen_years:
                                    assigned_year = year_text
                                    seen_years.add(year_text)
                                break
                        year_row.append(assigned_year)

                    sub_header_row_data = [first_col_label] + merged_subs
                    header_layers = [year_row, sub_header_row_data]
                    return header_layers, max(header_row_count, lookahead_count)

    # Extract categories with their positions, then merge vertically
    # Categories at same position merge: "EQUIPMENT" + "OPERATIONS" -> "EQUIPMENT OPERATIONS"
    # Only include cells with LARGE colspan (spanning multiple year columns)
    position_texts: dict = {}  # col_pos -> [text1, text2, ...]
    position_colspans: dict = {}  # col_pos -> colspan

    for row_idx, parsed in category_rows:
        for text, colspan, start in parsed:
            # Category headers must have large colspan (> 2) to span header columns
            if (
                text
                and colspan > 2
                and start > 0
                and (
                    is_category_text(text)
                    or re.search(
                        rf"(months?|quarters?|years?|weeks?)\s+ended|ended\s+{MONTHS_PATTERN}",
                        text,
                        re.I,
                    )
                )
            ):
                # Clean <br> tags from category text
                clean_text = re.sub(r"<[Bb][Rr]\s*/?>", " ", text).strip()
                clean_text = re.sub(r"\s+", " ", clean_text)
                if start not in position_texts:
                    position_texts[start] = []
                    position_colspans[start] = colspan
                else:
                    # Using the large parent colspan would incorrectly let the
                    # first child gobble up headers belonging to siblings.
                    position_colspans[start] = min(position_colspans[start], colspan)
                position_texts[start].append(clean_text)

    # Build merged categories in position order
    sorted_positions = sorted(position_texts.keys())
    categories = []  # [(merged_name, num_years_under), ...]

    for pos in sorted_positions:
        merged_name = " ".join(position_texts[pos])
        # Estimate headers under this category by colspan ratio
        # If all categories have same colspan, headers are evenly distributed
        categories.append(merged_name)

    # Collect "orphan" header cells from category rows — cells at
    # start > 0 that are NOT categories (failed is_category_text) and
    # NOT inside any recognized category's column span.  These are
    # independent column headers (e.g., "Balance Dec. 31, 2024")
    # that should appear as their own columns in the output.
    orphan_headers: list[tuple[str, int]] = []  # (text, start_pos)
    for _ri, parsed in category_rows:
        for text, colspan, start in parsed:
            if not text or start == 0:
                continue
            # Skip cells already captured as categories
            if start in position_texts:
                continue
            # Skip cells inside a category span
            inside_cat = False
            for cat_pos in sorted_positions:
                cat_end = cat_pos + position_colspans[cat_pos]
                if cat_pos <= start < cat_end:
                    inside_cat = True
                    break
            if inside_cat:
                continue
            clean_text = re.sub(r"<[Bb][Rr]\s*/?>", " ", text).strip()
            clean_text = re.sub(r"\s+", " ", clean_text)
            if clean_text:
                orphan_headers.append((clean_text, start))

    num_categories = len(categories)
    if num_categories == 0 and not orphan_headers:
        # No categories - just column headers
        header_layers = [[""] + column_headers_list]
        return header_layers, header_row_count

    # When there are orphan headers alongside categories, build a
    # combined position-ordered structure: orphan headers appear as
    # independent leaf columns (1 column each) and categories expand
    # to hold their sub-headers from year_rows.
    if orphan_headers and num_categories > 0:
        # Build a unified position list: each entry is either
        # ("orphan", text, start) or ("cat", name, start, colspan)
        unified: list = []
        for text, pos in orphan_headers:
            unified.append(("orphan", text, pos, 0))
        for cat_idx, cat_name in enumerate(categories):
            cat_pos = sorted_positions[cat_idx]
            cat_cs = position_colspans[cat_pos]
            unified.append(("cat", cat_name, cat_pos, cat_cs))
        unified.sort(key=lambda x: x[2])  # sort by start position

        cat_row = [""]
        header_row = [""]
        header_idx = 0

        for entry in unified:
            kind = entry[0]
            if kind == "orphan":
                orphan_text = entry[1]
                # Orphan headers are independent leaf columns —
                # they appear directly in the header row with empty
                # category text above.
                cat_row.append("")
                header_row.append(orphan_text)
            else:
                cat_name = entry[1]
                cat_pos = entry[2]
                cat_cs = entry[3]
                cat_end = cat_pos + cat_cs

                # Collect year headers whose positions fall within
                # this category's column range.
                sub_hdrs = []
                for hi in range(num_headers):
                    if column_headers_positions:
                        hdr_pos = column_headers_positions[hi]
                    else:
                        break
                    if cat_pos <= hdr_pos < cat_end:
                        sub_hdrs.append(column_headers_list[hi])

                if not sub_hdrs:
                    cat_row.append(cat_name)
                    header_row.append("")
                else:
                    cat_row.append(cat_name)
                    for _ in range(len(sub_hdrs) - 1):
                        cat_row.append("")
                    for sh in sub_hdrs:
                        header_row.append(sh)

        header_layers = [cat_row, header_row]

        return header_layers, header_row_count

    # Distribute column headers across categories
    # Use position-based matching when position info is available,
    # otherwise fall back to even distribution
    cat_row = [""]  # Start with label column
    header_row = [""]  # Start with label column

    if column_headers_positions and len(column_headers_positions) == num_headers:
        # Position-based distribution: match headers to categories
        # by checking which headers fall within each category's column range
        header_idx = 0

        # These are independent data columns (like unit-of-measure)
        # that don't belong under any period category.
        first_cat_pos = sorted_positions[0] if sorted_positions else 0
        while (
            header_idx < num_headers
            and column_headers_positions[header_idx] < first_cat_pos
        ):
            cat_row.append("")
            header_row.append(column_headers_list[header_idx])
            header_idx += 1

        for cat_idx, cat_name in enumerate(categories):
            cat_pos = sorted_positions[cat_idx]
            cat_cs = position_colspans[cat_pos]
            cat_end = cat_pos + cat_cs

            # Consume any gap/orphan headers that fall between the
            # previous category's end and this category's start.
            while (
                header_idx < num_headers
                and column_headers_positions[header_idx] < cat_pos
            ):
                cat_row.append("")
                header_row.append(column_headers_list[header_idx])
                header_idx += 1

            # Collect headers whose positions fall within [cat_pos, cat_end)
            start_idx = header_idx
            while header_idx < num_headers:
                hdr_pos = column_headers_positions[header_idx]
                if cat_pos <= hdr_pos < cat_end:
                    header_idx += 1
                else:
                    break

            count = header_idx - start_idx
            if count == 0:
                # Category has no sub-headers; add a single empty slot
                cat_row.append(cat_name)
                header_row.append("")
            else:
                cat_row.append(cat_name)
                for _ in range(count - 1):
                    cat_row.append("")

                for i in range(count):
                    idx = start_idx + i
                    if idx < len(column_headers_list):
                        header_row.append(column_headers_list[idx])
                    else:
                        header_row.append("")

        # Append any remaining unmatched headers
        while header_idx < num_headers:
            cat_row.append("")
            header_row.append(column_headers_list[header_idx])
            header_idx += 1
    else:
        # Fallback: even distribution when positions not available
        headers_per_category = (
            num_headers // num_categories if num_categories else num_headers
        )
        if headers_per_category == 0:
            headers_per_category = 1

        header_idx = 0
        for cat_name in categories:
            cat_row.append(cat_name)
            for _ in range(headers_per_category - 1):
                cat_row.append("")
            for i in range(headers_per_category):
                if header_idx < len(column_headers_list):
                    header_row.append(column_headers_list[header_idx])
                    header_idx += 1
                else:
                    header_row.append("")

    header_layers = [cat_row, header_row]

    return header_layers, header_row_count


def extract_periods_from_rows(
    rows_with_cs, row_has_th_flags=None, _year_pos_shift=None
):
    """Extract column headers from header rows.

    Args:
        rows_with_cs: List of rows, each row is list of (text, colspan) tuples
        row_has_th_flags: Optional list of booleans indicating if each row has <th> elements

    Returns (header_layers, header_row_count) where:
        header_layers: list of rows (each row is list of strings for each column)
        header_row_count: number of source rows consumed

    For multi-level headers (e.g., "Equipment Operations" spanning 2025/2024/2023),
    returns multiple header rows like:
        [["", "Equipment Operations", "Equipment Operations", ..., "Financial Services", ...],
         ["", "2025", "2024", "2023", "2025", ...]]
    """
    if not rows_with_cs:
        return [], 0

    # Calculate total columns from first row
    total_cols = sum(cs for _, cs in rows_with_cs[0]) if rows_with_cs else 0

    # Helper function to detect and merge vertical multi-row headers
    def merge_vertical_headers(rows_with_cs, total_cols, row_has_th_flags=None):
        """Merge consecutive header rows that have text at same column positions.

        For tables like:
            Row 1: "Retail Notes"[cs=2] | "Revolving"[cs=2]
            Row 2: "& Financing"[cs=2] | "Charge"[cs=2] | "Wholesale"[cs=2]
            Row 3: "Leases"[cs=2] | "Accounts"[cs=2] | "Receivables"[cs=2] | "Total"[cs=2]

        Merges to: ["Retail Notes & Financing Leases", "Revolving Charge Accounts",
                   "Wholesale Receivables", "Total"]

        Args:
            rows_with_cs: List of rows with colspan info
            total_cols: Total number of columns in table
            row_has_th_flags: Optional list of booleans - if row has only <td> elements (no <th>),
                             it's definitely a data row, not a header row
        """
        if not rows_with_cs:
            return None, 0

        # Helper to check if text looks like a header (not data, not a year)
        def is_header_text(t):
            if not t:
                return False
            # Remove zero-width chars
            t = (
                t.replace("\u200b", "")
                .replace("\u200c", "")
                .replace("\u200d", "")
                .replace("\ufeff", "")
                .strip()
            )
            if not t:
                return False
            # Years are headers
            if re.match(r"^(19|20)\d{2}$", t):
                return True
            # Year-range labels like "2009 -", "2011 –", "2013-" are headers
            # (the trailing dash signals the start of a date range spanning the
            # child row, e.g. "2009 - 2010").
            if re.match(r"^(19|20)\d{2}\s*[\-\u2013\u2014]", t):
                return True
            # Data patterns - not headers
            if re.match(r"^[\$]?\s*[\(\)]?\s*[\d,]+\.?\d*\s*[\)\%]?$", t):
                return False
            # Single punctuation - not a header
            if len(t) <= 1:
                return False
            # Numeric range labels like "0 - 6", "6 - 12", "1 - 5" are maturity
            # bucket column headers — they contain no letters but are clearly headers.
            if re.match(r"^\d+\s*[-\u2013\u2014]\s*\d+$", t):
                return True
            # Text with letters is likely a header
            return bool(re.search(r"[A-Za-z]", t))

        # Helper to check if row is a data row (has numeric values OR rating-like values)
        def is_data_row(row):
            col_pos = 0
            for text, cs in row:
                t = (
                    text.replace("\u200b", "")
                    .replace("\u200c", "")
                    .replace("\u200d", "")
                    .replace("\ufeff", "")
                    .strip()
                )
                if (
                    t
                    and re.match(r"^[\$]?\s*[\(\)]?\s*[\d,]+\.?\d*\s*[\)\%]?$", t)
                    and not re.match(r"^(19|20)\d{2}$", t)
                ):
                    # At position 0 (label column), a bare small number
                    # (1-3 digits with no financial formatting) may be a
                    # rendering artifact rather than a data value.
                    if col_pos == 0 and re.match(r"^\d{1,3}$", t):
                        col_pos += cs
                        continue
                    # Check if it's a year (years in header rows are ok)
                    return True
                # Also check for rating-like values (A+, A1, Prime-1, F1, Stable, etc.)
                # These are alphanumeric but short and look like data, not headers
                if t and len(t) <= 10:
                    # Short alphanumeric codes that are likely ratings/data
                    # Examples: A+, A1, Aa1, BBB+, Prime-1, F1, Stable, Positive, Negative
                    # IMPORTANT: Must end with a modifier (+/-/digit) to distinguish from words like "Tax"
                    if re.match(r"^[A-Z][a-z]{0,2}[+-][0-9]?$", t):  # A+, Aa+, Baa+
                        return True
                    if re.match(r"^[A-Z][a-z]{0,2}[0-9]$", t):  # A1, Aa1, Baa1
                        return True
                    if re.match(r"^[A-Z]{1,3}[+-]$", t):  # AA+, BBB-
                        return True
                    if re.match(r"^Prime-\d$", t):  # Prime-1
                        return True
                    if re.match(r"^[A-Z]\d$", t):  # F1
                        return True
                    # Common outlook/status values
                    if t.lower() in (
                        "stable",
                        "positive",
                        "negative",
                        "watch",
                        "developing",
                    ):
                        return True
                col_pos += cs
            return False

        # Helper to check if row is a title row (single cell spanning most of table)
        def is_title_row(row, total_cols):
            """Check if this row is a title/description spanning most of the table."""
            non_empty_cells = []
            total_span = 0
            for text, colspan in row:
                t = (
                    text.replace("\u200b", "")
                    .replace("\u200c", "")
                    .replace("\u200d", "")
                    .replace("\ufeff", "")
                    .strip()
                )
                total_span += colspan
                if t:
                    non_empty_cells.append((t, colspan))

            # If single text cell spans majority of the table width, it's a title row
            # This catches company names, statement titles, period descriptions, etc.
            if len(non_empty_cells) == 1:
                text, colspan = non_empty_cells[0]
                # Single cell spanning >= 40% of columns is a title/category row
                # Lower threshold to catch super-headers like "Total Stockholders' Equity"
                if colspan >= total_cols * 0.4:
                    return True
            return False

        # Find consecutive header rows (non-empty, non-data rows)
        header_rows: list = []

        # Only use <th>/<td> as a hard "data row" signal when the table mixes
        # them.  Old SEC HTML often uses <td> for every cell — including headers
        # — so when every row is all-<td> we must rely on is_data_row() alone.
        _some_th_rows = bool(row_has_th_flags and any(row_has_th_flags))

        for row_idx, row in enumerate(rows_with_cs):
            # In tables that mix <th> and <td>, a row with only <td> cells is
            # definitely a data row — stop collecting headers here.
            if (
                _some_th_rows
                and row_idx < len(row_has_th_flags)  # type: ignore
                and not row_has_th_flags[row_idx]  # type: ignore
            ):
                # Row has only <td> elements in a table that mixes th/td - data row
                break

            # Check for empty row
            has_content = any(is_header_text(text) for text, _ in row)
            if not has_content:
                if header_rows:
                    continue  # Skip empty rows between header rows
                continue

            # Check if this is a data row
            if is_data_row(row):
                break

            # Skip title/description rows that span most of the table
            if is_title_row(row, total_cols):
                continue

            # Check if this is a section label in column 0 (like "Assets:" or "Liabilities:")
            # Section labels can have colspan > 1 for formatting but are still a single label
            non_empty_cells = [
                (text.replace("\u200b", "").strip(), cs, idx)
                for idx, (text, cs) in enumerate(row)
                if text.replace("\u200b", "").strip()
            ]
            if len(non_empty_cells) == 1:
                text, cs, cell_idx = non_empty_cells[0]
                # Section label detection:
                # 1. Single non-empty cell at the start of the row (first few positions)
                # 2. Text ends with ":" (like "Assets:", "Liabilities and Equity:")
                # 3. OR small colspan (1-3) in first position - generic label
                # BUT: Don't treat years as section labels - they're data markers
                is_year_label = bool(re.match(r"^(19|20)\d{2}$", text.strip()))
                is_section_label = False
                if not is_year_label and (
                    cell_idx == 0 or cs >= 2
                ):  # First cell or spanning cell
                    if text.endswith(":"):
                        # Explicit section label like "Assets:" or "Liabilities:"
                        is_section_label = True
                    elif cs <= 3 and cell_idx == 0:
                        # Small colspan single text at start - likely a label
                        is_section_label = True

                if is_section_label:
                    if header_rows:
                        break
                    continue

            header_rows.append((row_idx, row))

        # Need at least 2 header rows for vertical merging to be useful
        if len(header_rows) < 2:
            return None, 0

        # Build per-row cell maps: start_pos -> (text, end_pos_inclusive)
        #
        # We intentionally store only the START position of each cell (not all
        # positions within its span).  Parent cells like "2007" (colspan=6) and
        # child cells like "Instruments" (colspan=2) therefore get distinct
        # entries at their respective starting positions.  The "covers" check
        # below (start <= leaf_pos <= end) is then used to find the cell that
        # covers any given leaf column position.
        row_cell_start_maps: list[dict] = []
        for _row_idx, row in header_rows:
            start_map: dict = {}
            col_pos = 0
            for text, colspan in row:
                t = (
                    text.replace("\u200b", "")
                    .replace("\u200c", "")
                    .replace("\u200d", "")
                    .replace("\ufeff", "")
                    .strip()
                )
                if t and is_header_text(t):
                    # (text, inclusive_end_position)
                    start_map[col_pos] = (t, col_pos + colspan - 1)
                col_pos += colspan
            if start_map:
                row_cell_start_maps.append(start_map)

        if not row_cell_start_maps:
            return None, 0

        # Leaf column positions = the UNION of all cell starting positions across
        # every header row.  Using the union (rather than just the row with the
        # most cells) ensures we capture columns that only appear in some rows.
        # Example – Commitments table:
        #   Row 0: "2008"(col2) "2009 -"(col4) "2011 -"(col6) "2013 -"(col8)   → 4 cells
        #   Row 1:              "2010"  (col4)  "2012"  (col6) "Thereafter"(col8) "Total"(col10) → 4 cells
        #   Union positions: [2, 4, 6, 8, 10]  → "Total" at col 10 is included.
        # Example – GS 2008 Financial Instruments staircase:
        #   Row 2: "Financial"(col6) "Financial"(col14)           → 2 cells
        #   Row 3: "Financial"(col2) "Instruments"(col6) ...      → 4 cells
        #   Union positions: [2, 6, 10, 14]  → same as max-cells approach.
        leaf_positions: list = sorted(set().union(*row_cell_start_maps))

        if not leaf_positions or len(leaf_positions) < 2:
            return None, 0

        # For each leaf position, walk all header rows top-to-bottom and collect
        # the text of the cell that COVERS that position
        # (i.e. cell_start <= leaf_pos <= cell_end).  Consecutive identical
        # texts are deduplicated so a parent "2007" that covers multiple leaf
        # columns doesn't repeat within the merged string for a single column.
        merged_headers: list = []
        for leaf_pos in leaf_positions:
            parts: list = []
            last_text = None
            for sm in row_cell_start_maps:
                for start, (text, end) in sm.items():
                    if start <= leaf_pos <= end:
                        if text != last_text:
                            parts.append(text)
                            last_text = text
                        break  # only one cell can cover a position per row
            if parts:
                merged_headers.append(" ".join(parts))

        if not merged_headers:
            return None, 0

        # If position 0 is not a leaf column it is the empty label column.
        is_label_col = 0 not in leaf_positions

        # Return as a single merged header layer.
        header_row_count = max(row_idx for row_idx, _ in header_rows) + 1
        prefix: list = [""] if is_label_col else []
        return [prefix + merged_headers], header_row_count

    # Try multi-level header extraction first
    header_layers, header_row_count = build_column_headers_from_colspan(
        rows_with_cs, _year_pos_shift
    )
    # Only attempt vertical merging when build_column_headers_from_colspan found
    # nothing.  If it already returned a proper multi-layer result (e.g. 2007/2006
    # parent rows spanning child sub-headers) we must NOT flatten it into a single
    # merged row — that destroys the multi-index structure the caller depends on.
    vertical_headers, vertical_row_count = (None, 0)
    _colspan_has_year_range_fragments = (
        header_layers is not None
        and len(header_layers) == 1
        and any(
            # Match incomplete year-range fragments like "2009 -" that need
            # merging with a row below (e.g. "2010"), but NOT complete ranges
            # like "2027-2028" or "2029 - 2030" which are valid headers.
            re.match(r"^(19|20)\d{2}\s*[-\u2013\u2014]", h.strip())
            and not re.match(
                r"^(19|20)\d{2}\s*[-\u2013\u2014]\s*(19|20)\d{2}$", h.strip()
            )
            for h in header_layers[0]
            if h
        )
    )
    if header_row_count == 0 or _colspan_has_year_range_fragments:
        # Also try vertical header merging for two cases:
        #   1. Colspan extraction found nothing (header_row_count == 0).
        #      Example: "2009 -" / "2010" stacked → merged to "2009 - 2010"
        #   2. Colspan returned a flat single-layer with incomplete year-range fragments
        #      like "2009 -" (companion row wasn't merged by the month-year logic).
        #      Vertical merging will produce the correct e.g. "2009 - 2010" strings.
        if _colspan_has_year_range_fragments:
            # Discard the useless flat result so the vertical output wins below
            header_layers = None
            header_row_count = 0
        vertical_headers, vertical_row_count = merge_vertical_headers(
            rows_with_cs, total_cols, row_has_th_flags
        )
    # Decide which approach produced better headers
    # Prefer vertical merge if it created multi-word headers (indicating successful merge)
    use_vertical = False

    if vertical_headers and vertical_row_count > 0:
        # Check if vertical merge created multi-word headers
        vertical_multi_word = any(
            len(h.split()) >= 2
            for layer in vertical_headers
            for h in layer
            if h
            and not re.match(r"^[\(\)]*$", h)
            and not re.match(r"^(19|20)\d{2}$", h)
        )

        # Check if build_column_headers_from_colspan produced multi-word headers
        colspan_multi_word = False
        if header_layers:
            colspan_multi_word = any(
                len(h.split()) >= 2
                for layer in header_layers
                for h in layer
                if h
                and not re.match(r"^[\(\)]*$", h)
                and not re.match(r"^(19|20)\d{2}$", h)
            )

        # Prefer vertical if it merged headers but colspan approach didn't
        if vertical_multi_word and not colspan_multi_word:
            use_vertical = True
        # Also prefer vertical if it has more non-year headers (better merging)
        elif vertical_multi_word:
            vertical_non_year = sum(
                1
                for layer in vertical_headers
                for h in layer
                if h and not re.match(r"^(19|20)\d{2}$", h.strip())
            )
            colspan_non_year = (
                sum(
                    1
                    for layer in header_layers
                    for h in layer
                    if h and not re.match(r"^(19|20)\d{2}$", h.strip())
                )
                if header_layers
                else 0
            )
            if vertical_non_year >= colspan_non_year:
                use_vertical = True

    if use_vertical:
        # Validate: check for years/periods or financial terms
        all_header_text = " ".join(h for layer in vertical_headers for h in layer)  # type: ignore
        has_year_in_headers = bool(re.search(r"\b(19|20)\d{2}\b", all_header_text))
        has_period_in_headers = bool(
            re.search(
                r"(months?\s+ended|year\s+ended|weeks?\s+ended|quarter|period|fiscal)",
                all_header_text,
                re.I,
            )
        )
        has_year_in_rows = any(
            re.search(r"\b(19|20)\d{2}\b", text)
            for row in rows_with_cs[:vertical_row_count]
            for text, _ in row
        )
        has_year_after_headers = (
            any(
                re.search(r"\b(19|20)\d{2}\b", text)
                for row in rows_with_cs[vertical_row_count : vertical_row_count + 2]
                for text, _ in row
            )
            if vertical_row_count < len(rows_with_cs)
            else False
        )

        # Check for financial terms
        financial_terms = [
            r"\bshares?\b",
            r"\bprice\b",
            r"\bvalue\b",
            r"\bterm\b",
            r"\bexercise\b",
            r"\bgranted?\b",
            r"\bvested\b",
            r"\bforfeited?\b",
            r"\b(?:thousands?|millions?|billions?)\b",
            r"\bper\s+share\b",
            r"\bweighted\b",
            r"\baverage\b",
            r"\baggregate\b",
            r"\bintrinsic\b",
            r"\bcontractual\b",
            r"\bremaining\b",
            r"\bexercisable\b",
            r"\bAmount\b",
            r"\bCredit\b",
            r"\bDebit\b",
            r"\bBalance\b",
            r"\bReceivables?\b",
            r"\bLeases?\b",
            r"\bNotes?\b",
            r"\bAccounts?\b",
            r"\bWholesale\b",
            r"\bRetail\b",
            r"\bFinancing\b",
            r"\bTotal\b",
            r"\bAllowance\b",
            r"\bProvision\b",
            r"\bRevolving\b",
            r"\bTax\b",
            r"\bExpense\b",
            r"\bIncome\b",
            r"\bLoss\b",
            r"\bGain\b",
        ]
        has_financial_terms = any(
            re.search(term, all_header_text, re.I) for term in financial_terms
        )

        merged_multi_word = any(
            len(h.split()) >= 2
            for layer in vertical_headers  # type: ignore
            for h in layer
            if h and not re.match(r"^[\(\)]*$", h)
        )

        if (
            has_year_in_headers
            or has_period_in_headers
            or has_year_in_rows
            or has_year_after_headers
        ):
            return vertical_headers, vertical_row_count

        if merged_multi_word and has_financial_terms:
            return vertical_headers, vertical_row_count

    # Fall back to colspan-based headers if available
    if header_layers and header_row_count > 0:
        # Check if we have meaningful multi-level headers
        # Look for years in any layer
        has_years = False

        for layer in header_layers:
            for h in layer:
                if re.search(r"\b(19|20)\d{2}\b", h):
                    has_years = True
                    break

            if has_years:
                break

        if has_years and len(header_layers) >= 1:
            return header_layers, header_row_count

    # Fall back to original single-row logic
    period_prefixes = []
    years: list = []
    generic_headers: list = []
    full_date_headers = []
    sub_headers = []
    period_parts = []
    ended_parts = []
    as_of_prefix = ""

    # Only look at first 10 rows for headers (not data rows at the bottom)
    for row_idx, row in enumerate(rows_with_cs[:10]):
        texts = [t.strip() for t, cs in row if t.strip()]
        if not texts:
            continue

        row_text = " ".join(texts)

        # Look for period descriptions (e.g., "Three Months Ended May")
        if re.search(
            r"(months?\s+ended|year\s+ended|quarter\s+ended|weeks?\s+ended)",
            row_text,
            re.I,
        ):
            prefixes = [
                t
                for t in texts
                if re.search(r"(months?|year|quarter|weeks?)\s+ended", t, re.I)
            ]
            if prefixes:
                period_prefixes = prefixes

        # Check individual cells, not the joined row_text
        period_cell_matches = [
            t
            for t in texts
            if re.match(
                r"^(Three|Six|Nine|Twelve|[1-9]|[1-4]\d|5[0-3])\s+(Months?|Weeks?|Week Ended)$",
                t,
                re.I,
            )
            or re.match(r"^(Fiscal\s+)?(Year|Quarter)$", t, re.I)
        ]

        if period_cell_matches:
            period_parts = period_cell_matches

        # Look for "Ended May" or "Ended" continuation row
        ended_cell_matches = [t for t in texts if re.match(r"^Ended\b", t, re.I)]

        if ended_cell_matches and period_parts:
            ended_parts = ended_cell_matches
            # Combine with period_parts to make full prefixes
            if len(ended_parts) == len(period_parts):
                period_prefixes = [
                    f"{p} {e}" for p, e in zip(period_parts, ended_parts)
                ]
            elif len(ended_parts) == 1:
                # Same "Ended X" for all periods
                period_prefixes = [f"{p} {ended_parts[0]}" for p in period_parts]

        # Look for "As of" prefix row (for balance sheets)
        if re.match(r"^As\s+of$", row_text, re.I):
            as_of_prefix = "As of"

        # These are Month + Year in a single cell (possibly with "As of" prefix)
        date_pattern = rf"^(As\s+of\s+)?({MONTHS_PATTERN})\s+((?:19|20)\d{{2}})$"
        date_matches = [t for t in texts if re.match(date_pattern, t, re.I)]
        if len(date_matches) >= 2:
            full_date_headers = date_matches

        # Look for sub-headers like "Assets | Liabilities" that should combine with parent headers
        # These typically appear in rows with repeating short column labels
        sub_header_pattern = r"^(Assets|Liabilities|Actual|Pro\s*Forma|Adjustments)$"
        sub_matches = [t for t in texts if re.match(sub_header_pattern, t, re.I)]
        if len(sub_matches) >= 2:
            sub_headers = sub_matches

        # Look for years - but only standalone years, not years in parentheses (effective dates)
        # or years embedded in long descriptive text
        year_cells = []
        for t in texts:
            # Skip cells that are too long to be column headers
            if len(t) > 50:
                continue
            # Skip cells with years in parentheses like "(2020)" - these are effective dates
            if re.search(r"\(\d{4}\)", t):
                continue
            # Skip cells where year is part of a longer descriptive header
            # like "Executive Contributions in FY 2025 ($)" or "Aggregate Balance at FY 2025-end"
            # These are descriptive column headers, not year column headers
            if len(t) > 20 and re.search(
                r"(contributions?|balance|earnings|aggregate|withdrawals?|distributions?)",
                t,
                re.I,
            ):
                continue
            # Skip cells that are full dates (e.g., "April 7, 2025")
            # These are data values, not year column headers
            if re.match(
                rf"({MONTHS_PATTERN})\s+\d{{1,2}},?\s*(19|20)\d{{2}}",
                t,
                re.I,
            ):
                continue
            # Look for standalone years or years in simple header formats
            match = re.search(r"\b((?:19|20)\d{2})\b", t)
            if match:
                year_cells.append(match.group(1))
        if len(year_cells) >= 2 and not years:
            years = year_cells

        # Look for generic column headers ONLY in first few rows
        # Must be: non-numeric text, multiple items, short length, row has no data
        if row_idx < 5 and not generic_headers:
            # Skip descriptor rows like "(in millions...)"
            if row_text.startswith("("):
                continue
            # Skip rows with numbers that look like data (commas in numbers or decimals)
            if re.search(r"\d{1,3}(,\d{3})+|\d+\.\d{2}", row_text):
                continue
            # Candidates: short text items that are not numbers
            candidates = [
                t
                for t in texts
                if 2 <= len(t) <= 30
                and not re.match(r"^[\d\.,x\-]+$", t)
                and not t.startswith("(")
            ]
            if len(candidates) >= 2:
                # Check if these look like headers (mostly alphabetic)
                alpha_count = sum(1 for c in candidates if re.match(r"^[A-Za-z]", c))
                if alpha_count >= 2:
                    generic_headers = candidates

    # Priority 1: Full date headers with sub-headers (e.g., "As of May 1999" + "Assets/Liabilities")
    if full_date_headers and sub_headers:
        # Combine parent headers with sub-headers
        combined = []
        subs_per_parent = len(sub_headers) // len(full_date_headers)

        if subs_per_parent > 0:
            for i, parent in enumerate(full_date_headers):
                for j in range(subs_per_parent):
                    sub_idx = i * subs_per_parent + j

                    if sub_idx < len(sub_headers):
                        combined.append(f"{parent} {sub_headers[sub_idx]}")

            if combined:
                # Return as two rows: parent row and sub row
                parent_row = [""]
                sub_row = [""]

                for i, parent in enumerate(full_date_headers):
                    for j in range(subs_per_parent):
                        parent_row.append(parent)
                        sub_idx = i * subs_per_parent + j

                        if sub_idx < len(sub_headers):
                            sub_row.append(sub_headers[sub_idx])

                return [parent_row, sub_row], 2

    # Priority 2: Full date headers without sub-headers
    if full_date_headers:
        headers = (
            [f"{as_of_prefix} {d}" for d in full_date_headers]
            if as_of_prefix
            else full_date_headers
        )
        return [[""] + headers], 1

    # Priority 3: Combine prefixes with years
    if period_prefixes and years:
        # Check if prefixes already contain years (e.g., "For the Three Months Ended January 26, 2025")
        # Count how many years are mentioned in the prefixes
        prefix_year_counts = []

        for p in period_prefixes:
            year_matches = re.findall(r"\b(19|20)\d{2}\b", p)
            prefix_year_counts.append(len(year_matches))

        # If any prefix contains multiple years (describes multiple periods),
        # skip using prefixes and just use the years
        if any(count > 1 for count in prefix_year_counts):
            return [[""] + years], 1

        # If each prefix has exactly one year and matches the number of years,
        # use prefixes directly (they're full period descriptions)
        if all(count == 1 for count in prefix_year_counts) and len(
            period_prefixes
        ) == len(years):
            return [[""] + period_prefixes], 1

        periods = []
        prefix_idx = 0

        for i, year in enumerate(years):
            if prefix_idx < len(period_prefixes):
                prefix = period_prefixes[prefix_idx]
                # Only append year if prefix doesn't already have it
                if not re.search(r"\b" + year + r"\b", prefix):
                    periods.append(f"{prefix} {year}")
                else:
                    periods.append(prefix)
                # Advance prefix index every N years based on ratio
                years_per_prefix = len(years) // len(period_prefixes)
                if years_per_prefix > 0 and (i + 1) % years_per_prefix == 0:
                    prefix_idx += 1
            else:
                periods.append(year)
        return [[""] + periods], 1

    if years:
        return [[""] + years], 1

    if generic_headers:
        # No financial periods, use generic headers
        return [[""] + generic_headers], 1

    return [], 0


# ── Chart-legend helper ─────────────────────────────────────────────
_LEGEND_BG_RE = re.compile(r"background-color:\s*(#[0-9a-fA-F]{6})")


def _extract_chart_legend(table) -> str | None:
    """Detect a chart-legend table and return an inline legend string.

    SEC filings embed bar/pie charts as ``<img>`` tags followed by
    small HTML tables that use tiny coloured ``<td>`` cells as colour
    swatches paired with label text (typically font-family 'Gotham
    Narrow Book', font-size ~5 pt, rows of height ~3 pt).

    The standard table converter turns these into single-column
    markdown tables like::

        | Affiliates |
        |---|
        | Europe |

    This helper detects the pattern and emits a more useful format
    that preserves the colour-to-label mapping so the chart can be
    interpreted::

        **Legend:** ■ (#009dd9) United States · ■ (#0b2d71) Other Americas · …

    Returns ``None`` if the table is *not* a chart legend.
    """
    rows = table.find_all("tr")
    if not rows or len(rows) > 30:
        return None

    # Quick pre-check: reject tables that look like financial data.
    # Real chart legends never contain numeric data, dollar signs,
    # parenthesised negatives, or percentage values in their cells.
    _data_cell_re = re.compile(
        r"(?:^\s*[-—]?\s*\$|\d[\d,]+\.\d|^\s*\(\s*\d|\d\s*%\s*$" + r"|^\s*\d{4}\s*$)"
    )
    data_cell_count = 0
    for row in rows:
        for td in row.find_all("td"):
            cell_text = td.get_text(strip=True)
            if cell_text and _data_cell_re.search(cell_text):
                data_cell_count += 1
    if data_cell_count >= 2:
        return None

    # Chart-legend tables use tiny coloured cells as colour swatches.
    # A "swatch cell" MUST be a cell whose ONLY purpose is to show
    # a background colour — it must have NO text content (or at most
    # a single non-breaking space).  Cells that combine colour with
    # text are header/data cells, NOT swatches.
    #
    # Additionally, swatch cells should be physically small (height
    # ≤ 8px or width ≤ 30px via inline style).
    _height_re = re.compile(r"height:\s*(\d+(?:\.\d+)?)\s*(?:px|pt)", re.I)
    _width_re = re.compile(r"width:\s*(\d+(?:\.\d+)?)\s*(?:px|pt)", re.I)
    swatch_count = 0
    all_labels: list[str] = []
    all_colors: list[str] = []
    # Track how many rows have non-empty text in > 2 columns — a sign
    # this is a real data table, not a legend.
    multi_col_text_rows = 0

    for row in rows:
        tds = row.find_all("td")
        row_color: str | None = None
        row_label: str | None = None
        text_cell_count = 0
        for td in tds:
            style = td.get("style", "") or ""
            bg = _LEGEND_BG_RE.search(style)
            cell_text = td.get_text(strip=True)

            # A swatch cell: has background-color, is NOT white,
            # and has NO meaningful text content.
            if bg and bg.group(1).lower() not in ("#ffffff", "#fff") and not cell_text:
                # Check for small dimensions (strong swatch signal)
                h_m = _height_re.search(style)
                w_m = _width_re.search(style)
                is_tiny = (h_m and float(h_m.group(1)) <= 8) or (
                    w_m and float(w_m.group(1)) <= 30
                )
                if is_tiny:
                    row_color = bg.group(1)
                    swatch_count += 1
                else:
                    # Empty cell with colour but not tiny — could
                    # still be a swatch if no dimension is specified
                    # (some legends omit explicit sizes).  Count it
                    # but don't bump swatch_count (only truly tiny
                    # cells are confident swatch detections).
                    row_color = bg.group(1)
                # Cell has BOTH colour and text → NOT a swatch.
                # This is typically a header or data cell with shading.

            if cell_text and len(cell_text) < 80:
                row_label = cell_text
                text_cell_count += 1

        if text_cell_count > 2:
            multi_col_text_rows += 1
        if row_color and not row_label:
            all_colors.append(row_color)
        elif row_label and not row_color:
            all_labels.append(row_label)
        elif row_color and row_label:
            # Both in one row — paired directly
            all_colors.append(row_color)
            all_labels.append(row_label)

    # If many rows have text in 3+ columns, this is a data table.
    if multi_col_text_rows >= 2:
        return None

    # Require enough CONFIDENT swatch detections (tiny empty colour
    # cells) and at least two labels.
    if swatch_count < 2 or len(all_labels) < 2:
        return None

    # Labels should be category names, NOT numbers/years/percentages.
    _numeric_label_re = re.compile(r"^\s*[\d,.%$€£()\-—]+\s*$")
    non_numeric_labels = [lab for lab in all_labels if not _numeric_label_re.match(lab)]
    if len(non_numeric_labels) < 2:
        return None

    # Final sanity: the raw text of the whole table should be short
    # (legends are just a handful of category names).
    full_text = table.get_text(strip=True)
    if len(full_text) > 500:
        return None

    # Pair colours and labels.  The HTML structure typically puts the
    # label row immediately before its colour swatch row, so
    # all_labels[i] corresponds to all_colors[i].
    # Only include labels that have a paired colour swatch.
    # Unpaired labels (more labels than colours) are typically chart
    # titles/descriptions embedded in the legend table — omit them.
    n_pairs = min(len(non_numeric_labels), len(all_colors))
    if n_pairs < 2:
        return None

    # Build an HTML legend with actual CSS-styled colour swatches.
    # Using background-color on inline-block spans is the most reliable
    # way to render coloured boxes across markdown renderers.
    swatch = (
        '<span style="display:inline-block;width:12px;height:12px;'
        "background:{color};vertical-align:middle;border-radius:2px"
        '"></span>'
    )
    items: list[str] = []
    for idx in range(n_pairs):
        box = swatch.format(color=all_colors[idx])
        items.append(f"{box} {non_numeric_labels[idx]}")

    legend_body = " &nbsp;&middot;&nbsp; ".join(items)
    return (
        f'<div style="margin:4px 0;font-size:0.9em"><b>Legend:</b> {legend_body}</div>'
    )


# ── Table-title pattern for composite-table splitting ──────────────
_TABLE_TITLE_RE = re.compile(r"^TABLE\s+\d+", re.IGNORECASE)


def _split_composite_table(table) -> list:
    """Split a single <table> that contains multiple sub-tables.

    Certent CDM and similar absolute-position SEC filings often group
    several logical tables (e.g. TABLE 5, TABLE 6, TABLE 7) plus
    connecting body-text paragraphs into **one** horizontal-rule zone,
    so ``_build_table_from_zone`` emits a single ``<table>`` for the
    whole lot.

    This function detects "TABLE X:" header rows and splits the
    original table element into a list of ``(rows, is_body_text)``
    tuples.  Each ``rows`` list is a contiguous slice of ``<tr>``
    elements.  ``is_body_text`` is True when the section between two
    TABLE headers consists entirely of single-cell (full-width) text
    rows that should be rendered as paragraphs rather than a table.

    Returns a list of BS4 ``<table>`` elements (and plain-text string
    fragments for body-text sections) ready for independent conversion.
    """
    all_rows = table.find_all("tr")
    if len(all_rows) < 4:
        return [table]

    # Find rows whose first cell matches "TABLE X: …"
    split_indices: list[int] = []
    for idx, row in enumerate(all_rows):
        cells = row.find_all(["td", "th"])
        if not cells:
            continue
        first_text = cells[0].get_text(strip=True)
        if _TABLE_TITLE_RE.match(first_text):
            split_indices.append(idx)

    # Need at least 2 sub-table headers to justify splitting
    if len(split_indices) < 2:
        return [table]

    # Helper: detect if a row-set is purely body text
    # (all data in column 0, rest empty)
    def _is_body_text_section(rows):
        if not rows:
            return True
        for row in rows:
            cells = row.find_all(["td", "th"])
            # Check if any cell beyond the first has content
            if any(c.get_text(strip=True) for c in cells[1:]):
                return False
        return True

    # Build segments: each segment is a slice of rows
    # Segments between TABLE headers that are all single-cell → body text
    # TABLE header row + data rows after it → sub-table
    parts: list = []

    # Rows before the first TABLE header (belong to whatever table was at top)
    if split_indices[0] > 0:
        pre_rows = all_rows[: split_indices[0]]
        # Check if there's a "TABLE X:" in the very first rows
        # If so, this is the main table data; otherwise check for body text
        sub = _make_sub_table(pre_rows, table)
        parts.append(sub)

    for si in range(len(split_indices)):
        start = split_indices[si]
        end = split_indices[si + 1] if si + 1 < len(split_indices) else len(all_rows)

        # Find where body text starts between this and next TABLE header
        # The sub-table continues until rows become single-cell body text
        sub_rows = all_rows[start:end]

        # Within this slice, find where the data rows end and body text begins
        # Body text: every cell after col 0 is empty AND text is long (>60 chars),
        # OR an all-caps heading followed by body text paragraphs.
        data_end = len(sub_rows)
        for ri in range(1, len(sub_rows)):
            row = sub_rows[ri]
            cells = row.find_all(["td", "th"])
            first = cells[0].get_text(strip=True) if cells else ""
            rest_empty = not any(c.get_text(strip=True) for c in cells[1:])
            if not rest_empty or not first:
                continue
            if _TABLE_TITLE_RE.match(first):
                continue

            # Long body text paragraph
            is_body_start = len(first) > 60
            # Or: all-caps section heading followed by body text
            if not is_body_start and first.isupper() and len(first) > 5:
                # Check if the NEXT row is long body text
                ni = ri + 1
                if ni < len(sub_rows):
                    ncells = sub_rows[ni].find_all(["td", "th"])
                    nfirst = ncells[0].get_text(strip=True) if ncells else ""
                    nrest = not any(c.get_text(strip=True) for c in ncells[1:])
                    if nrest and len(nfirst) > 60:
                        is_body_start = True

            if is_body_start:
                remaining = sub_rows[ri:]
                if _is_body_text_section(remaining):
                    data_end = ri
                    break

        # Table data part
        table_rows = sub_rows[:data_end]
        if table_rows:
            parts.append(_make_sub_table(table_rows, table))

        # Body text part
        if data_end < len(sub_rows):
            body_rows = sub_rows[data_end:]
            body_text = "\n".join(
                row.find_all(["td", "th"])[0].get_text(strip=True)
                for row in body_rows
                if row.find_all(["td", "th"])
                and row.find_all(["td", "th"])[0].get_text(strip=True)
            )
            if body_text.strip():
                parts.append(body_text)

    return parts


def _make_sub_table(rows, original_table):
    """Create a new BS4 <table> element from a subset of rows."""
    # pylint: disable=import-outside-toplevel
    import copy as _copy

    soup = BeautifulSoup("<table></table>", "html.parser")
    new_table = soup.new_tag("table")
    # Copy attributes from original
    for attr, val in original_table.attrs.items():
        new_table[attr] = val
    for row in rows:
        new_table.append(_copy.copy(row))
    return new_table


def convert_table(table, base_url: str = "") -> str:
    """Convert HTML table to markdown table or text.

    Uses a single classification to determine table type:
    - BULLET: Tables with bullet chars in first column → bullet list
    - FOOTNOTE: Tables with (1), (a), * markers → "marker text" format
    - HEADER: Single-cell tables with section titles → markdown header
    - LAYOUT: Tables with multi-line content cells → section headers + bullet lists
    - DATA: Everything else → markdown table (the default)
    """
    # ── Chart-legend detection ──────────────────────────────────────
    # SEC filings embed bar / pie charts as <img> tags with adjacent
    # HTML tables that use tiny coloured cells as colour swatches
    # paired with label text (font-family: 'Gotham Narrow Book' /
    # similar, font-size ~5pt, rows of height 3pt).  The standard
    # table converter turns these into useless single-column markdown
    # tables.  Detect them early and emit a compact inline legend.
    legend = _extract_chart_legend(table)
    if legend is not None:
        return legend

    # Classify the table
    table_type = _classify_table(table)

    if table_type == "BULLET":
        result = _extract_bullet_list(table)
        if result:
            return result

    elif table_type == "FOOTNOTE":
        result = _extract_footnote_text(table)
        if result:
            return result

    elif table_type == "HEADER":
        result = _extract_header_text(table)
        if result:
            return result

    # For LAYOUT-classified tables (or unhandled types), try layout conversion.
    # Skip for DATA tables — they should always go through the data-table path.
    if table_type != "DATA":
        layout_result = _convert_layout_table(table, base_url)
        if layout_result:
            return layout_result

    # Default: process as data table (markdown table format)
    rows = table.find_all("tr")
    if not rows:
        return ""

    # Shared state: when year sub-headers start at position 0 (label
    # column), build_column_headers_from_colspan computes the offset
    # needed to align year positions with data-column positions.  The
    # semantic extraction code reads this to apply the same shift.
    _year_pos_shift = [0]  # mutable container so nested functions can write

    # First pass: Extract all rows WITHOUT merge/shift
    # We need to identify $ positions across all rows first
    raw_extracted_rows = []
    raw_extracted_colspans = []
    raw_row_has_th = []  # Track whether each row has <th> elements

    # Track grid positions occupied by cells with rowspan > 1 from
    # earlier rows.  Maps grid_col -> remaining row count.
    _rowspan_grid: dict[int, int] = {}

    for row in rows:
        cells = row.find_all(["td", "th"])
        row_data: list[str] = []
        row_with_colspan: list[tuple[str, int]] = []  # (text, colspan) pairs
        has_th = any(cell.name == "th" for cell in cells)

        grid_col = 0
        cell_idx = 0

        while cell_idx < len(cells):
            # Insert empty placeholders for positions occupied by
            # rowspan from earlier rows before placing the current cell.
            while grid_col in _rowspan_grid:
                row_data.append("")
                row_with_colspan.append(("", 1))
                grid_col += 1

            cell = cells[cell_idx]

            # Check for id attribute on cell - emit anchor if present
            cell_id = cell.get("id")
            anchor_prefix = ""
            if cell_id:
                anchor_prefix = f'<a id="{cell_id}"></a>'

            # For table cells, extract text while preserving links
            # but without the full recursive processing that introduces newlines
            text = _extract_cell_text(cell, base_url)

            # Clean up text - remove zero-width spaces and normalize whitespace
            text = text.replace("\u200b", "")
            text = text.replace("\xa0", " ")  # Non-breaking space
            text = re.sub(r"\s+", " ", text)
            text = text.strip()
            text = text.replace("|", "\\|")  # Escape pipes
            # Prepend anchor if cell had an id
            if anchor_prefix:
                text = anchor_prefix + text

            # Handle colspan and rowspan
            colspan = int(cell.get("colspan", 1) or 1)
            rowspan = int(cell.get("rowspan", 1) or 1)

            row_data.append(text)
            row_with_colspan.append((text, colspan))

            # Register this cell's grid positions for future rows
            if rowspan > 1:
                for _c in range(colspan):
                    _rowspan_grid[grid_col + _c] = rowspan

            for _ in range(colspan - 1):
                row_data.append("")

            grid_col += colspan
            cell_idx += 1

        # Fill any trailing positions still occupied by rowspan
        while grid_col in _rowspan_grid:
            row_data.append("")
            row_with_colspan.append(("", 1))
            grid_col += 1

        raw_extracted_rows.append(row_data)
        raw_extracted_colspans.append(row_with_colspan)
        raw_row_has_th.append(has_th)

        # Decrement rowspan counts; drop positions that have expired.
        _rowspan_grid = {pos: rem - 1 for pos, rem in _rowspan_grid.items() if rem > 1}

    # Identify positions that have currency prefixes ($, €, £) in ANY row.
    # These are the only positions where "empty + numeric" shift should apply.
    _CURRENCY_PREFIXES = {
        "$",
        "$(",
        "($",
        "$-",
        "€",
        "€(",
        "(€",
        "€-",
        "£",
        "£(",
        "(£",
        "£-",
    }
    dollar_positions = set()
    for row_data in raw_extracted_rows:
        for i, cell in enumerate(row_data):
            cell_stripped = strip_all(cell)
            if cell_stripped in _CURRENCY_PREFIXES:
                dollar_positions.add(i)

    # Extract all rows, preserving colspan info for headers
    data = []
    raw_rows_with_colspan = []  # For header detection - stores (text, colspan) pairs
    row_has_th_flags = []  # Track which rows have <th> elements
    for row_idx, (row_data, row_with_colspan, has_th) in enumerate(
        zip(raw_extracted_rows, raw_extracted_colspans, raw_row_has_th)
    ):
        # Merge currency prefix cells with their following value cells.
        # SEC tables often have $ in one cell and the number in the next.
        # 20-F filings frequently use € with colspan=3, placing the number
        # up to 3 positions away after empty expansion cells.
        merged_row = []
        merged_row_with_colspan = []
        i = 0
        while i < len(row_data):
            cell = strip_all(row_data[i])
            # Check if this is a currency prefix cell ($, €, £, etc.)
            if cell in _CURRENCY_PREFIXES and i + 1 < len(row_data):
                # Look ahead up to 3 positions for the number
                # (currency cell may have colspan>1 producing empty gaps)
                _num_re = re.compile(r"^\(?\s*[\d,]+\.?\d*\s*\)?%?$")
                _found_offset = None
                for _look in range(1, min(4, len(row_data) - i)):
                    _ahead = strip_all(row_data[i + _look])
                    if _ahead and _num_re.match(_ahead):
                        _found_offset = _look
                        break
                    if _ahead:  # non-empty non-numeric → stop
                        break
                if _found_offset is not None:
                    merged_val = cell + strip_all(row_data[i + _found_offset])
                    merged_row.append(merged_val)
                    # Add empty placeholders for all consumed cells
                    for _ in range(_found_offset):
                        merged_row.append("")
                    # Preserve colspan tracking for all consumed cells
                    for j in range(_found_offset + 1):
                        if i + j < len(row_with_colspan):
                            merged_row_with_colspan.append(row_with_colspan[i + j])
                    i += _found_offset + 1
                    continue
            # Handle rows WITHOUT currency prefix: empty cell followed by
            # a numeric value.  Secondary data rows may omit the currency
            # symbol shown on the first row.  Shift the value to the
            # currency position to keep alignment.  Also use look-ahead
            # (up to 3 cells) for €-style tables with colspan>1 gaps.
            elif cell == "" and i + 1 < len(row_data) and i in dollar_positions:
                _num_re2 = re.compile(r"^\(?\s*[\d,]+\.?\d*\s*\)?%?$")
                _found_offset2 = None
                for _look2 in range(1, min(4, len(row_data) - i)):
                    _ahead2 = strip_all(row_data[i + _look2])
                    if _ahead2 and _num_re2.match(_ahead2):
                        _found_offset2 = _look2
                        break
                    if _ahead2:
                        break
                if _found_offset2 is not None:
                    merged_row.append(strip_all(row_data[i + _found_offset2]))
                    for _ in range(_found_offset2):
                        merged_row.append("")
                    for j in range(_found_offset2 + 1):
                        if i + j < len(row_with_colspan):
                            merged_row_with_colspan.append(row_with_colspan[i + j])
                    i += _found_offset2 + 1
                    continue
            merged_row.append(row_data[i])
            if i < len(row_with_colspan):
                merged_row_with_colspan.append(row_with_colspan[i])
            i += 1

        row_data = merged_row  # noqa
        row_with_colspan = merged_row_with_colspan  # noqa

        # Merge footnote cells with the ROW LABEL (first non-empty cell)
        # SEC tables have footnote markers like <sup>12</sup> in their own cells
        # These belong on the label, not on data values
        footnote_merged_row = []
        collected_footnotes = []
        label_index = -1  # Track which cell is the row label

        for i, cell_text in enumerate(row_data):
            # Check if this cell is ONLY a superscript footnote
            if re.match(r"^\s*<sup>\d{1,3}</sup>\s*$", cell_text):
                # Collect footnotes to append to label later
                collected_footnotes.append(cell_text)
            else:
                footnote_merged_row.append(cell_text)
                # First non-empty cell is the label
                if label_index == -1 and cell_text.strip():
                    label_index = len(footnote_merged_row) - 1

        # Append all collected footnotes to the row label
        if collected_footnotes and label_index >= 0:
            footnote_merged_row[label_index] = footnote_merged_row[
                label_index
            ] + "".join(collected_footnotes)

        row_data = footnote_merged_row  # noqa

        if any(row_data):  # Skip empty rows
            data.append(row_data)
            raw_rows_with_colspan.append(row_with_colspan)
            row_has_th_flags.append(has_th)

    if not data:
        return ""

    # Filter out page footer tables
    if len(data) <= 2:
        non_empty = [c for c in data[0] if c.strip()]
        if len(non_empty) == 2:
            first_cell = non_empty[0].strip()
            second_cell = non_empty[1].strip()
            first_lower = first_cell.lower()
            second_lower = second_cell.lower()
            form_keywords = ["form 10-", "10-k", "10-q", "annual report"]
            if (
                first_cell.isdigit() and any(kw in second_lower for kw in form_keywords)
            ) or (
                second_cell.isdigit() and any(kw in first_lower for kw in form_keywords)
            ):
                return ""  # Skip page footer

    # Check if this is a section header table (single cell with TOC anchor)
    # Header like: <td id="toc..."><div style="font-weight:bold">Section Title</div></td>
    if len(data) == 1 and len([c for c in data[0] if c.strip()]) == 1:
        cell_text = [c for c in data[0] if c.strip()][0]
        # Check if it has a TOC anchor
        if '<a id="toc' in cell_text or '<a id="TOC' in cell_text:
            # Extract the text after the anchor
            text_match = re.search(r"</a>(.*)", cell_text)
            anchor_match = re.search(r'(<a id="[^"]+"></a>)', cell_text)
            if text_match and anchor_match:
                anchor = anchor_match.group(1)
                header_text = text_match.group(1).strip()
                if header_text:
                    return f"\n\n{anchor}\n\n### {header_text}\n\n"

    # Check if this is a bullet-list layout table
    # Must have actual bullet characters, not just empty cells
    is_bullet_list = False
    bullet_items = []
    for row in data:
        non_empty = [c for c in row if c.strip()]
        if len(non_empty) == 2 and non_empty[0] in BULLET_CHARS:
            # Actual bullet + text pattern
            bullet_items.append(non_empty[1])
            is_bullet_list = True
        elif len(non_empty) == 1 and is_bullet_list:
            # Continuation of bullet list (single items after we've seen bullets)
            bullet_items.append(non_empty[0])
        elif len(non_empty) >= 1 and not is_bullet_list:
            # Single row with content but not a bullet pattern
            # Join all non-empty cells as text (preserves both image and text)
            if len(data) == 1:
                return " ".join(non_empty)
            break
        else:
            is_bullet_list = False
            break

    if is_bullet_list and bullet_items:
        return "\n".join(f"- {item}" for item in bullet_items)

    # Normalize column count
    max_cols = max(len(row) for row in data)
    for row in data:
        while len(row) < max_cols:
            row.append("")

    # Clean up financial table formatting

    data = clean_table_cells(data)

    # Normalize financial values to compact format.
    # SEC filings use spacer elements between $ signs, parentheses, and
    # numbers, producing inconsistent formats like "$ 1,787" vs "$1,787"
    # or "( 135 )" vs "(135)".  Normalize everything to compact form.
    data = _normalize_financial_rows(data)

    # Merge consecutive rows that contain split text (e.g., "(in millions, except per" + "share amounts)")
    # This happens when HTML has multi-line text split across separate TR elements

    data, raw_rows_with_colspan = merge_split_rows(data, raw_rows_with_colspan)

    # Merge cells that contain split values within each row
    # Old SEC HTML often splits negative numbers like "(306" and ")" across cells
    # and puts footnote markers like "(1)" in separate cells

    data = merge_split_cells(data)

    # Normalize column count after cleaning
    if data:
        max_cols = max(len(row) for row in data)
        for row in data:
            while len(row) < max_cols:
                row.append("")

    # Remove columns that are completely empty

    # Step 1: Extract period headers from header rows

    # Step 2: Parse each row semantically - first text is label, numbers are values

    # Detect multi-level headers directly from DATA (not raw_rows_with_colspan)
    # This handles SEC tables where categories are stacked vertically:
    #   Row: EQUIPMENT | FINANCIAL | | | ...
    #   Row: OPERATIONS | SERVICES | ELIMINATIONS | CONSOLIDATED | ...
    #   Row: 2025 | 2024 | 2023 | 2025 | 2024 | 2023 | ...

    # Try to detect multi-index headers from data
    multiindex_result = detect_and_merge_multiindex_headers(data)

    if multiindex_result[0] and len(multiindex_result[0]) >= 1:
        header_layers, data_start_idx, num_periods = multiindex_result
        is_financial_periods = True
        header_row_count = data_start_idx
    else:
        # Fall back to original approach
        header_layers, extracted_header_count = extract_periods_from_rows(
            raw_rows_with_colspan, row_has_th_flags, _year_pos_shift
        )

        num_periods = 0

        if header_layers:
            # Count columns that have content in ANY header layer, but
            # collapse adjacent positions with identical composite text
            # (from colspan expansion).  E.g., "2025" at positions 3,4,5
            # from a cs=3 header counts as ONE period, not three.
            max_cols = max(len(layer) for layer in header_layers)
            num_periods = 0
            prev_key = None
            for col_idx in range(1, max_cols):  # Skip first col (label)
                key_parts = []
                has_content = False
                for layer in header_layers:
                    text = layer[col_idx].strip() if col_idx < len(layer) else ""
                    key_parts.append(text)
                    if text:
                        has_content = True
                if has_content:
                    key = "|".join(key_parts)
                    if key != prev_key:
                        num_periods += 1
                    prev_key = key
                else:
                    prev_key = None  # Reset on empty columns

            # When all header layers have the same size they are already
            # compact (from the flat-header / multi-category-row path).
            # Empty trailing columns still represent real data columns
            # (e.g., a total column with no header text), so trust the
            # layer size as the minimum column count.
            layer_sizes = set(len(hl) for hl in header_layers)

            if len(layer_sizes) == 1:
                layers_cols = layer_sizes.pop() - 1  # subtract label col
                num_periods = max(num_periods, layers_cols)

        # Check if headers are financial periods (years, dates, "months ended",
        # or maturity-bucket labels like "0 - 6 Months" / "1 - 5 Years")
        is_financial_periods = False

        if header_layers:
            for layer in header_layers:
                for h in layer:
                    if re.search(r"\b(19|20)\d{2}\b", h):  # Has a year
                        is_financial_periods = True
                        break
                    if re.search(
                        r"(months?\s+ended|year\s+ended|quarter|as\s+of)", h, re.I
                    ):
                        is_financial_periods = True
                        break
                    # Maturity-bucket labels: "0 - 6 Months", "1 - 5 Years",
                    # "10 Years or Greater", "Less than 1 Year", etc.
                    if re.search(
                        r"\d+\s*[-\u2013\u2014]\s*\d+\s*(months?|years?)"
                        r"|\d+\s+(months?|years?)(\s+or\s+(greater|more|less))?"
                        r"|less\s+than\s+\d+\s+(months?|years?)",
                        h,
                        re.I,
                    ):
                        is_financial_periods = True
                        break

                if is_financial_periods:
                    break

        # Use extracted_header_count if available
        header_row_count = extracted_header_count

    # These need special handling to merge headers and align columns

    # Try equity statement processing first
    if is_equity_statement_table(data):
        equity_result, equity_header_count = process_equity_statement_table(
            data, raw_rows_with_colspan
        )
        if equity_result:
            data = equity_result
            num_header_rows = equity_header_count
            # Skip the usual processing - go directly to markdown output
            if data and data[0]:
                max_cols = max(len(row) for row in data) if data else 0
                lines = []
                for i, row in enumerate(data):
                    while len(row) < max_cols:
                        row.append("")
                    clean_row = []
                    for cell in row:
                        clean_cell = re.sub(r"[\r\n]+", " ", cell)
                        # Remove <br>/<BR> tags from header cells (first few rows)
                        # num_header_rows is equity_header_count here
                        if i < max(num_header_rows, 2):
                            clean_cell = re.sub(r"<[Bb][Rr]\s*/?>", " ", clean_cell)
                        clean_cell = re.sub(r" +", " ", clean_cell).strip()
                        clean_row.append(clean_cell)
                    line = "| " + " | ".join(clean_row) + " |"
                    lines.append(line)
                    # Separator after FIRST row only (markdown requirement)
                    if i == 0:
                        lines.append("|" + "|".join(["---"] * max_cols) + "|")
                return "\n".join(lines)

    # Build output table
    new_data = []

    # Helper to check if a row from data array is a header/title row (should be skipped)
    has_meaningful_headers = False
    has_financial_header_terms = False
    if header_layers:
        all_header_text = " ".join(h for layer in header_layers for h in layer)

        for layer in header_layers:
            # Check for multi-word headers that indicate merged vertical labels
            for _h in layer:
                h = _h.strip()
                # Multi-word headers (e.g., "Retail Notes & Financing Leases")
                if h and len(h.split()) >= 2 and not re.match(r"^(19|20)\d{2}$", h):
                    has_meaningful_headers = True
                    break
            if has_meaningful_headers:
                break

        # Check for financial terms in headers that indicate structured financial table
        # These terms indicate the table should be parsed semantically even without years
        financial_header_terms = [
            r"\bshares?\b",
            r"\bprice\b",
            r"\bvalue\b",
            r"\bterm\b",
            r"\bexercise\b",
            r"\bgranted?\b",
            r"\bvested\b",
            r"\bforfeited?\b",
            r"\b(?:thousands?|millions?|billions?)\b",
            r"\bper\s+share\b",
            r"\baggregate\b",
            r"\bintrinsic\b",
            r"\bcontractual\b",
            r"\bremaining\b",
            r"\bweighted[-\s]?average\b",
            r"\bexercisable\b",
            r"\bAmount\b",
            r"\bCredit\b",
            r"\bDebit\b",
            r"\bBalance\b",
            r"\bReceivables?\b",
            r"\bLeases?\b",
            r"\bFinancing\b",
            r"\bWholesale\b",
            # Maturity / time-duration bucket labels
            r"\bmonths?\b",
            r"\byears?\b",
            r"\bor\s+greater\b",
            r"\bmaturity\b",
        ]
        has_financial_header_terms = any(
            re.search(term, all_header_text, re.I) for term in financial_header_terms
        )

    has_mixed_headers = False

    if header_layers and len(header_layers) == 1:
        # Single header row - check if it mixes years with non-year columns.
        # "Mixed" means the non-year columns OUTNUMBER the year/year-range
        # columns, implying the headers are different dimensions (e.g.,
        # "2024 | 2023 | % Change | Useful Lives") rather than a year-period
        # table with a summary column ("2008 | 2009-2010 | ... | Total").
        last_layer = header_layers[-1]
        year_cols: int = 0
        non_year_cols: int = 0

        for _h in last_layer[1:]:  # Skip label column
            h = _h.strip()
            if not h:
                continue
            if re.search(r"\b(19|20)\d{2}\b", h):
                year_cols += 1
            else:
                non_year_cols += 1

        # Mixed only when non-year columns are the majority, or there are NO
        # year columns at all AND the headers don't form a cohesive maturity-
        # bucket set (e.g. "0 - 6 Months", "1 - 5 Years", "Total").
        # Maturity-bucket tables look like year-range tables but use time
        # durations instead of calendar years — they are NOT truly mixed.
        _maturity_bucket_re = re.compile(
            r"^\s*("
            r"\d+\s*[-\u2013\u2014]\s*(\d+|\w+)\s*(months?|years?)"
            r"|\d+\s+(months?|years?)(\s+or\s+(greater|more|less))?"
            r"|less\s+than\s+\d+"
            r"|or\s+(greater|more|less)"
            r"|n/?a"
            r"|total"
            r"|thereafter"
            r")\s*$",
            re.I,
        )
        if year_cols == 0:
            # All non-empty, non-label headers are maturity buckets → not mixed
            _all_maturity = all(
                _maturity_bucket_re.match(h) for h in last_layer[1:] if h.strip()
            )
            if not _all_maturity:
                has_mixed_headers = True
        elif non_year_cols > year_cols:
            has_mixed_headers = True

    use_semantic_parsing = (
        is_financial_periods and header_layers and not has_mixed_headers
    )

    if (
        not use_semantic_parsing
        and header_layers
        and has_meaningful_headers
        and has_financial_header_terms
        and not has_mixed_headers
    ):
        # Treat merged vertical headers with financial terms as financial tables
        use_semantic_parsing = True

    # Guard: verify num_periods matches the actual data width.
    # Complex multi-index headers (e.g., "Economic value sensitivity" spanning
    # date sub-headers spanning country sub-sub-headers) can cause the header
    # detection to undercount periods.  When data rows consistently have more
    # non-empty values than num_periods, the header structure is wrong and we
    # must fall back to positional (non-semantic) rendering.
    if use_semantic_parsing and num_periods > 0 and header_row_count < len(data):
        _val_re = re.compile(
            r"^[+\-]?[\$\u20ac]?\s*\(?[\$\u20ac]?\s*[\d,]+\.?\d*\s*\)?\s*[*%]*(pts)?$"
        )
        _dash_vals = {
            "\u2014",
            "\u2013",
            "-",
            "$\u2014",
            "$\u2013",
            "$-",
            "\u20ac\u2014",
            "\u20ac\u2013",
            "\u20ac-",
            "N/A",
            "n/a",
            "NM",
            "nm",
        }
        for _dr in data[header_row_count:]:
            _n = sum(
                1
                for c in _dr[1:]
                if c.strip() and (_val_re.match(c.strip()) or c.strip() in _dash_vals)
            )
            if _n > num_periods * 2:
                use_semantic_parsing = False
                break

    if use_semantic_parsing:
        # For multi-level headers, derive column positions from year cells
        # in the expanded data array. This enables position-aware extraction
        # for sparse data rows (where values have gaps between columns).
        header_col_positions = None

        if header_layers and len(header_layers) >= 2:
            year_positions = []
            for row_idx in range(min(header_row_count, len(data))):
                for col_idx, cell in enumerate(data[row_idx]):
                    cell_clean = cell.strip().strip("\u200b").strip()
                    # Strip footnote markers
                    cell_stripped = re.sub(r"[*†‡§+]+$", "", cell_clean)

                    if (
                        cell_stripped
                        and re.match(r"^(19|20)\d{2}$", cell_stripped)
                        and col_idx not in year_positions
                    ):
                        year_positions.append(col_idx)

            year_positions.sort()

            if len(year_positions) == num_periods and num_periods > 0:
                # When year headers start at column 0 (label column),
                # they are offset from data values.  Apply the same shift
                # that was computed during header extraction so positions
                # align with actual data columns.
                if year_positions[0] == 0 and _year_pos_shift[0] > 0:
                    year_positions = [p + _year_pos_shift[0] for p in year_positions]
                header_col_positions = year_positions

            # When year_positions alone don't cover all periods (e.g.,
            # tables with "% Change" or "Basis Point Change" columns
            # alongside date columns), augment with positions of other
            # non-empty header texts from the header data rows.  Exclude
            # category texts (from Layer 0) and financial data values.
            if (
                not header_col_positions
                and year_positions
                and len(year_positions) < num_periods
                and num_periods > 0
            ):
                category_texts_set: set[str] = set()
                if header_layers:
                    for _h in header_layers[0]:
                        _ht = _h.strip()
                        if _ht:
                            category_texts_set.add(_ht)

                all_leaf_positions: set[int] = set(year_positions)
                for row_idx in range(min(header_row_count, len(data))):
                    for col_idx, cell in enumerate(data[row_idx]):
                        if col_idx == 0 or col_idx in all_leaf_positions:
                            continue
                        cell_clean = cell.strip().strip("\u200b").strip()
                        cell_stripped = re.sub(r"[*†‡§+]+$", "", cell_clean)
                        if not cell_stripped:
                            continue
                        # Skip years (already collected)
                        if re.match(r"^(19|20)\d{2}$", cell_stripped):
                            continue
                        # Skip financial data values
                        if re.match(
                            r"^[\$]?\s*[\(\)]?\s*[\d,]+\.?\d*\s*[\)\%]?$",
                            cell_stripped,
                        ):
                            continue
                        # Skip category header texts (from colspan expansion)
                        if cell_stripped in category_texts_set:
                            continue
                        # Skip descriptor text in parentheses
                        if cell_stripped.startswith("(") and re.search(
                            r"(million|except|thousand|billion|percent)",
                            cell_stripped,
                            re.I,
                        ):
                            continue
                        all_leaf_positions.add(col_idx)

                sorted_all = sorted(all_leaf_positions)
                if len(sorted_all) == num_periods:
                    header_col_positions = sorted_all

            # For tables with text sub-headers (no year values),
            # dollar signs mark the start of each data column
            if not header_col_positions and dollar_positions:
                sorted_dollar = sorted(dollar_positions)

                if len(sorted_dollar) == num_periods and num_periods > 0:
                    header_col_positions = sorted_dollar

            if not header_col_positions and header_layers:
                # Build a list of (col_idx_in_layer, text, layer_idx) for all
                # non-empty header positions, then deduplicate by column index.
                all_header_entries = []  # (col_pos, text, layer_idx)

                for li, layer in enumerate(header_layers):
                    for col_pos in range(1, len(layer)):
                        h = layer[col_pos].strip()

                        if h:
                            all_header_entries.append((col_pos, h, li))

                # Deduplicate
                col_to_text: dict = {}

                for col_pos, h, li in all_header_entries:
                    if col_pos not in col_to_text or li > col_to_text[col_pos][1]:
                        col_to_text[col_pos] = (h, li)

                sub_texts = [col_to_text[cp][0] for cp in sorted(col_to_text.keys())]

                if len(sub_texts) == num_periods and num_periods > 0:
                    found_positions: list[int] = []
                    used_cols: set[int] = set()

                    for target in sub_texts:
                        matched = False
                        for row_idx in range(min(header_row_count, len(data))):
                            for col_idx, cell in enumerate(data[row_idx]):
                                if col_idx in used_cols:
                                    continue

                                if cell.strip() == target:
                                    found_positions.append(col_idx)
                                    used_cols.add(col_idx)
                                    matched = True
                                    break

                            if matched:
                                break

                    if len(found_positions) == num_periods:
                        header_col_positions = sorted(found_positions)

        # Single-layer header fallback: find where each unique header text
        # first appears in the raw (colspan-expanded) data header rows.
        # E.g., header_layers=[['', '2025', '2024', '% Change']] and the
        # raw data row is ['', '', '2025', '2025', '', '2024', '2024', '',
        # '% Change', ''].  We need header_col_positions=[2, 5, 8] so the
        # position-aware extraction maps data cells to correct columns.
        if not header_col_positions and header_layers and len(header_layers) == 1:
            unique_headers = [h for h in header_layers[0][1:] if h.strip()]
            if len(unique_headers) == num_periods and num_periods > 0:
                found_positions = []
                used_cols = set()
                for target in unique_headers:
                    for row_idx in range(min(header_row_count, len(data))):
                        matched = False
                        for col_idx, cell in enumerate(data[row_idx]):
                            if col_idx in used_cols:
                                continue
                            if cell.strip() == target:
                                found_positions.append(col_idx)
                                used_cols.add(col_idx)
                                matched = True
                                break
                        if matched:
                            break
                if len(found_positions) == num_periods:
                    header_col_positions = found_positions

        if header_layers:
            for layer in header_layers:
                if len(layer) == num_periods + 1:
                    new_data.append(layer[:])
                    continue

                # Pad on the right to match the expected column count rather than collapsing.
                if len(layer) <= num_periods + 1:
                    padded = layer[:] + [""] * (num_periods + 1 - len(layer))
                    new_data.append(padded[: num_periods + 1])
                    continue

                # Collapse adjacent identical texts from colspan expansion.
                # E.g., ['', '', '', '2025', '2025', '2025', '', '', '',
                #         '2024', '2024', '2024', ...]
                # becomes ['', '2025', '2024', '2023']
                collapsed = []
                prev_text = None
                for idx, text in enumerate(layer):
                    t = text.strip()

                    if idx == 0:
                        # Always keep the label column as-is
                        collapsed.append(text)
                        prev_text = None
                        continue

                    if t:
                        if t != prev_text:
                            collapsed.append(text)
                        prev_text = t
                    else:
                        prev_text = None  # Reset on empty

                # Ensure it has the right number of columns
                while len(collapsed) < num_periods + 1:
                    collapsed.append("")
                new_data.append(collapsed[: num_periods + 1])

        # Process data rows - use header_row_count to skip header rows
        # Use a two-pass approach: first extract values into *groups*
        # per header range, then flatten.  This correctly interleaves
        # sub-column values (e.g. absolute change + percentage under a
        # single "2025 vs. 2024" header) instead of appending overflows
        # to the end.
        _extracted_rows: list[tuple] = []
        _has_sub_columns = False
        _num_header_entries = len(new_data)  # header rows already added

        for i, row in enumerate(data):
            # Skip rows before data starts (headers already extracted)
            if i < header_row_count:
                continue

            # Also skip any remaining header-like rows by content
            if is_data_row_header(row):
                continue

            if header_col_positions:
                # Position-aware extraction: map data cells to headers
                # by checking which header column range each cell falls in
                ranges = []

                for hi, pos in enumerate(header_col_positions):
                    end = (
                        header_col_positions[hi + 1]
                        if hi + 1 < len(header_col_positions)
                        else len(row)
                    )
                    ranges.append((pos, end))

                label_parts = []
                value_groups: list[list[str]] = [[] for _ in range(num_periods)]

                for col_idx, cell_text in enumerate(row):
                    cell_clean = cell_text.strip().strip("\u200b").strip()

                    if not cell_clean or cell_clean in ("$", "\u20ac"):
                        continue
                    # Before first header position = label column
                    if col_idx < header_col_positions[0]:
                        label_parts.append(cell_clean)
                        continue

                    # Find which header range this cell falls into
                    for hi, (start, end) in enumerate(ranges):
                        if start <= col_idx < end:
                            # Numeric/dash values go as data
                            if re.match(
                                r"^[+\-]?[\$\u20ac]?\s*\(?[\$\u20ac]?\s*[\d,]+\.?\d*\s*\)?\s*[*%]*(pts)?$",
                                cell_clean,
                            ) or cell_clean in (
                                "\u2014",
                                "\u2013",
                                "-",
                                "$\u2014",
                                "$\u2013",
                                "$-",
                                "$ \u2014",
                                "$ \u2013",
                                "$ -",
                                "\u20ac\u2014",
                                "\u20ac\u2013",
                                "\u20ac-",
                                "\u2014%",
                                "\u2013%",
                                "-%",
                                "\u2014 %",
                                "\u2013 %",
                                "- %",
                                "N/A",
                                "n/a",
                                "NM",
                                "nm",
                            ):
                                value_groups[hi].append(cell_clean)
                                if len(value_groups[hi]) > 1:
                                    _has_sub_columns = True
                            elif (
                                re.match(
                                    r"^(bps?|pts?|pps?|x)$",
                                    cell_clean,
                                    re.I,
                                )
                                and value_groups[hi]
                            ):
                                # Unit suffix (e.g. "bps", "pts") that
                                # belongs to the preceding numeric value
                                # in the same header range — merge rather
                                # than creating a spurious extra column.
                                value_groups[hi][
                                    -1
                                ] = f"{value_groups[hi][-1]} {cell_clean}"
                            elif not label_parts:
                                # Non-numeric before any data = part of label
                                label_parts.append(cell_clean)
                            else:
                                value_groups[hi].append(cell_clean)
                                if len(value_groups[hi]) > 1:
                                    _has_sub_columns = True

                            break

                label = " ".join(label_parts) if label_parts else None
                _extracted_rows.append((label, value_groups))
            else:
                label, values = parse_row_semantic(row, num_periods)
                # Wrap each value as a single-element group
                _extracted_rows.append((label, [[v] if v else [] for v in values]))

        # Determine max sub-column count per period across all rows.
        _max_group_sizes = [1] * num_periods
        if _has_sub_columns:
            for _, groups in _extracted_rows:
                for hi in range(min(num_periods, len(groups))):
                    _max_group_sizes[hi] = max(_max_group_sizes[hi], len(groups[hi]))

        _actual_periods = sum(_max_group_sizes)

        # Flatten each row's value groups into a flat value list.
        for label, groups in _extracted_rows:
            if label is None and all(not g for g in groups):
                continue

            flat_values: list[str] = []
            for hi in range(num_periods):
                g = list(groups[hi]) if hi < len(groups) else []
                while len(g) < _max_group_sizes[hi]:
                    g.append("")
                flat_values.extend(g)

            while len(flat_values) < _actual_periods:
                flat_values.append("")

            new_data.append([label or ""] + flat_values)

        # Expand header layers if sub-columns were detected.
        if _has_sub_columns and _actual_periods > num_periods:
            for li in range(_num_header_entries):
                old_hdr = new_data[li]
                expanded = [old_hdr[0]]  # label column
                for hi in range(num_periods):
                    h = old_hdr[hi + 1] if hi + 1 < len(old_hdr) else ""
                    expanded.append(h)
                    for _ in range(_max_group_sizes[hi] - 1):
                        expanded.append("")
                while len(expanded) < _actual_periods + 1:
                    expanded.append("")
                new_data[li] = expanded
            num_periods = _actual_periods

        data = new_data
        num_header_rows = len(header_layers) if header_layers else 1

        # Re-align single-layer period headers to match actual data column
        # positions.  When a year header like "September 2025" (cs=6) spans
        # multiple physical data columns (e.g. amount + percentage), the
        # collapsed header row places it at col 1 while "December 2024" lands
        # at col 2 — even though the December data starts at col 3.
        # Fix: scan the first data row for dollar-prefixed values ($xxx) and
        # move each period name to the column where its period's $ amount sits.
        if (
            header_layers
            and len(header_layers) == 1
            and num_periods >= 2
            and len(header_layers[0]) == num_periods + 1
            and len(data) > num_header_rows
        ):
            _period_names = [h for h in header_layers[0][1:] if h.strip()]
            if len(_period_names) == num_periods:
                _dollar_cols: list = []
                for _drow in data[num_header_rows:]:
                    _positions = [
                        ci for ci, c in enumerate(_drow) if c and c.startswith("$")
                    ]
                    if len(_positions) == num_periods:
                        _dollar_cols = _positions
                        break
                if _dollar_cols and max(_dollar_cols) >= num_periods:
                    # Only realign if dollar cols are NOT already sequential
                    # from 1..num_periods (which would mean no change needed)
                    _expected = list(range(1, num_periods + 1))
                    if _dollar_cols != _expected:
                        _max_dc = max(len(r) for r in data)
                        _new_hdr = [""] * _max_dc
                        for _pi, _pos in enumerate(_dollar_cols):
                            if _pos < _max_dc:
                                _new_hdr[_pos] = _period_names[_pi]
                        data[0] = _new_hdr

    elif has_mixed_headers and header_layers:
        # Mixed-header table (has non-year columns like "Useful Lives")
        header_part = data[:header_row_count]
        if is_financial_periods:
            filtered_rows = [
                row for row in data[header_row_count:] if not is_data_row_header(row)
            ]
        else:
            filtered_rows = list(data[header_row_count:])
        data = header_part + filtered_rows

        # Check if this is a simple flat table
        if header_row_count == 1:
            data = remove_empty_columns(data)
            data = collapse_repeated_headers(data)
            num_header_rows = 1
        else:
            # Multi-row header structure with mixed headers.
            header_part = data[:header_row_count]
            data_rows_only = data[header_row_count:]

            actual_header_rows = []
            for row in header_part:
                non_empty = [c for c in row if c.strip()]

                if len(non_empty) >= 2:
                    # Multiple cells with content → column-defining header
                    actual_header_rows.append(row)

            if not actual_header_rows:
                # Fallback: use the last header row
                actual_header_rows = [header_part[-1]]

            combined = actual_header_rows + data_rows_only
            combined = remove_empty_columns(combined)
            combined = collapse_repeated_headers(combined)

            data = combined
            num_header_rows = len(actual_header_rows)
    else:
        # Non-financial table - filter out header-like rows from data portion
        if header_row_count > 0:
            header_part = data[:header_row_count]
            filtered_rows = [
                row for row in data[header_row_count:] if not is_data_row_header(row)
            ]
            data = header_part + filtered_rows
        data = remove_empty_columns(data)
        # This handles tables where header has colspan=2 but data only fills one position
        data = collapse_repeated_headers(data)
        num_header_rows = 0

    if not data or not data[0]:
        return ""

    max_cols = max(len(row) for row in data) if data else 0
    lines = []

    for i, row in enumerate(data):
        while len(row) < max_cols:
            row.append("")
        # Ensure no cell contains newlines
        clean_row = []

        for cell in row:
            # Replace any newlines with space
            clean_cell = re.sub(r"[\r\n]+", " ", cell)
            # Remove <br>/<BR> tags from header cells (first few rows)
            # This handles multi-row headers where row 1 also has column names
            if i < max(num_header_rows, 2):
                clean_cell = re.sub(r"<[Bb][Rr]\s*/?>", " ", clean_cell)
            # Collapse multiple spaces
            clean_cell = re.sub(r" +", " ", clean_cell).strip()
            clean_row.append(clean_cell)

        line = "| " + " | ".join(clean_row) + " |"
        lines.append(line)
        # Add separator after the first header row only — this is standard markdown.
        # Additional header layers (Layer 1, Layer 2...) render as normal rows below
        # the separator, acting as visual sub-headers.
        if i == 0:
            lines.append("|" + "|".join(["---"] * max_cols) + "|")

    return "\n".join(lines)


def get_text_content(
    element, preserve_links_in_text: bool = False, base_url: str = ""
) -> str:
    """Get text from element, handling XBRL wrappers and preserving word boundaries.

    If preserve_links_in_text is True, converts <a> tags to markdown [text](href) format.
    """
    if isinstance(element, NavigableString):
        return str(element)

    texts = []
    for child in element.children:
        if isinstance(child, NavigableString):
            texts.append(str(child))
        elif child.name == "br":
            texts.append(" ")  # Treat line breaks as spaces
        elif child.name == "a" and preserve_links_in_text:
            # Convert link to markdown format
            href = child.get("href", "")
            link_text = child.get_text(strip=True)
            if href and link_text:
                # Keep anchor links as-is, resolve relative links
                if (
                    not href.startswith("#")
                    and base_url
                    and not href.startswith(("http://", "https://"))
                ):
                    href = urljoin(base_url, href)
                texts.append(f"[{link_text}]({href})")
            else:
                texts.append(link_text or "")
        elif child.name and child.name.startswith("ix:"):
            # XBRL wrapper - get its text content
            texts.append(child.get_text(separator=" "))
        else:
            texts.append(get_text_content(child, preserve_links_in_text, base_url))

    result_parts: list = []
    had_whitespace_separator = False

    for _t in texts:
        t = _t.replace("\xa0", " ")  # Normalize non-breaking spaces first

        if not t.strip():
            # This prevents split words like <b>INCOM</b><b>E</b> → "INCOM E"
            # while preserving spaces where <b>WORD1</b><b> </b><b>WORD2</b>.
            if result_parts:
                had_whitespace_separator = True
            continue

        if result_parts:
            last_char = result_parts[-1][-1] if result_parts[-1] else ""
            first_char = t[0] if t else ""

            if had_whitespace_separator:
                # Explicit whitespace between parts — add space unless
                # punctuation rules say not to
                if (
                    last_char not in NO_SPACE_AFTER
                    and first_char not in NO_SPACE_BEFORE
                ):
                    result_parts.append(" ")
                # Adjacent elements of the same type with no separator
                # (e.g. <b>INCOM</b><b>E</b>) are parts of one word.
            elif not (last_char.isalpha() and first_char.isalpha()) and (
                last_char not in NO_SPACE_AFTER and first_char not in NO_SPACE_BEFORE
            ):
                result_parts.append(" ")

            had_whitespace_separator = False

        result_parts.append(t)

    result = "".join(result_parts)
    # Collapse any remaining multiple spaces
    result = re.sub(r" +", " ", result)
    return result


# ============================================================================
# ABSOLUTE-POSITIONED LAYOUT REFLOW
# ============================================================================
# Some SEC filings (notably Canadian bank 40-F exhibits like TD) are
# generated from PDF-to-HTML converters that render every text fragment
# as an absolutely-positioned <div> with pixel left/top coordinates.
# These documents contain ZERO <table> tags and thousands of positioned
# divs.  The regular html_to_markdown converter cannot reconstruct
# paragraphs or tables from these.
#
# _reflow_absolute_layout detects such documents and rewrites the HTML
# into flowing <p> / <table> elements so the rest of the pipeline works.
# ============================================================================

# HTML entity map for quick decoding in the reflow function.
_REFLOW_ENTITIES: dict[str, str] = {
    "&#160;": " ",
    "&#8217;": "\u2019",
    "&#8216;": "\u2018",
    "&#8220;": "\u201c",
    "&#8221;": "\u201d",
    "&#8211;": "\u2013",
    "&#8212;": "\u2014",
    "&#8226;": "\u2022",
    "&#9679;": "\u25cf",
    "&#8230;": "\u2026",
    "&#8482;": "\u2122",
    "&#174;": "\u00ae",
    "&#169;": "\u00a9",
    "&amp;": "&",
    "&lt;": "<",
    "&gt;": ">",
    "&quot;": '"',
    "&#39;": "'",
    "&apos;": "'",
    "&nbsp;": " ",
}

# Regex to detect the "Page N" footer divs.
_PAGE_FOOTER_RE = re.compile(
    r"(?:Page\s+\d+|TD\s+BANK\s+GROUP)",
    re.IGNORECASE,
)


def _reflow_absolute_layout(html_content: str) -> str | None:
    """Rewrite position:absolute HTML into flowing HTML.

    Uses a *rule-based* approach: the Certent CDM (and similar PDF-to-HTML
    generators) encode table row separators as thin (≤ 2 px high), full-width
    (≥ 500 px) ``position:absolute`` divs.  These horizontal rules provide
    deterministic table detection — text fragments between consecutive rules
    belong to the same table, and their horizontal positions map to columns.

    Non-table text (paragraphs, headings, chart annotations) is rendered
    outside the rule-delimited zones.  When the page contains a side-by-side
    layout (body text on the left, chart on the right), the fragments are
    split into two columns so chart content doesn't pollute paragraph text.

    Returns the rewritten HTML string, or ``None`` if the document does
    not use an absolute-positioned layout and should be processed normally.
    """
    # Quick heuristic: is this an abs-positioned document?
    # Must have MANY absolute-positioned elements, very few <table> tags,
    # AND the characteristic Certent CDM id="aNN" text-fragment pattern.
    _sample = html_content[:50_000]
    _abs_count = len(re.findall(r"position:\s*absolute", _sample, re.I))
    _table_count = len(re.findall(r"<table\b", html_content[:200_000], re.I))
    if _abs_count < 30 or _table_count > 2:
        return None

    _abs_total = len(re.findall(r"position:\s*absolute", html_content, re.I))
    _div_total = len(re.findall(r"<div\b", html_content, re.I))
    if _div_total == 0 or _abs_total / _div_total < 0.4:
        return None

    # Require the Certent CDM text-fragment pattern: divs with
    # id="aNN" (numeric IDs) that carry the actual text content.
    # This is the hallmark of PDF-to-HTML absolute-positioned layouts.
    # Without this, normal filings with many absolute-positioned logos
    # or headers would be incorrectly rewritten.
    _text_frag_count = len(re.findall(r'<div[^>]+id="a\d+"', _sample, re.I))
    if _text_frag_count < 15:
        return None

    # ---- Parse page boundaries ----
    _page_re = re.compile(r'id="Page(\d+)"')
    page_boundaries = list(_page_re.finditer(html_content))
    if not page_boundaries:
        return None

    page_map: dict[int, int] = {int(m.group(1)): m.start() for m in page_boundaries}
    total_pages = max(page_map.keys())

    # ---- Regex toolbox ----
    _tag_re = re.compile(r"<[^>]+>")
    _bold_re = re.compile(r"font-weight:\s*bold", re.I)
    _fsize_re = re.compile(r"font-size:\s*([\d.]+)px", re.I)
    _content_re = re.compile(
        r'(.*?)(?=<div\s+id="a\d+"|<div\s+style="[^"]*position:\s*absolute)',
        re.S,
    )
    _content_end_re = re.compile(r"(.*?)</div>", re.S)

    def _decode_entities(text: str) -> str:
        for ent, ch in _REFLOW_ENTITIES.items():
            text = text.replace(ent, ch)
        text = re.sub(
            r"&#(\d+);",
            lambda m: chr(int(m.group(1))) if int(m.group(1)) < 0x10000 else "",
            text,
        )
        return text

    def _strip_tags(raw: str) -> str:
        return _decode_entities(_tag_re.sub("", raw)).strip()

    # ---- Per-page parser ----
    def _parse_page(
        page_num: int,
    ) -> tuple[list[float], list[tuple[float, float, str, bool, float]]]:
        """Extract horizontal rules and text fragments from a page.

        Returns ``(hrules, text_frags)`` where *hrules* is a sorted list
        of ``top`` positions of full-width rules and *text_frags* is a
        list of ``(top, left, text, bold, font_size)`` tuples.
        """
        p_start = page_map[page_num]
        p_end = page_map.get(page_num + 1, len(html_content))
        page_html = html_content[p_start:p_end]

        hrules: list[float] = []
        text_frags: list[tuple[float, float, str, bool, float]] = []

        for m in re.finditer(
            r'<div\s[^>]*?style="([^"]*position:\s*absolute[^"]*)"[^>]*>',
            page_html,
            re.I,
        ):
            style = m.group(1)

            left_m = re.search(r"left:([\d.]+)px", style)
            top_m = re.search(r"top:([\d.]+)px", style)
            if not (left_m and top_m):
                continue
            left = float(left_m.group(1))
            top = float(top_m.group(1))

            width_m = re.search(r"width:([\d.]+)px", style)
            height_m = re.search(r"height:([\d.]+)px", style)
            width = float(width_m.group(1)) if width_m else 0
            height = float(height_m.group(1)) if height_m else 0

            # Horizontal rule: thin + wide-enough + explicit dimensions.
            # Full-width rules (≥ 500 px) delimit major tables.
            # Medium rules (200–499 px) delimit smaller tables such as
            # "Fiscal Year 2026 Targets" boxes or split-page layouts.
            if height_m and width_m and height <= 2 and width >= 200:
                hrules.append(top)
                continue

            # Skip vertical rules (explicit narrow width, e.g. 1px bars)
            if width_m and width <= 2:
                continue
            # Skip coloured rectangles (chart bars) that have no text id
            if width_m and height_m and width > 5 and height > 5:
                div_tag = page_html[m.start() : m.end()]
                if not re.search(r'id="a\d+"', div_tag):
                    continue

            # Text fragment — must have id="aNN"
            div_tag = page_html[m.start() : m.end()]
            id_m = re.search(r'id="(a\d+)"', div_tag)
            if not id_m:
                continue

            rest = page_html[m.end() : m.end() + 2000]
            cm = _content_re.match(rest)
            if not cm:
                cm = _content_end_re.match(rest)
            if not cm:
                continue

            text = _strip_tags(cm.group(1))
            if not text:
                continue

            if _PAGE_FOOTER_RE.search(text) and top > 950:
                continue

            bold = bool(_bold_re.search(style))
            fs_m = _fsize_re.search(style)
            font_size = float(fs_m.group(1)) if fs_m else 10.0

            text_frags.append((top, left, text, bold, font_size))

        hrules = sorted(set(round(r, 1) for r in hrules))
        text_frags.sort()
        return hrules, text_frags

    # ---- Table-zone detection ----
    def _identify_table_zones(
        hrules: list[float],
    ) -> list[tuple[float, float]]:
        """Group consecutive full-width rules into table zones.

        Rules separated by < 300 px are considered part of the same table.
        Returns a list of ``(zone_top, zone_bottom)`` pairs.
        """
        if len(hrules) < 2:
            return []
        zones: list[tuple[float, float]] = []
        zone_start = hrules[0]
        zone_end = hrules[0]
        for i in range(1, len(hrules)):
            if hrules[i] - hrules[i - 1] < 300:
                zone_end = hrules[i]
            else:
                if zone_end > zone_start:
                    zones.append((zone_start, zone_end))
                zone_start = hrules[i]
                zone_end = hrules[i]
        if zone_end > zone_start:
            zones.append((zone_start, zone_end))
        return zones

    # ---- Dedup consecutive identical rows ----
    def _dedup_rows(
        rows: list[list[str]],
    ) -> list[list[str]]:
        """Remove consecutive duplicate rows (same text ignoring bold)."""
        if not rows:
            return rows
        _bold_tag = re.compile(r"</?b>")
        result = [rows[0]]
        for row in rows[1:]:
            prev_text = [_bold_tag.sub("", c) for c in result[-1]]
            cur_text = [_bold_tag.sub("", c) for c in row]
            if cur_text != prev_text:
                result.append(row)
            else:
                prev_bold = sum(1 for c in result[-1] if "<b>" in c)
                cur_bold = sum(1 for c in row if "<b>" in c)
                if cur_bold > prev_bold:
                    result[-1] = row
        return result

    # ---- Build table from a rule-delimited zone ----
    def _build_table_from_zone(
        frags: list[tuple[float, float, str, bool, float]],
        rules: list[float],
    ) -> str:
        if not frags or len(rules) < 2:
            return ""

        rules = sorted(rules)

        # Build row bands: text between consecutive rules
        row_bands: list[list[tuple[float, float, str, bool, float]]] = []
        for i in range(len(rules) - 1):
            band_top = rules[i]
            band_bot = rules[i + 1]
            band_frags = [f for f in frags if band_top - 2 <= f[0] <= band_bot + 2]
            if band_frags:
                row_bands.append(band_frags)

        if not row_bands:
            return ""

        # Determine column positions (cluster left coordinates ±20 px)
        all_lefts: list[float] = []
        for band in row_bands:
            for _, lf, _, _, fs in band:
                if fs >= 7:
                    all_lefts.append(lf)
        if not all_lefts:
            return ""

        all_lefts.sort()
        cols: list[float] = []
        col_n: list[int] = []
        for lf in all_lefts:
            merged = False
            for ci in range(len(cols)):
                if abs(lf - cols[ci]) <= 20:
                    cols[ci] = (cols[ci] * col_n[ci] + lf) / (col_n[ci] + 1)
                    col_n[ci] += 1
                    merged = True
                    break
            if not merged:
                cols.append(lf)
                col_n.append(1)
        cols.sort()
        ncols = len(cols)

        # Build raw row data
        raw_rows: list[list[str]] = []
        for band in row_bands:
            band.sort()
            lines: list[list[tuple[float, str, bool, float]]] = []
            cur_top = band[0][0]
            cur: list[tuple[float, str, bool, float]] = []
            for top, lf, text, bold, fs in band:
                if abs(top - cur_top) <= 3:
                    cur.append((lf, text, bold, fs))
                else:
                    if cur:
                        lines.append(cur)
                    cur_top = top
                    cur = [(lf, text, bold, fs)]
            if cur:
                lines.append(cur)

            for line in lines:
                # Skip superscript footnote markers
                main = [
                    (lv, t, b, f)
                    for lv, t, b, f in line
                    if not (f < 7 and re.match(r"^\d[\d,]*$", t.strip()))
                ]
                if not main:
                    continue

                cells = [""] * ncols
                bolds = [False] * ncols
                for lf, text, bold, _fs in main:
                    best = 0
                    best_dist = abs(lf - cols[0])
                    for ci in range(1, ncols):
                        d = abs(lf - cols[ci])
                        if d < best_dist:
                            best_dist = d
                            best = ci
                    if cells[best]:
                        cells[best] += " " + text
                    else:
                        cells[best] = text
                    if bold:
                        bolds[best] = True

                formatted: list[str] = []
                for ci in range(ncols):
                    c = _html_escape(cells[ci])
                    if bolds[ci] and c:
                        c = f"<b>{c}</b>"
                    formatted.append(c)
                raw_rows.append(formatted)

        raw_rows = _dedup_rows(raw_rows)
        if not raw_rows:
            return ""

        # ---- Pre-merge currency-symbol cells (per-row) ----
        # Absolute-positioned layouts produce "$" / "€" / "£" as
        # separate fragments in their own column.  For each row,
        # merge a lone currency cell with the nearest numeric cell
        # to its right so that convert_table() receives clean data
        # (e.g. "$4,602" instead of "$" + "" + "4,602" in three
        # separate cells).
        _CURR_PLAIN = {"$", "\u20ac", "\u00a3"}  # $, €, £
        _re_btag = re.compile(r"</?b>")
        _re_numval = re.compile(r"^\(?\s*[\d,]+\.?\d*\s*\)?\s*%?$")

        for row in raw_rows:
            ci = 0
            while ci < len(row):
                plain = _re_btag.sub("", row[ci]).strip()
                if plain not in _CURR_PLAIN or not plain:
                    ci += 1
                    continue
                # Look right: skip empties, merge into first numeric
                merged = False
                for cj in range(ci + 1, len(row)):
                    tgt_plain = _re_btag.sub("", row[cj]).strip()
                    if not tgt_plain:
                        continue  # skip empty cells
                    if _re_numval.match(tgt_plain):
                        sym_bold = "<b>" in row[ci]
                        tgt_bold = "<b>" in row[cj]
                        combo = plain + tgt_plain
                        if sym_bold or tgt_bold:
                            combo = f"<b>{combo}</b>"
                        row[cj] = combo
                        row[ci] = ""
                        merged = True
                    break  # stop on first non-empty (merge or not)
                ci += 1

        # Remove columns that are entirely empty
        non_empty = [
            ci
            for ci in range(ncols)
            if any(row[ci].strip() for row in raw_rows if ci < len(row))
        ]

        parts: list[str] = ["<table>\n"]
        for row in raw_rows:
            parts.append("<tr>")
            for ci in non_empty:
                parts.append(f"<td>{row[ci]}</td>")
            parts.append("</tr>\n")
        parts.append("</table>\n")
        return "".join(parts)

    # ---- Fragment classification ----
    def _classify_fragments(
        frags: list[tuple[float, float, str, bool, float]],
    ) -> tuple[
        list[tuple[float, float, str, bool, float]],
        list[tuple[float, float, str, bool, float]],
        list[tuple[float, float, str, bool, float]],
    ]:
        """Classify free fragments as body text, chart content, or footnotes.

        Uses **per-page body-font detection** so the same logic works on
        pages where body text is set in 10 px *and* pages where it is set
        in 8 px (common in the business-segment detail pages).

        1. Detect the page's body font size — the most frequent font size
           among left-margin (left < 75 px) fragments.
        2. *Body text*: fragment whose font size is within +/-0.5 px of
           the detected body font and sits at the left margin, **or**
           within +/-0.3 px at any position (right-column text / unruled
           tables).  Large headings (font > 18 px) and bold subheadings
           at the left margin are also body text.
        3. *Footnotes*: fragments near the page bottom (top > 950 px).
        4. *Chart content*: everything else — axis ticks, legend labels,
           chart titles whose font deviates from the body font.

        Returns ``(body_frags, chart_frags, footnote_frags)``.
        """
        if not frags:
            return [], [], []

        # ---- Detect per-page body font size ----
        # Use a tight left margin (< 55 px) so chart axis labels that
        # sit at left ≈ 62–82 px don't bias the detection.
        body_margin_sizes = [
            round(fs, 1)
            for top, left, _, _, fs in frags
            if left < 55 and top < 950 and 5.0 < fs < 18.0
        ]
        body_fs = (
            Counter(body_margin_sizes).most_common(1)[0][0]
            if len(body_margin_sizes) >= 3
            else 10.0
        )

        # ---- Classify each fragment ----
        # Short numeric/currency tokens that look like chart axis ticks
        # are excluded from body text even when their font matches.
        _chart_val = re.compile(r"^-?[$]\d[\d,.]*$|^-?\d+[%]$|^\d{4}$")

        body: list[tuple[float, float, str, bool, float]] = []
        chart: list[tuple[float, float, str, bool, float]] = []
        footnotes: list[tuple[float, float, str, bool, float]] = []

        for frag in frags:
            top, left, _text, _bold, font_size = frag
            stripped = _text.strip()
            is_axis = len(stripped) < 10 and bool(_chart_val.match(stripped))

            if top > 950:
                footnotes.append(frag)
            elif font_size > 18:
                # Large section heading (e.g. "Net Income" at 22.7 px)
                body.append(frag)
            elif left < 75 and abs(font_size - body_fs) <= 0.5 and not is_axis:
                # Body-font fragment at the left margin
                body.append(frag)
            elif abs(font_size - body_fs) <= 0.3 and not is_axis:
                # Body-font fragment anywhere (right column, unruled table)
                body.append(frag)
            elif left < 75 and _bold and len(stripped) > 8:
                # Bold subheading at the left margin
                body.append(frag)
            else:
                chart.append(frag)

        return body, chart, footnotes

    # ---- Free-content (paragraph / heading) builder ----
    def _build_free_content(
        frags: list[tuple[float, float, str, bool, float]],
    ) -> str:
        """Build body text as flowing HTML with lists, headings, paragraphs.

        Handles bullet lists (●/•), section headings (detected by gap),
        first-line-indent paragraph breaks, and preserves per-fragment
        bold formatting.
        """
        if not frags:
            return ""

        frags = sorted(frags)

        # ---- Build lines: group fragments by top (± 2 px) ----
        # Each line: (top, min_left, fragments)
        lines: list[tuple[float, float, list[tuple[float, str, bool, float]]]] = []
        cur_top = frags[0][0]
        cur: list[tuple[float, str, bool, float]] = []
        for top, left, text, bold, fs in frags:
            if abs(top - cur_top) <= 2:
                cur.append((left, text, bold, fs))
            else:
                if cur:
                    cur.sort()
                    lines.append((cur_top, cur[0][0], cur))
                cur_top = top
                cur = [(left, text, bold, fs)]
        if cur:
            cur.sort()
            lines.append((cur_top, cur[0][0], cur))

        # ---- Split ALL-CAPS heading prefixes from mixed-case text ----
        # Certent CDM layouts place section headers like
        # "BUSINESS SEGMENT ANALYSIS" and subsection names like
        # "Business Focus" at the same top coordinate, forming a
        # multi-fragment line.  Split the ALL-CAPS bold prefix into
        # its own line so the single-bold H2 check can fire for each.
        _ALL_CAPS_RE = re.compile(r"^[A-Z][A-Z &,\-/\u2019\u00a0']+$")
        split_lines: list[tuple[float, float, list[tuple[float, str, bool, float]]]] = (
            []
        )
        for line_top, line_left, line_frags in lines:
            if len(line_frags) <= 1:
                split_lines.append((line_top, line_left, line_frags))
                continue

            # Find the boundary: consecutive bold ALL-CAPS fragments
            # at the start, followed by non-ALL-CAPS or non-bold text.
            caps_end = 0
            for idx, (_, ftext, fbold, _) in enumerate(line_frags):
                t = ftext.strip()
                if fbold and t and _ALL_CAPS_RE.match(t):
                    caps_end = idx + 1
                else:
                    break

            if caps_end > 0 and caps_end < len(line_frags):  # pylint: disable=R1716
                # Verify the remaining text starts mixed-case
                rest_text = " ".join(
                    t.strip() for _, t, _, _ in line_frags[caps_end:]
                ).strip()
                if rest_text and not _ALL_CAPS_RE.match(rest_text):
                    caps_frags = line_frags[:caps_end]
                    rest_frags = line_frags[caps_end:]
                    split_lines.append((line_top, caps_frags[0][0], caps_frags))
                    split_lines.append((line_top + 0.1, rest_frags[0][0], rest_frags))
                    continue

            split_lines.append((line_top, line_left, line_frags))

        lines = split_lines

        # ---- Helpers ----
        _BULLET = {"\u25cf", "\u2022"}

        def _has_bullet(
            lf: list[tuple[float, str, bool, float]],
        ) -> bool:
            return any(t.strip() in _BULLET for _, t, _, _ in lf)

        def _strip_bullet(
            lf: list[tuple[float, str, bool, float]],
        ) -> list[tuple[float, str, bool, float]]:
            return [
                (left_, t, b, f) for left_, t, b, f in lf if t.strip() not in _BULLET
            ]

        def _rich(
            lf: list[tuple[float, str, bool, float]],
        ) -> str:
            """Combine fragments preserving per-fragment bold."""
            parts: list[str] = []
            for _, text, bold, _ in lf:
                esc = _html_escape(text)
                if bold and esc.strip():
                    parts.append(f"<b>{esc}</b>")
                else:
                    parts.append(esc)
            return " ".join(parts)

        # Detect common body-left margin for indent paragraph detection
        left_vals = [lf[0][0] for _, _, lf in lines if lf]
        if left_vals:
            _left_counts: dict[int, int] = {}
            for _lv in left_vals:
                _k = round(_lv)
                _left_counts[_k] = _left_counts.get(_k, 0) + 1
            body_left = max(_left_counts, key=_left_counts.get)  # type: ignore[arg-type]
        else:
            body_left = 48

        # Regex for detecting sentence verbs — a strong signal that
        # the text is body-paragraph content, not a heading title.
        _SENTENCE_VERB_RE = re.compile(
            r"\b(?:is|are|was|were|has|have|had|"
            r"offers?|provides?|includes?|presents?|enables?|allows?"
            r"|consists?|describes?|involves?|ensures?|continues?"
            r"|represents?|reflects?|operates?|serves?|manages?"
            r"|oversees?|supports?|covers?|conform[s]?"
            r"|should|shall|will|would|could)\b",
            re.IGNORECASE,
        )

        # ---- Main loop ----
        out: list[str] = []
        in_list = False
        i = 0

        while i < len(lines):
            line_top, line_left, line_frags = lines[i]
            prev_top = lines[i - 1][0] if i > 0 else None
            gap = (line_top - prev_top) if prev_top is not None else 999

            # ---- H2: single bold fragment ----
            # In absolute-positioned SEC layouts a standalone bold
            # line is always a heading — no gap threshold needed.
            # However, bold body-text paragraphs can also appear as
            # single fragments per line; exclude those based on
            # length, casing, and verb-based sentence detection.
            if len(line_frags) == 1:
                _, text, bold, fs = line_frags[0]
                t = text.strip()
                if bold and fs >= 9.5 and len(t) > 3:
                    _is_heading = True
                    # Starts lowercase → mid-sentence fragment
                    if (
                        t[0].islower()
                        or len(t) > 120
                        and not t.isupper()
                        or len(t) > 60
                        and not t.isupper()
                        and _SENTENCE_VERB_RE.search(t)
                        or t.endswith(".")
                        and not re.search(
                            r"\b(?:INC|CORP|LTD|LLC|CO|JR|SR|DR|MR|MS"
                            + r"|U\.S)\.\s*$",
                            t,
                            re.IGNORECASE,
                        )
                    ):
                        _is_heading = False

                    if in_list:
                        out.append("</ul>\n")
                        in_list = False
                    if _is_heading:
                        out.append(f"<h2>{_html_escape(t)}</h2>\n")
                    else:
                        out.append(
                            f'<p data-body-text="1"><b>{_html_escape(t)}</b></p>\n'
                        )
                    i += 1
                    continue

            # ---- H2: very large font ----
            max_fs = max(fs for _, _, _, fs in line_frags)
            if max_fs >= 18:
                if in_list:
                    out.append("</ul>\n")
                    in_list = False
                parts = [_html_escape(t) for _, t, _, _ in line_frags]
                out.append(f"<h2>{' '.join(parts)}</h2>\n")
                i += 1
                continue

            # ---- Section heading: large gap + short + followed by bullet ----
            plain = " ".join(t for _, t, _, _ in line_frags).strip()
            next_is_bullet = i + 1 < len(lines) and _has_bullet(lines[i + 1][2])
            if (
                gap > 22
                and line_left <= 55
                and len(plain) < 50
                and not _has_bullet(line_frags)
                and next_is_bullet
            ):
                if in_list:
                    out.append("</ul>\n")
                    in_list = False
                out.append(f"<h3>{_rich(line_frags)}</h3>\n")
                i += 1
                continue

            # ---- Bullet line: absorb continuations ----
            if _has_bullet(line_frags):
                if not in_list:
                    out.append("<ul>\n")
                    in_list = True
                clean = _strip_bullet(line_frags)
                parts_list = [_rich(clean)]
                j = i + 1
                while j < len(lines):
                    ntop, _, nfrags = lines[j]
                    ngap = ntop - lines[j - 1][0]
                    if ngap <= 18 and not _has_bullet(nfrags):
                        nmax = max(fs for _, _, _, fs in nfrags)
                        if nmax >= 18:
                            break
                        if len(nfrags) == 1 and nfrags[0][2] and nfrags[0][3] >= 9.5:
                            break
                        parts_list.append(_rich(nfrags))
                        j += 1
                    else:
                        break
                out.append(f"<li>{' '.join(parts_list)}</li>\n")
                i = j
                continue

            # ---- Close list if we fell out of bullets ----
            if in_list:
                out.append("</ul>\n")
                in_list = False

            # ---- Paragraph: collect lines (gap ≤ 18 px) ----
            para = [_rich(line_frags)]
            j = i + 1
            while j < len(lines):
                ntop, _, nfrags = lines[j]
                ngap = ntop - lines[j - 1][0]
                if ngap <= 18 and not _has_bullet(nfrags):
                    nmax = max(fs for _, _, _, fs in nfrags)
                    if nmax >= 18:
                        break
                    if len(nfrags) == 1 and nfrags[0][2] and nfrags[0][3] >= 9.5:
                        break
                    # First-line indent → new paragraph
                    if nfrags[0][0] > body_left + 5:
                        break
                    para.append(_rich(nfrags))
                    j += 1
                else:
                    break

            out.append(f"<p>{' '.join(para)}</p>\n")
            i = j

        if in_list:
            out.append("</ul>\n")

        return "".join(out)

    # ---- Chart-summary builder ----
    def _build_chart_summary(
        frags: list[tuple[float, float, str, bool, float]],
    ) -> str:
        """Build a chart placeholder rendered as a <div class="chart">.

        Extracts bold titles and parenthesised descriptions.  The
        resulting ``<div>`` is preserved as raw HTML in the final
        markdown output so downstream consumers can identify and
        render chart blocks with their own styling.
        """
        if not frags:
            return ""

        titles: list[str] = []
        descs: list[str] = []
        seen_titles: set[str] = set()
        seen_descs: set[str] = set()

        for _top, _left, text, bold, fs in sorted(frags):
            t = text.strip()
            if not t:
                continue
            if bold and fs > 9 and len(t) > 3 and t not in seen_titles:
                titles.append(t)
                seen_titles.add(t)
            elif t.startswith("(") and len(t) > 10 and t not in seen_descs:
                descs.append(t)
                seen_descs.add(t)

        if not titles:
            return ""

        label = " / ".join(titles)
        # Build as a SINGLE line so post-processing cleanup steps
        # (e.g. _remove_repeated_page_elements) cannot split the div
        # into individual lines and strip them as short repeats.
        inner = f"<span>{_html_escape(label)}</span>"
        if descs:
            inner += f'<span class="chart-desc">{_html_escape("; ".join(descs))}</span>'
        return f'<div class="chart">{inner}</div>\n'

    # ---- Per-page reflow orchestrator ----
    def _reflow_page(page_num: int) -> str:
        hrules, text_frags = _parse_page(page_num)
        zones = _identify_table_zones(hrules)

        # Classify fragments into table zones vs. free
        table_frags: dict[int, list[tuple[float, float, str, bool, float]]] = {
            zi: [] for zi in range(len(zones))
        }
        free_frags: list[tuple[float, float, str, bool, float]] = []

        for frag in text_frags:
            top = frag[0]
            placed = False
            for zi, (zt, zb) in enumerate(zones):
                if zt - 5 <= top <= zb + 15:
                    table_frags[zi].append(frag)
                    placed = True
                    break
            if not placed:
                free_frags.append(frag)

        # Classify free fragments into body text, chart, and footnotes
        body_frags, chart_frags, footnote_frags = _classify_fragments(free_frags)

        # Collect page segments in vertical order
        segments: list[tuple[float, str]] = []

        for zi, (zt, zb) in enumerate(zones):
            if table_frags[zi]:
                rules_in = [r for r in hrules if zt - 1 <= r <= zb + 1]
                t_html = _build_table_from_zone(table_frags[zi], rules_in)
                if t_html:
                    # Split composite tables (TABLE 5 + 6 + 7 in one
                    # zone) into independent <table> elements so each
                    # gets converted separately by convert_table().
                    _t_soup = BeautifulSoup(t_html, "html.parser")
                    _t_tag = _t_soup.find("table")
                    if _t_tag:
                        _parts = _split_composite_table(_t_tag)
                        if len(_parts) > 1:
                            _offset = 0.0
                            for _p in _parts:
                                if isinstance(_p, str):
                                    segments.append((zt + _offset, f"<p>{_p}</p>"))
                                else:
                                    segments.append((zt + _offset, str(_p)))
                                _offset += 0.01
                        else:
                            segments.append((zt, t_html))
                    else:
                        segments.append((zt, t_html))

        # Body text → paragraphs / headings
        if body_frags:
            body_frags.sort()
            groups: list[list[tuple[float, float, str, bool, float]]] = []
            cur_group = [body_frags[0]]
            for i in range(1, len(body_frags)):
                gap = body_frags[i][0] - body_frags[i - 1][0]
                crosses_zone = any(
                    body_frags[i - 1][0] < zt and body_frags[i][0] > zb
                    for zt, zb in zones
                )
                if crosses_zone or gap > 40:
                    groups.append(cur_group)
                    cur_group = [body_frags[i]]
                else:
                    cur_group.append(body_frags[i])
            groups.append(cur_group)

            for g in groups:
                content = _build_free_content(g)
                if content.strip():
                    segments.append((g[0][0], content))

        # Chart content → compact annotation
        if chart_frags:
            chart_html = _build_chart_summary(chart_frags)
            if chart_html.strip():
                avg_top = sum(f[0] for f in chart_frags) / len(chart_frags)
                segments.append((avg_top, chart_html))

        # Footnotes → rendered as body paragraphs at page bottom
        if footnote_frags:
            fn_html = _build_free_content(footnote_frags)
            if fn_html.strip():
                segments.append((footnote_frags[0][0], fn_html))

        segments.sort(key=lambda s: s[0])
        return "".join(s[1] for s in segments)

    # ---- Main loop: process every page ----
    out_parts: list[str] = ["<html><body>\n"]

    for pg in range(1, total_pages + 1):
        page_html = _reflow_page(pg)
        if page_html:
            out_parts.append(page_html)

    out_parts.append("</body></html>")
    return "".join(out_parts)


def _html_escape(text: str) -> str:
    """Minimal HTML escaping for reflowed text."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def html_to_markdown(
    html_content: str,
    base_url: str = "",
    keep_tables: bool | None = True,
) -> str:
    """Convert SEC HTML content to Markdown format.

    Parameters
    ----------
    html_content : str or bytes
        HTML content to convert
    base_url : str
        Base URL for resolving relative links and images
    keep_tables : bool
        If True, convert tables to markdown tables. If False, skip tables entirely.

    Returns
    -------
    str
        Markdown-formatted text
    """
    # Handle legacy parameter
    if not keep_tables:
        keep_tables = False

    if not html_content:
        return ""

    if isinstance(html_content, bytes):
        html_content = html_content.decode("utf-8", errors="ignore")

    # Remove XML declaration
    html_content = re.sub(r"<\?xml.*?\?>", "", html_content, flags=re.IGNORECASE)

    for entity, char in WIN1252_MAP.items():
        html_content = html_content.replace(entity, char)

    # Detect and rewrite absolute-positioned layouts (e.g. TD 40-F
    # exhibits generated by PDF-to-HTML converters) into flowing HTML
    # before the main converter processes them.
    _reflowed = _reflow_absolute_layout(html_content)
    if _reflowed is not None:
        html_content = _reflowed

    soup = BeautifulSoup(html_content, "lxml")

    # Remove hidden XBRL elements and junk
    for tag in soup.find_all(["ix:header", "ix:hidden", "script", "style", "noscript"]):
        tag.decompose()

    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    for tag in soup.find_all(True):
        if tag.attrs and "style" in tag.attrs:
            style = str(tag.get("style", "")).lower().replace(" ", "")
            if "display:none" in style or "visibility:hidden" in style:
                # Do NOT decompose table cells (td/th) — their colspan
                # is structural even when hidden.  Removing them breaks
                # the column grid and causes data columns to disappear.
                # Instead, clear their content so they remain as empty
                # placeholders in the grid.
                if tag.name in ("td", "th"):
                    tag.string = ""
                else:
                    tag.decompose()

    _merge_continuation_tables(soup)

    # Presentation slide decks (e.g. Spotify 6-K EX-99):
    # Each slide is a <div class="slide"> containing an <img> (the
    # actual slide) and a <div class="slideText"> with invisible
    # (1pt / white) accessibility text.  The text is an unstructured
    # dump that doesn't convert to readable markdown.  Convert the
    # slideText content into HTML comments so it is preserved for
    # search / AI consumption but not rendered visually.
    _slide_divs = soup.find_all("div", class_="slide")
    if len(_slide_divs) >= 3:  # at least 3 slides → slide deck
        for _sd in _slide_divs:
            for _st in _sd.find_all("div", class_="slideText"):
                _txt = _st.get_text(separator=" ", strip=True)
                _txt = re.sub(r"\s+", " ", _txt).strip()
                if _txt:
                    _comment = Comment(f" {_txt} ")
                    _st.replace_with(_comment)
                else:
                    _st.decompose()
        # Also remove the spacer divs between slides.
        for _sp in soup.find_all("div", class_="spaceAfterSlideText"):
            _sp.decompose()

    # General invisible accessibility text (e.g. LOW 8-K infographics):
    # Some filings embed tiny white text (<font style="font-size:1pt;
    # color:white">) as accessibility descriptions for images.  This
    # text dumps as an unformatted wall of text in markdown.  Convert
    # it to HTML comments so it's preserved for search / AI but not
    # rendered visually.  This handles patterns not covered by the
    # slide-deck detection above.
    _invisible_re = re.compile(r"font-size\s*:\s*1(?:pt|px)", re.IGNORECASE)
    _white_re = re.compile(r"color\s*:\s*white", re.IGNORECASE)
    for _inv_tag in soup.find_all(["font", "span", "div", "p"]):
        _style = _inv_tag.get("style", "")
        if not _style:
            continue
        if _invisible_re.search(_style) and _white_re.search(_style):
            _txt = _inv_tag.get_text(separator=" ", strip=True)
            _txt = re.sub(r"\s+", " ", _txt).strip()
            if _txt and len(_txt) > 20:
                _comment = Comment(f" {_txt} ")
                _inv_tag.replace_with(_comment)
            elif not _txt:
                _inv_tag.decompose()
            # Short text (<= 20 chars) is left alone — unlikely to be
            # meaningful accessibility description.

    # Track whether we have already emitted a TOC / page-navigation table.
    # Older SEC exhibits (e.g. IBM 2008 Annual Report) embed the same sidebar
    # navigation table on every page — dozens of copies.  We keep only the
    # first one and suppress the rest.
    _seen_toc_table = [False]  # mutable so inner function can write

    def process_element(element, depth=0) -> str:
        """Recursively process element to markdown."""
        if isinstance(element, NavigableString):
            # Preserve Comment nodes as HTML comments in markdown output.
            if isinstance(element, Comment):
                return f"<!--{element}-->\n\n"
            text = str(element)
            # Normalize whitespace: convert tabs/newlines to spaces, collapse multiple spaces
            text = text.replace("\xa0", " ")  # Non-breaking space
            text = re.sub(r"[\t\n\r]+", " ", text)
            text = re.sub(r" +", " ", text)  # Collapse multiple spaces
            return text

        if element.name is None:
            return ""

        if element.name in ["script", "style", "noscript"]:
            return ""

        # Skip "Table of Contents" page-header elements.
        # SEC filings repeat these at every page break.  Two patterns:
        #   1) A simple div/p whose *only* text is the TOC link.
        #   2) A container div (often with min-height style) that holds
        #      a TOC link *plus* a running section name (e.g.
        #      "Notes to Consolidated Financial Statements — (continued)").
        # Both are navigation artefacts, not document content.
        if element.name in ["div", "p"]:
            toc_link = element.find(
                "a",
                href=True,
                string=re.compile(r"^\s*Table of Contents\s*$", re.I),
            )
            if toc_link:
                full_text = element.get_text(separator=" ", strip=True)
                if len(full_text) < 200:
                    return ""  # Skip this navigation / page-header element

        # Also skip h1-h6 navigation headings whose sole text is "Table of Contents".
        # Some SEC filings embed these as page-break separators (e.g. <h5>Table of Contents</h5>).
        if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            _h_text = element.get_text(separator=" ", strip=True)
            if re.match(r"^\s*Table of Contents\s*$", _h_text, re.I):
                return ""

        # This handles modern HTML where anchors use id= on div/p/td/etc
        element_id = element.get("id")
        anchor_prefix = ""

        if element_id and element.name != "a":  # Don't double-process <a> tags
            anchor_prefix = f'<a id="{element_id}"></a>'

        # Handle XBRL inline elements (ix:continuation, ix:nonNumeric, etc.)
        # These are containers that should preserve the structure of their children
        if element.name.startswith("ix:"):
            parts = []

            for child in element.children:
                if isinstance(child, NavigableString):
                    text = str(child).strip()
                    if text:
                        parts.append(text)
                else:
                    parts.append(process_element(child, depth + 1))
            # Join with empty string to preserve paragraph breaks (\n\n) from children
            return "".join(parts)

        # Images - use helper to preserve sizes
        if element.name == "img":
            img_md = _convert_image_to_html(element, base_url)

            if img_md:
                return f"\n\n{img_md}\n\n"

            return ""

        # Tables
        if element.name == "table":
            if keep_tables:
                # Detect TOC / page-navigation tables and suppress duplicates.
                # Older SEC exhibits (e.g. IBM 2008 Annual Report) embed a
                # sidebar navigation table on every page.  These tables have
                # section names with page numbers — NOT financial data.
                # Key signal: a row whose first cell says "Management
                # Discussion" (or similar TOC heading) combined with most
                # rows ending in a bare page-number integer.
                tbl_rows = element.find_all("tr")
                if len(tbl_rows) >= 5:
                    _has_toc_heading = False
                    _page_num_rows = 0
                    for _tr in tbl_rows:
                        _cells = _tr.find_all(["td", "th"])
                        if not _cells:
                            continue
                        _first = _cells[0].get_text(strip=True).lower()
                        if _first in (
                            "management discussion",
                            "table of contents",
                        ) or _first.startswith("management\n"):
                            _has_toc_heading = True
                        _last = _cells[-1].get_text(strip=True)
                        if _last.isdigit() and 0 < int(_last) < 300:
                            _page_num_rows += 1
                    if _has_toc_heading and _page_num_rows >= len(tbl_rows) * 0.5:
                        if _seen_toc_table[0]:
                            return ""  # Already emitted one — skip
                        _seen_toc_table[0] = True
                return "\n\n" + convert_table(element, base_url) + "\n\n"
            return ""

        # Headers
        if is_header_element(element):
            anchor_tag = element.find("a", attrs={"name": True})
            anchor_html = anchor_prefix  # Use element's id if present

            if anchor_tag:
                anchor_name = anchor_tag.get("name")
                if anchor_name:
                    anchor_html = f'<a id="{anchor_name}"></a>\n\n'
            elif anchor_prefix:
                anchor_html = anchor_prefix + "\n\n"

            text = get_text_content(element).strip()
            text = re.sub(r"\s+", " ", text)

            if text:
                level = get_header_level(element)
                return f"\n\n{anchor_html}{'#' * level} {text}\n\n"

            return anchor_html if anchor_html else ""

        # Lists
        if element.name == "ul":
            items = []

            for li in element.find_all("li", recursive=False):
                # Check for id on li element
                li_id = li.get("id")
                li_anchor = f'<a id="{li_id}"></a>' if li_id else ""
                item_text = process_element(li, depth + 1).strip()

                if item_text:
                    items.append(f"- {li_anchor}{item_text}")

            result = "\n" + "\n".join(items) + "\n" if items else ""

            return f"{anchor_prefix}{result}" if anchor_prefix else result

        if element.name == "ol":
            items = []

            for i, li in enumerate(element.find_all("li", recursive=False), 1):
                # Check for id on li element
                li_id = li.get("id")
                li_anchor = f'<a id="{li_id}"></a>' if li_id else ""
                item_text = process_element(li, depth + 1).strip()

                if item_text:
                    items.append(f"{i}. {li_anchor}{item_text}")

            result = "\n" + "\n".join(items) + "\n" if items else ""

            return f"{anchor_prefix}{result}" if anchor_prefix else result

        # Paragraphs and divs
        if element.name in ["p", "div"]:
            # Chart divs produced by _build_chart_summary() should be
            # preserved as raw HTML blocks in the markdown output.
            if element.get("class") and "chart" in element.get("class", []):
                return f"\n\n{str(element)}\n\n"

            # Check if this is an inline element (display:inline in style)
            # Be careful not to match "display:inline-block" which is block-level
            style = element.get("style", "")
            is_inline = bool(
                re.search(
                    r"display:\s*inline(?:\s*;|\s*$|(?![a-z-]))", style, re.IGNORECASE
                )
            )
            has_bold = re.search(
                r"font-weight:\s*(bold|bolder|[6-9]00)", style, re.IGNORECASE
            )
            has_italic = re.search(r"font-style:\s*italic", style, re.IGNORECASE)

            # Check if this is a CSS table-row with bullet (display: table-row)
            # These are used as pseudo-lists in SEC filings
            is_table_row = "display: table-row" in style or "display:table-row" in style

            if is_table_row:
                # Look for bullet in first table-cell, text in second
                cells = element.find_all(
                    "div", style=re.compile(r"display:\s*table-cell", re.IGNORECASE)
                )
                if len(cells) >= 2:
                    first_cell_text = cells[0].get_text(strip=True)

                    if first_cell_text in BULLET_CHARS:
                        # This is a bullet item - extract text from remaining cells
                        text = " ".join(
                            c.get_text(separator=" ", strip=True) for c in cells[1:]
                        )
                        text = re.sub(r"\s+", " ", text).strip()
                        if text:
                            return f"\n- {text}"

            # These are section headers where an anchor tag splits bold text
            children_list = list(element.children)
            children_text = []
            skip_until = -1

            for ci, child in enumerate(children_list):
                if ci <= skip_until:
                    continue
                # Check for anchor with bold content followed by sibling bold
                if (
                    isinstance(child, Tag)
                    and child.name == "a"
                    and (child.get("name") or child.get("id"))
                ):
                    inner_b = child.find(["b", "strong"])

                    if inner_b:
                        anchor_text = child.get_text()

                        if anchor_text.strip():
                            # Look for following <b>/<strong> siblings
                            combined = anchor_text
                            last_consumed = ci
                            found_bold_sib = False

                            for j in range(ci + 1, len(children_list)):
                                sib = children_list[j]

                                if (
                                    isinstance(sib, NavigableString)
                                    and sib.strip() == ""
                                ):
                                    last_consumed = j
                                    continue

                                if isinstance(sib, Tag) and sib.name in [
                                    "b",
                                    "strong",
                                ]:
                                    combined += sib.get_text()
                                    last_consumed = j
                                    found_bold_sib = True
                                else:
                                    break

                            if found_bold_sib:
                                anchor_id = child.get("name") or child.get("id")
                                anchor_html = f'<a id="{anchor_id}"></a>\n\n'
                                combined = re.sub(r"\s+", " ", combined).strip()
                                children_text.append(
                                    f"\n\n{anchor_html}### {combined}\n\n"
                                )
                                skip_until = last_consumed
                                continue

                children_text.append(process_element(child, depth + 1))

            text = "".join(children_text).strip()

            if text:
                if is_inline:
                    # Apply bold/italic formatting for CSS-styled inline elements
                    if has_bold and has_italic:
                        text = f"***{text}***"
                    elif has_bold:
                        text = f"**{text}**"
                    elif has_italic:
                        text = f"*{text}*"
                    return f"{anchor_prefix}{text}" if anchor_prefix else text

                # Convert to proper heading + paragraph
                subheading_match = re.match(
                    r"^(\*{2,3})([^*]+)\1\s*\.\s*(.+)$", text, re.DOTALL
                )

                if subheading_match:
                    title = subheading_match.group(2).strip()
                    body = subheading_match.group(3).strip()

                    return f"\n\n{anchor_prefix}#### {title}\n\n{body}\n\n"

                return f"\n\n{anchor_prefix}{text}\n\n"

            return anchor_prefix if anchor_prefix else ""

        # Line breaks
        if element.name == "br":
            return "\n"

        # Horizontal rules
        if element.name == "hr":
            return "\n\n---\n\n"

        # Anchor tags - handle both links and anchor targets
        if element.name == "a":
            name = element.get("name")
            elem_id = element.get("id")  # Modern HTML uses id instead of name
            href = element.get("href")
            text = get_text_content(element).strip()

            # Anchor target (for TOC links to jump to) - support both name and id
            if name or elem_id:
                anchor_id = name or elem_id  # Prefer name, fall back to id
                anchor = f'<a id="{anchor_id}"></a>'

                if text:
                    return f"{anchor}\n{text}"

                return anchor

            # Regular link
            if href and text:
                if (
                    not href.startswith("#")
                    and base_url
                    and not href.startswith(("http://", "https://"))
                ):
                    href = urljoin(base_url, href)

                return f"[{text}]({href})"

            return text or ""

        # Bold - process children to preserve anchors inside
        if element.name in ["b", "strong"]:
            if element.find("img") and not element.get_text(strip=True):
                parts = []

                for child in element.children:
                    parts.append(process_element(child, depth + 1))

                return "".join(parts)

            parts = []

            for child in element.children:
                parts.append(process_element(child, depth + 1))

            inner = "".join(parts).strip()
            inner = re.sub(r"\s+", " ", inner)

            if inner:
                if '<a id="' in inner:
                    match = re.search(r'(<a id="[^"]+"></a>)(.*)', inner)
                    if match:
                        anchor = match.group(1)
                        text = match.group(2).strip()
                        if text:
                            return f"{anchor}**{text}** "

                        return anchor
                # If inner is only asterisks (footnote markers like *, **),
                # escape them to prevent collision with Markdown formatting
                if re.match(r"^\*+$", inner):
                    return inner.replace("*", "\\*")

                return f"**{inner}** "

            return ""

        # Italic - process children to preserve anchors
        if element.name in ["i", "em"]:
            parts = []

            for child in element.children:
                parts.append(process_element(child, depth + 1))

            inner = "".join(parts).strip()

            if inner:
                if '<a id="' in inner:
                    match = re.search(r'(<a id="[^"]+"></a>)(.*)', inner)
                    if match:
                        anchor = match.group(1)
                        text = match.group(2).strip()

                        if text:
                            return f"{anchor}*{text}*"

                        return anchor
                # If inner is only asterisks (footnote markers like *, **),
                # escape them to prevent collision with Markdown formatting
                if re.match(r"^\*+$", inner):
                    return inner.replace("*", "\\*")

                return f"*{inner}*"

            return ""

        # Underline - just process children
        if element.name == "u":
            parts = []

            for child in element.children:
                parts.append(process_element(child, depth + 1))

            return "".join(parts).strip()

        # Superscript - ensure space separation from adjacent text
        # SEC footnotes use <sup>1</sup>Text which concatenates as "1Text" without this
        if element.name == "sup":
            text = element.get_text().strip()
            if text:
                return f"{text} "
            return ""

        # Blockquote
        if element.name == "blockquote":
            parts = []

            for child in element.children:
                parts.append(process_element(child, depth + 1))

            text = "".join(parts).strip()

            if text:
                lines = text.split("\n")
                quoted = "\n".join(f"> {line}" for line in lines)

                return f"\n\n{quoted}\n\n"

            return ""

        # Pre/code
        if element.name == "pre":
            text = element.get_text()

            return f"\n\n```\n{text}\n```\n\n"

        if element.name == "code":
            text = element.get_text()

            if "\n" not in text:
                return f"`{text}`"

            return f"\n```\n{text}\n```\n"

        # Default: process children (including spans, sections, etc.)
        result_list: list = []

        for child in element.children:
            result_list.append(process_element(child, depth + 1))

        inner = "".join(result_list)
        # Prepend anchor if element had an id attribute
        if anchor_prefix and inner.strip():
            return f"{anchor_prefix}{inner}"

        return inner

    # Process the body or root
    body = soup.body or soup
    markdown = process_element(body)

    # Clean up
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    markdown = re.sub(r" {2,}", " ", markdown)

    # Fix orphaned bullet characters
    markdown = re.sub(
        r"^([•●◦○▪■\-\*])\s*\n+([A-Z])", r"• \2", markdown, flags=re.MULTILINE
    )

    # Convert inline bullet characters to markdown bullets
    markdown = re.sub(
        r"(?:^|\n\n)([•●◦○▪■])([A-Z])",
        r"\n\n- \2",
        markdown,
    )

    # Detect section headers from standalone short lines
    header_patterns = [
        r"^(Introduction)$",
        r"^(Executive Overview)$",
        r"^(Financial Overview)$",
        r"^(Business Environment)$",
        r"^(Critical Accounting Policies)$",
        r"^(Results of Operations)$",
        r"^(Liquidity and Capital Resources)$",
        r"^(Risk Management)$",
        r"^(Balance Sheet Analysis)$",
        r"^(Segment Results)$",
        r"^(Recent Developments)$",
        r"^(Forward[-\s]Looking Statements?)$",
        r"^(Market Risk)$",
        r"^(Credit Risk)$",
        r"^(Operational Risk)$",
        r"^(Legal Proceedings?)$",
        r"^(Controls and Procedures)$",
        r"^(Fair Value)$",
        r"^(Allowance for Credit Losses)$",
        r"^(Capital)$",
        r"^(Funding)$",
    ]
    for pattern in header_patterns:
        markdown = re.sub(
            pattern,
            r"## \1",
            markdown,
            flags=re.MULTILINE | re.IGNORECASE,
        )

    # Strip anchor tags that are not referenced by any in-document link.
    # XBRL cell IDs (Tc_*), GUID-like IDs, and other noise anchors clutter
    # the output and break section header formatting.
    _referenced_ids = set(re.findall(r"\(#([^)]+)\)", markdown))

    def _filter_anchor(m):
        anchor_id = m.group(1)
        if anchor_id in _referenced_ids:
            return m.group(0)
        return ""

    markdown = re.sub(r'<a id="([^"]+)"></a>', _filter_anchor, markdown)
    # Clean up lines that are now empty after anchor removal
    markdown = re.sub(r"\n[ \t]*\n", "\n\n", markdown)

    # Merge consecutive bold sections on the same line.
    # Use [ ]+ (not \s*) to avoid merging across paragraph boundaries,
    # and skip merges when either side contains an image tag.
    def _merge_bold(m):
        a, b = m.group(1), m.group(2)
        if "<img " in a or "<img " in b:
            return m.group(0)  # Don't merge bold across images
        return f"**{a} {b}**"

    markdown = re.sub(r"\*\*([^*]+)\*\*[ ]+\*\*([^*]+)\*\*", _merge_bold, markdown)
    for _ in range(5):
        new_md = re.sub(r"\*\*([^*]+)\*\*[ ]+\*\*([^*]+)\*\*", _merge_bold, markdown)
        if new_md == markdown:
            break
        markdown = new_md

    # Remove repeated "Table of Contents" headers.
    # Some filings (e.g. IBM) produce lines like:
    #   ### Table of Contents Management Discussion – (continued)
    # so match any heading that *starts with* the TOC prefix.
    _toc_re = re.compile(r"^#{1,6}\s+Table of Contents", re.IGNORECASE)
    lines = markdown.split("\n")
    first_toc_kept = False
    filtered_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if _toc_re.match(line.strip()):
            # Keep the very first occurrence when it is followed by an
            # actual TOC table (pipe-delimited rows).
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if (
                j < len(lines)
                and lines[j].strip().startswith("|")
                and not first_toc_kept
            ):
                filtered_lines.append(line)
                first_toc_kept = True
                i += 1
                continue
            i += 1
            continue
        filtered_lines.append(line)
        i += 1
    markdown = "\n".join(filtered_lines)

    # Remove repeated [Table of Contents](#...) links (page header navigation)
    # Anchor target varies by filing: #toc, GUIDs, etc.
    markdown = re.sub(
        r"\n+\[Table of Contents\]\(#[^)]+\)\n+", "\n\n", markdown, flags=re.IGNORECASE
    )

    # Remove page break horizontal rules (often followed/preceded by excessive whitespace)
    # These are artifacts from page-break-before:always in the HTML
    markdown = re.sub(r"\n{2,}---\n{2,}", "\n\n", markdown)

    # Remove standalone page numbers
    markdown = re.sub(
        r"\n\n(?:S-)?(?:[ivxlcdm]+|[IVX]+|\d{1,3}|F-\d{1,2})\n\n",
        "\n\n",
        markdown,
        flags=re.IGNORECASE,
    )

    # Clean up double bullet/dash patterns (e.g., "- •" or "- –")
    # These occur when the converter adds a markdown bullet and the source also had a Unicode bullet
    markdown = re.sub(r"^- •\s*", "- ", markdown, flags=re.MULTILINE)
    markdown = re.sub(r"^- ●\s*", "- ", markdown, flags=re.MULTILINE)
    markdown = re.sub(r"^- –\s*", "- ", markdown, flags=re.MULTILINE)
    markdown = re.sub(r"^- —\s*", "- ", markdown, flags=re.MULTILINE)
    markdown = re.sub(r"^• •\s*", "- ", markdown, flags=re.MULTILINE)
    markdown = re.sub(r"^● ●\s*", "- ", markdown, flags=re.MULTILINE)
    markdown = re.sub(
        r"^•\s+", "- ", markdown, flags=re.MULTILINE
    )  # Convert standalone • to -
    markdown = re.sub(
        r"^●\s+", "- ", markdown, flags=re.MULTILINE
    )  # Convert standalone ● to -

    # Remove specific page header/footer patterns with images (e.g., DEF14A proxy statements)
    markdown = re.sub(
        r"\n(?:\d{1,3}\s+)?<img[^>]+>\s*\d{4}\s+Annual Meeting of Stockholders\s*\n",
        "\n",
        markdown,
    )
    markdown = re.sub(
        r"\n\d{4}\s+Annual Meeting of Stockholders\s*<img[^>]+>(?:\s*\d{1,3})?\s*\n",
        "\n",
        markdown,
    )

    # Remove repeated page footer/header patterns
    # Find short lines that repeat many times (likely page footers/headers)
    markdown = _remove_repeated_page_elements(markdown)

    # Normalize bullet characters (•) into proper markdown bullet lines
    markdown = _normalize_bullet_chars(markdown)

    # Join paragraphs that were split by page breaks
    markdown = _join_split_paragraphs(markdown)

    # Convert inline subheadings to proper markdown headers
    # Pattern: "Title . Body text" where Title starts the line and is followed by period-space
    # These are common in SEC filings for subsection titles
    markdown = _convert_inline_subheadings(markdown)

    # Merge consecutive headers at the same level
    # SEC filings often have split headers like:
    #   ### CONDENSED CONSOLIDATED STATEMENTS OF CHANGES IN
    #   ### STOCKHOLDERS EQUITY AND PARTNERS CAPITAL
    # These should be merged into a single header
    markdown = _merge_consecutive_headers(markdown)

    # Separate footnote markers from text.
    # SEC filings often have footnotes like "1Refer to Note 11..." or
    # "2We calculated..." where the footnote number (from a <font> or
    # <span> tag with small font-size, NOT a <sup> tag) is directly
    # concatenated with the following text.  Insert a space so it
    # renders as "1 Refer to Note 11..." instead of "1Refer...".
    # Only match 1-2 digit markers immediately followed by an uppercase
    # letter at the start of a line (or after a double-newline paragraph
    # break) to avoid splitting things like "3M" or "401k".
    markdown = re.sub(
        r"^(\d{1,2})([A-Z][a-z])",
        r"\1 \2",
        markdown,
        flags=re.MULTILINE,
    )

    # Final whitespace cleanup - convert any remaining Windows-1252 characters
    for win_char, unicode_char in WIN1252_MAP.items():
        markdown = markdown.replace(win_char, unicode_char)

    # Replace non-breaking spaces with regular spaces
    markdown = markdown.replace("\xa0", " ")
    # Collapse multiple consecutive spaces to single space
    markdown = re.sub(r" {2,}", " ", markdown)
    # Clean up trailing whitespace on lines
    markdown = re.sub(r" +$", "", markdown, flags=re.MULTILINE)
    # Clean up leading whitespace on lines (except for code blocks/lists)
    # Only strip leading spaces that aren't part of markdown formatting
    markdown = re.sub(r"^[ \t]+(?=[^\-\*\d\|#])", "", markdown, flags=re.MULTILINE)
    # Collapse excessive blank lines (more than 2 newlines -> 2 newlines)
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    # Also collapse lines that are just whitespace
    markdown = re.sub(r"\n[ \t]+\n", "\n\n", markdown)
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    markdown = markdown.strip()

    return markdown


def _merge_consecutive_headers(markdown: str) -> str:
    """
    Merge consecutive headers at the same level into a single header.

    SEC filings often have titles split across multiple lines/elements:
        ### CONDENSED CONSOLIDATED STATEMENTS OF CHANGES IN
        ### STOCKHOLDERS EQUITY AND PARTNERS CAPITAL
        **(UNAUDITED)**

    This merges them into:
        ### CONDENSED CONSOLIDATED STATEMENTS OF CHANGES IN STOCKHOLDERS EQUITY AND PARTNERS CAPITAL
        **(UNAUDITED)**

    Only merges when the first header looks *incomplete* — i.e. its last
    word is a preposition, conjunction, article, or determiner.  Two
    genuinely separate headers (e.g. a section title followed by a
    subsection title) are left alone.
    """
    # Words that signal the heading phrase is incomplete.
    _CONTINUATION_ENDINGS = {
        "in",
        "of",
        "and",
        "the",
        "for",
        "to",
        "with",
        "on",
        "a",
        "an",
        "by",
        "at",
        "as",
        "or",
        "nor",
        "but",
        "from",
        "into",
        "onto",
        "upon",
        "per",
        "its",
        "their",
        "our",
        "your",
        "this",
        "that",
        "these",
        "those",
        "which",
        "who",
        "whom",
        "whose",
    }

    def _looks_incomplete(text: str) -> bool:
        """Return True if *text* appears to be an incomplete title phrase."""
        t = text.rstrip()
        if not t:
            return False
        # Ends with a continuation punctuation mark (comma, dash, colon)
        if t[-1] in (",", "\u2013", "\u2014", "-"):
            return True
        last_word = t.split()[-1].lower().rstrip(".,;:")
        return last_word in _CONTINUATION_ENDINGS

    lines = markdown.split("\n")
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Check if this is a header line
        header_match = re.match(r"^(#{1,6})\s+(.+)$", stripped)

        if header_match:
            level = header_match.group(1)  # e.g., "###"
            header_text = header_match.group(2)

            # Look ahead for consecutive headers at the same level
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()

                # Skip empty lines between consecutive headers
                if not next_line:
                    j += 1
                    continue

                # Check if next non-empty line is same-level header
                next_match = re.match(r"^(#{1,6})\s+(.+)$", next_line)
                if (
                    next_match
                    and next_match.group(1) == level
                    and _looks_incomplete(header_text)
                ):
                    # Merge this header text — first header is an
                    # incomplete phrase that continues on the next line.
                    header_text = header_text.rstrip() + " " + next_match.group(2)
                    j += 1
                elif (
                    next_match
                    and next_match.group(1) != level
                    and _looks_incomplete(header_text)
                ):
                    # Different-level header but first header is clearly
                    # incomplete — merge at the current (higher) level.
                    header_text = header_text.rstrip() + " " + next_match.group(2)
                    j += 1
                else:
                    # Not a continuation — stop merging
                    break

            # Output the merged header
            result.append(f"{level} {header_text}")
            i = j
        else:
            result.append(line)
            i += 1

    return "\n".join(result)


def _convert_inline_subheadings(markdown: str) -> str:
    """
    Convert inline subheadings to proper markdown headers.

    SEC filings often have subsection titles formatted as:
    "Subsection Title . Body text continues here..."

    This converts them to:
    "#### Subsection Title

    Body text continues here..."
    """
    # Pattern matches: Start of line, capitalized title (2-8 words), period, space, body text
    # Title must start with capital letter and contain 2-8 words
    # Must have period followed by space and then more text (body)
    pattern = (
        r"^([A-Z][A-Za-z]+(?:\s+(?:and|of|on|the|for|in|to|a|an|with|as|or|by|at|from|"
        r"under|into|through|after|before|between|during|without|within|about|against|"
        r"among|around|behind|below|beyond|except|inside|outside|over|since|toward|until|"
        r"upon|versus|via|[A-Z][A-Za-z\']+)){1,7})\s+\.\s+([A-Z].+)$"
    )

    def replace_subheading(match):
        title = match.group(1).strip()
        body = match.group(2).strip()
        return f"#### {title}\n\n{body}"

    # Process line by line since we need to match at start of line
    lines = markdown.split("\n")
    result = []
    for line in lines:
        # Only process non-table, non-header lines
        stripped = line.strip()
        if stripped and not stripped.startswith("|") and not stripped.startswith("#"):
            new_line = re.sub(pattern, replace_subheading, line)
            result.append(new_line)
        else:
            result.append(line)

    return "\n".join(result)


# ============================================================================
# PAGE ELEMENT CLEANUP FUNCTIONS
# ============================================================================


def _normalize_bullet_chars(markdown: str) -> str:
    """Normalize Unicode bullet characters (•) into proper markdown bullet lines.

    Position-based HTML layouts (Workiva) often produce lines like:
        •item one; •item two; and •item three.
    This splits them into separate markdown bullet lines:
        - item one;
        - item two; and
        - item three.

    Also handles lines that start with a single •.
    """
    lines = markdown.split("\n")
    result = []
    for line in lines:
        stripped = line.strip()
        # Skip lines without bullet chars
        if "\u2022" not in stripped:
            result.append(line)
            continue

        # Skip if inside a markdown table row
        if stripped.startswith("|"):
            result.append(line)
            continue

        # Split on • to get individual bullet items
        # Handle leading text before first •
        parts = re.split(r"\u2022", stripped)

        # parts[0] is text before the first •  (may be empty)
        prefix_text = parts[0].strip()
        if prefix_text:
            result.append(prefix_text)

        # Each subsequent part is a bullet item
        for part in parts[1:]:
            item_text = part.strip()
            if item_text:
                result.append(f"- {item_text}")

    return "\n".join(result)


def _join_split_paragraphs(markdown: str) -> str:
    """
    Join paragraphs that were split by page breaks in SEC filings.

    Handles two patterns:
    1. Hyphenated words split across pages: "pre-" ... "tax" → "pre-tax"
    2. Sentences split at connecting words: "and" ... "acquisitions" → "and acquisitions"

    Also removes page headers that interrupt paragraphs (e.g., company name, section titles).
    """
    # First, remove common SEC filing page headers that interrupt text
    # These are bold lines that repeat throughout the document
    page_header_patterns = [
        # Company name + section continuation markers
        r"\*\*[A-Z][A-Z\s,\.&]+(?:INC\.|CORP\.|LLC|LP|L\.P\.)?\s+(?:and\s+)?(?:SUBSIDIARIES?)?\s*(?:NOTES?\s+TO\s+)?(?:CONDENSED\s+)?(?:CONSOLIDATED\s+)?(?:FINANCIAL\s+STATEMENTS?)?\s*(?:—|–|-)\s*\(Continued\)\s*(?:\(UNAUDITED\))?\*\*",
        # Just "(UNAUDITED)" on its own line
        r"^\*\*\(UNAUDITED\)\*\*$",
    ]

    for pattern in page_header_patterns:
        markdown = re.sub(pattern, "", markdown, flags=re.MULTILINE | re.IGNORECASE)

    # Clean up any resulting excessive blank lines
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)

    lines = markdown.split("\n")
    result = []
    i = 0

    # Patterns for structural lines that should never be joined
    # Note: \d{1,2}\.\s matches numbered lists (1-99) but NOT years like "2024."
    _STRUCTURAL_RE = re.compile(r"^(?:#|\||- |\* |\d{1,2}\.\s|<img|<a\s|\[)")
    # Connecting words that always indicate mid-sentence when at line end
    _CONNECTING_RE = re.compile(
        r"\b(and|or|the|a|an|of|to|in|for|with|by|from|at|on|as|that|which|but|"
        r"is|are|was|were|be|been|being|have|has|had|not|its|their|our|this|"
        r"these|those|into|upon|about|through|under|between|during|after|"
        r"before|including|such)\s*$",
        re.IGNORECASE,
    )

    def _is_joinable_line(s: str) -> bool:
        """Return True if stripped line *s* is eligible for joining."""
        return (
            bool(s)
            and not _STRUCTURAL_RE.match(s)
            and not _INLINE_HTML_RE.search(s)
            and not _PAGE_HEADER_LINK_RE.match(s)
        )

    def _next_nonblank(start: int):
        """Return (index, stripped_text) of next non-blank line, or (start, None)."""
        j = start
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j < len(lines):
            return j, lines[j].strip()
        return j, None

    # Bullet prefixes that should participate in forward-joining
    _BULLET_RE = re.compile(r"^(?:- |\* |\d+\.\s)")
    # Non-bullet structural lines that should NEVER join
    _HARD_STRUCTURAL_RE = re.compile(r"^(?:#|\||\<img|\<a\s|\<div\s|\*\*Legend:\*\*)")
    # Lines containing inline HTML spans/divs are intentionally formatted;
    # they should never be joined or consumed as continuation lines.
    _INLINE_HTML_RE = re.compile(r"<(?:span|div)\s")
    # Running page headers: "Section Title [Link](#anchor)" patterns
    # that repeat on every page of the original filing.
    _PAGE_HEADER_LINK_RE = re.compile(r"^[A-Z].*\[.*\]\(#[^)]+\)\s*$")

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip blank lines and hard-structural lines (headers, tables, images)
        if (
            not stripped
            or _HARD_STRUCTURAL_RE.match(stripped)
            or _INLINE_HTML_RE.search(stripped)
            or _PAGE_HEADER_LINK_RE.match(stripped)
        ):
            result.append(line)
            i += 1
            continue

        # --- Iterative joining loop ---
        is_bullet = bool(_BULLET_RE.match(stripped))
        joined_any = True
        join_count = 0

        while joined_any:
            joined_any = False

            # 1) Hyphenated word split: "pre-" ... "tax" → "pre-tax"
            if line.rstrip().endswith("-") and not line.rstrip().endswith("--"):
                j, nxt = _next_nonblank(i + 1)

                if nxt and nxt[0].islower():
                    m = re.match(r"^(\S+)(.*)", nxt)
                    if m:
                        line = line.rstrip()[:-1] + m.group(1) + m.group(2)
                        i = j + 1
                        join_count += 1
                        joined_any = True
                        continue

            cur_stripped = line.strip()

            # 2) Line ends with a connecting word → ALWAYS continuation
            #    (regardless of next-line case)
            if _CONNECTING_RE.search(line.rstrip()):
                j, nxt = _next_nonblank(i + 1)

                if nxt and _is_joinable_line(nxt):
                    line = line.rstrip() + " " + nxt
                    i = j + 1
                    join_count += 1
                    joined_any = True
                    continue

            # 3) General mid-sentence: line does NOT end with sentence-terminal
            #    punctuation → join with next non-structural line.
            #    3a) next starts lowercase → always join
            #    3b) current line is >30 chars AND first join attempt → join
            #        (guards against runaway merging: titles/references that
            #         don't end with punctuation won't chain into the next
            #         paragraph after the first join)
            #    3c) line ends with continuation punctuation (, ; &) → join
            #        Also handles quoted forms like ,"  or ;"
            _end_stripped = cur_stripped.rstrip("\"\u201d\u2019\u2018'")
            _has_cont_punct = _end_stripped.endswith((",", ";", "&"))

            if (
                not cur_stripped.endswith((".", "!", "?", ":", '"', "\u201d"))
                or _has_cont_punct
            ):
                j, nxt = _next_nonblank(i + 1)

                if nxt and _is_joinable_line(nxt):
                    should_join = (
                        nxt[0].islower()
                        or (
                            len(cur_stripped) > 30 and join_count == 0 and not is_bullet
                        )
                        or _has_cont_punct
                    )

                    if should_join:
                        line = line.rstrip() + " " + nxt
                        i = j + 1
                        join_count += 1
                        joined_any = True
                        continue

            # 4) Abbreviation / mid-sentence period: line ends with "." but
            #    next non-blank starts lowercase → definitely a continuation
            #    (handles "U.S." / "Inc." / "No." at visual line-wrap boundary)
            if cur_stripped.endswith("."):
                j, nxt = _next_nonblank(i + 1)

                if nxt and _is_joinable_line(nxt) and nxt[0].islower():
                    line = line.rstrip() + " " + nxt
                    i = j + 1
                    join_count += 1
                    joined_any = True
                    continue

            # 5) Unclosed quote: line contains an opening " (or ")
            #    that hasn't been closed yet → we're inside a quoted
            #    reference (e.g. refer to "Part II, Item 7.)
            #    The period/punctuation is NOT sentence-terminal.
            _quote_chars = cur_stripped.count('"') + cur_stripped.count("\u201c")
            _close_chars = cur_stripped.count("\u201d")
            # For straight quotes, odd count means unclosed; for smart
            # quotes, more openers than closers means unclosed.
            _has_unclosed = (cur_stripped.count("\u201c") > _close_chars) or (
                cur_stripped.count('"') % 2 == 1
                and "\u201c" not in cur_stripped
                and "\u201d" not in cur_stripped
            )

            if _has_unclosed:
                j, nxt = _next_nonblank(i + 1)

                if nxt and _is_joinable_line(nxt):
                    line = line.rstrip() + " " + nxt
                    i = j + 1
                    join_count += 1
                    joined_any = True
                    continue

        result.append(line)
        i += 1

    return "\n".join(result)


def _remove_repeated_page_elements(markdown: str) -> str:
    """
    Remove repeated page footer/header patterns from markdown.

    Detects short text patterns that appear many times (5+) in the document,
    which are likely page headers or footers that got repeated during conversion.

    Examples of patterns this catches:
    - "- 32 2025 Annual Meeting of Stockholders"
    - "Company Name | Page 5"
    - "CONFIDENTIAL"
    """
    lines = markdown.split("\n")

    # Find candidate repeated lines (short lines that appear multiple times)
    # Normalize lines by stripping and replacing page numbers with placeholder
    def normalize_line(line: str) -> str:
        """Normalize a line for comparison by replacing variable parts."""
        normalized = line.strip()
        # Replace page numbers (standalone digits) with placeholder
        normalized = re.sub(r"\b\d{1,3}\b", "#", normalized)
        # Replace markdown image URLs with placeholder, but keep the image marker
        # so we can distinguish "text with image" from "standalone image"
        normalized = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"![IMG]", normalized)
        # Also replace HTML <img> tags with placeholder
        normalized = re.sub(r"<img[^>]+>", "[IMG]", normalized)
        return normalized

    # Count normalized patterns
    line_counts: Counter = Counter()

    for line in lines:
        stripped = line.strip()
        normalized = normalize_line(stripped)
        # Only consider lines that normalize to short patterns (< 80 chars after normalization)
        # that aren't empty, headers, table rows, or STANDALONE images
        # Standalone images like ![LOGO](url) or <img ...> should NOT be removed
        if (
            normalized
            and len(normalized) < 80
            and not stripped.startswith("#")  # Not a header
            and not stripped.startswith("|")  # Not a table row
            and not stripped.startswith("[")  # Not a link
            and not re.match(r"^!\[", stripped)  # Not a standalone markdown image
            and not re.match(r"^<img\s", stripped)  # Not a standalone HTML image
            and not re.match(r"^<div[\s>]", stripped)  # Not an HTML div block
            and stripped != "---"
        ):  # Not a horizontal rule
            line_counts[normalized] += 1

    # Find patterns that repeat 5+ times (likely page footers/headers)
    repeated_patterns = {
        pattern for pattern, count in line_counts.items() if count >= 5
    }

    if not repeated_patterns:
        return markdown

    # Filter out the repeated lines
    filtered_lines = []
    for line in lines:
        stripped = line.strip()
        normalized = normalize_line(stripped)
        if normalized in repeated_patterns:
            # Skip this repeated page element
            continue
        filtered_lines.append(line)

    return "\n".join(filtered_lines)


# ============================================================================
# TABLE HELPER FUNCTIONS
# ============================================================================


def _classify_table(table_elem) -> str:
    """
    Unified table classifier. Returns one of:
    - "BULLET": Table with bullet characters → extract as bullet list
    - "FOOTNOTE": Table with footnote markers (*, (1), (a)) → extract as text
    - "HEADER": Single-cell section header → extract as markdown header
    - "DATA": Everything else → render as markdown table (DEFAULT)

    The key principle: be CONSERVATIVE about extracting as text.
    When in doubt, render as a table. Tables are data; don't lose structure.
    """
    rows = table_elem.find_all("tr")
    if not rows:
        return "DATA"

    # Collect info about the table structure
    non_empty_rows = []
    for row in rows:
        cells = row.find_all(["td", "th"])
        cell_texts = [c.get_text(strip=True) for c in cells]
        non_empty_texts = [t for t in cell_texts if t]
        if non_empty_texts:
            non_empty_rows.append((cells, non_empty_texts))

    if not non_empty_rows:
        return "DATA"

    # Check for bullet list (actual bullet characters, not asterisk which is a footnote marker)
    bullet_rows = 0
    for cells, texts in non_empty_rows:
        for text in texts[:2]:
            if text in BULLET_CHARS:
                bullet_rows += 1
                break

    if bullet_rows >= 1 and bullet_rows >= len(non_empty_rows) * 0.5:
        return "BULLET"

    # ===== CHECK FOR FOOTNOTE TABLE =====
    # Table where first non-empty cell is a footnote marker
    # Markers: *, **, †, ‡, (1), (2), (a), (b), etc.
    footnote_pattern = re.compile(r"^[\*†‡§¶]+$|^\(\d+\)$|^\([a-z]\)$|^\d+[\.\)]$")

    # Count rows that look like footnotes
    footnote_rows = 0
    for cells, texts in non_empty_rows:
        if len(texts) >= 2:
            first_text = texts[0]
            if footnote_pattern.match(first_text):
                footnote_rows += 1

    # If ALL multi-column rows are footnote-style, treat as footnote table.
    # Single-column rows are neutral continuation text (e.g. "The following
    # table sets forth the reconciliation...") and should not disqualify the
    # table from FOOTNOTE classification.
    candidate_rows = sum(1 for _, texts in non_empty_rows if len(texts) >= 2)
    if candidate_rows >= 1 and footnote_rows == candidate_rows:
        return "FOOTNOTE"

    # ===== CHECK FOR SECTION HEADER =====
    # Single row, single non-empty cell, typically bold or has id attribute
    if len(non_empty_rows) == 1:
        cells, texts = non_empty_rows[0]
        if len(texts) == 1:
            text = texts[0]
            cell = None
            for c in cells:
                if c.get_text(strip=True) == text:
                    cell = c
                    break

            if cell and len(text) < 100:
                # Check for header indicators
                has_toc_id = any(c.get("id", "").startswith("toc") for c in cells)
                is_bold = cell.find(["b", "strong"]) is not None
                # Also check for font-weight:bold in CSS
                if not is_bold:
                    is_bold = (
                        cell.find(
                            style=re.compile(r"font-weight:\s*bold", re.IGNORECASE)
                        )
                        is not None
                    )
                # If it looks like a section header, extract as header
                if has_toc_id or (is_bold and len(text) < 60):
                    return "HEADER"

    # ===== DEFAULT: DATA TABLE =====
    return "DATA"


def _extract_bullet_list(table_elem) -> str | None:
    """Extract bullet list from table format.

    Note: * is NOT included as it's typically a footnote marker, not a bullet.

    Special handling: If the content cell has a bold header at the beginning,
    format as a subsection header (#### Header) followed by the description.
    """
    bullets = []
    rows = table_elem.find_all("tr")

    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 2:
            bullet_col = -1
            for idx, cell in enumerate(cells[:2]):
                if cell.get_text(strip=True) in BULLET_CHARS:
                    bullet_col = idx
                    break

            if bullet_col >= 0:
                content_cell = (
                    cells[bullet_col + 1] if bullet_col + 1 < len(cells) else None
                )
                if content_cell:
                    # Check if this cell starts with bold text (subsection header pattern)
                    bold_elem = content_cell.find(["b", "strong"])
                    if not bold_elem:
                        # Check for font-weight:bold in nested divs
                        bold_elem = content_cell.find(
                            style=re.compile(r"font-weight:\s*bold", re.IGNORECASE)
                        )

                    if bold_elem:
                        # Use separator=" " to preserve spacing between inline elements
                        bold_text = bold_elem.get_text(separator=" ").strip()
                        bold_text = re.sub(
                            r"\s+", " ", bold_text
                        )  # Normalize whitespace
                        full_text = content_cell.get_text(separator=" ", strip=True)
                        full_text = _clean_html_entities(full_text)
                        full_text = re.sub(r"\s+", " ", full_text).strip()

                        # If bold text is at the start and there's more content after
                        if (
                            full_text.startswith(bold_text)
                            and len(full_text) > len(bold_text) + 5
                        ):
                            # This is a subsection header: "**Header**. Description..."
                            rest = full_text[len(bold_text) :].strip()
                            if rest.startswith("."):
                                rest = rest[1:].strip()
                            bullets.append(f"**{bold_text}**. {rest}")
                        else:
                            # Just bold text with no description
                            bullets.append(f"**{bold_text}**")
                    else:
                        # Regular bullet item
                        text = " ".join(
                            c.get_text(separator=" ", strip=True)
                            for c in cells[bullet_col + 1 :]
                        )
                        text = _clean_html_entities(text)
                        text = re.sub(r"\s+", " ", text).strip()
                        if text and len(text) > 3:
                            bullets.append(f"- {text}")
        elif len(cells) == 1:
            text = cells[0].get_text(separator=" ", strip=True)
            text = _clean_html_entities(text)
            text = re.sub(r"\s+", " ", text).strip()
            if text and text[0] in BULLET_CHARS:
                text = text[1:].strip()
                if text:
                    bullets.append(f"- {text}")

    return "\n\n".join(bullets) if bullets else None


def _extract_footnote_text(table_elem) -> str | None:
    """Extract footnote table as 'marker text' format."""
    parts = []
    rows = table_elem.find_all("tr")

    for row in rows:
        cells = row.find_all(["td", "th"])
        texts = []
        for cell in cells:
            text = cell.get_text(separator=" ", strip=True)
            text = _clean_html_entities(text)
            text = re.sub(r"\s+", " ", text).strip()
            if text:
                texts.append(text)

        if len(texts) >= 2:
            # Join marker with its text
            parts.append(" ".join(texts))
        elif len(texts) == 1:
            parts.append(texts[0])

    return "\n\n".join(parts) if parts else None


def _convert_layout_table(table_elem, base_url: str = "") -> str | None:
    """Convert layout tables with multi-line content cells to formatted sections.

    Detects tables where cells contain multiple block elements (like bullet lists
    of checkmark items) and converts them to section headers with bullet lists
    instead of trying to force them into markdown table format.

    Handles three patterns:
    1. Single-column tables with cells containing multiple divs (checkmark lists)
    2. Multi-column tables where one column has headers and another has bullet items (same row)
    3. Tables with alternating header rows and bullet rows
    """
    rows = table_elem.find_all("tr")

    if not rows:
        return None

    # Check if this is a multi-column data table with a header row (not a layout table)
    # Look for a row that has 3+ cells with bold text (indicating a header row)
    for row in rows:
        cells = row.find_all(["td", "th"])
        bold_content_cells = 0
        for cell in cells:
            text = cell.get_text(strip=True)
            if text and text not in ["\xa0", " ", ""]:
                # Check if this cell has bold text
                bold = cell.find(["b", "strong"]) or cell.find(
                    style=re.compile(
                        r"font-weight:\s*(?:bold|bolder|[6-9]00)",
                        re.IGNORECASE,
                    )
                )
                if bold:
                    bold_content_cells += 1
        # If this row has 3+ bold content cells, it's a real data table header
        if bold_content_cells >= 3:
            return None  # Let regular table processing handle this

    # Helper to extract bullet items from a cell with embedded bullets
    def extract_bullet_items(cell):
        """Extract bullet items from a cell containing divs with bullets at start."""
        items = []
        divs = cell.find_all("div", recursive=True)
        for div in divs:
            # Skip empty divs
            div_text = div.get_text(strip=True)
            if not div_text or div_text in ["\xa0", " ", ""]:
                continue
            # Skip divs that are purely containers of other divs
            if div.find("div") and len(div.find_all(string=True, recursive=False)) == 0:
                continue

            # Check if this div starts with a bullet character
            first_char = div_text[0] if div_text else ""
            if first_char in BULLET_CHARS:
                # Convert images in this div
                for img in div.find_all("img"):
                    img.replace_with(_convert_image_to_html(img, base_url))

                text = div.get_text(separator=" ", strip=True)
                text = _clean_html_entities(text)
                text = re.sub(r"\s+", " ", text).strip()
                # Remove leading bullet
                if text and text[0] in BULLET_CHARS:
                    text = text[1:].strip()
                if text:
                    items.append(text)
        return items

    # Helper to extract header text from a cell
    def extract_header_text(cell):
        """Extract header text and anchor ID, handling multi-line name cells.

        Returns tuple of (anchor_id, text) where anchor_id may be None.
        """
        lines = []
        anchor_id = cell.get("id")

        # Also check nested divs for anchor ID
        if not anchor_id:
            for div in cell.find_all("div"):
                div_id = div.get("id")
                if div_id:
                    anchor_id = div_id
                    break

        # First try to get text from bold elements
        for bold in cell.find_all(["b", "strong"]):
            text = bold.get_text(separator=" ", strip=True)
            text = re.sub(r"\s+", " ", text).strip()
            if text and text not in ["\xa0", " "]:
                lines.append(text)

        # Also check for font-weight:bold in style
        if not lines:
            bold_styled = cell.find(
                style=re.compile(r"font-weight:\s*bold", re.IGNORECASE)
            )
            if bold_styled:
                text = bold_styled.get_text(separator=" ", strip=True)
                text = re.sub(r"\s+", " ", text).strip()
                if text and text not in ["\xa0", " "]:
                    lines.append(text)

        # If no bold elements, try divs
        if not lines:
            for div in cell.find_all("div", recursive=False):
                text = div.get_text(separator=" ", strip=True)
                text = re.sub(r"\s+", " ", text).strip()
                if text and text not in ["\xa0", " "]:
                    lines.append(text)

        text = (
            " ".join(lines)
            if lines
            else cell.get_text(separator=" ", strip=True).strip()
        )
        return (anchor_id, text)

    # Helper to check if a row is a header-only row (bold text, no bullets)
    def is_header_row(row):
        """Check if this row contains only header text (bold, no bullets)."""
        cells = row.find_all(["td", "th"])
        row_text = ""
        has_bold = False
        has_bullets = False

        for cell in cells:
            text = cell.get_text(strip=True)
            if text and text not in ["\xa0", " "]:
                row_text += text
                # Check for bold
                if cell.find(["b", "strong"]) or cell.find(
                    style=re.compile(r"font-weight:\s*bold", re.IGNORECASE)
                ):
                    has_bold = True
                # Check for bullets
                if extract_bullet_items(cell):
                    has_bullets = True

        # It's a header row if it has bold text, no bullets, and reasonable length
        return has_bold and not has_bullets and row_text and len(row_text) < 150

    # ===== PATTERN 0: Bio-style tables with rowspan paragraph cells =====
    # Detect tables that have cells with rowspan containing paragraph content
    # (e.g., director biographies in proxy statements)
    bio_sections = []
    for row in rows:
        cells = row.find_all(["td", "th"])
        for cell in cells:
            rowspan = int(cell.get("rowspan", 1) or 1)
            if rowspan > 1:
                # This cell spans multiple rows - check if it has paragraph content
                cell_text = cell.get_text(strip=True)
                # Bio cells typically have 200+ characters of paragraph text
                if len(cell_text) > 200:
                    # Found a potential bio cell - extract header from same or nearby rows
                    # Look for a bold name cell in an earlier row of this table
                    name_text = None

                    # Search backward through rows for header
                    row_idx = rows.index(row)
                    for prev_idx in range(row_idx - 1, -1, -1):
                        prev_row = rows[prev_idx]
                        prev_cells = prev_row.find_all(["td", "th"])
                        for prev_cell in prev_cells:
                            prev_text = prev_cell.get_text(strip=True)
                            if not prev_text or prev_text in ["\xa0", " "]:
                                continue
                            # Check for bold name
                            bold = prev_cell.find(["b", "strong"]) or prev_cell.find(
                                style=re.compile(r"font-weight:\s*bold", re.IGNORECASE)
                            )
                            # A name is typically short, bold, and all caps or title case
                            if bold and len(prev_text) < 50 and prev_text.isupper():
                                name_text = prev_text
                                break
                        if name_text:
                            break

                    # Also extract metadata from the same row (title, tenure, age, etc.)
                    metadata_items = []
                    seen_metadata = set()
                    for other_cell in cells:
                        if other_cell == cell:
                            continue
                        other_text = other_cell.get_text(strip=True)
                        if not other_text or other_text in ["\xa0", " "]:
                            continue
                        # Skip if too long (probably another bio)
                        if len(other_text) > 150:
                            continue
                        # Extract items from divs (direct children only)
                        for div in other_cell.find_all("div", recursive=False):
                            div_text = div.get_text(strip=True)
                            div_text = _clean_html_entities(div_text)
                            div_text = re.sub(r"\s+", " ", div_text).strip()
                            if (
                                div_text
                                and div_text not in ["\xa0", " ", ""]
                                and div_text not in seen_metadata
                            ):
                                metadata_items.append(div_text)
                                seen_metadata.add(div_text)

                    # Extract bio paragraphs from the cell
                    # Only get top-level divs to avoid duplicates from nested divs
                    bio_paragraphs = []
                    seen_texts = set()
                    for div in cell.find_all("div", recursive=False):
                        div_text = div.get_text(strip=True)
                        div_text = _clean_html_entities(div_text)
                        div_text = re.sub(r"\s+", " ", div_text).strip()
                        if (
                            div_text
                            and div_text not in ["\xa0", " ", ""]
                            and len(div_text) > 20
                            and div_text not in seen_texts
                        ):
                            bio_paragraphs.append(div_text)
                            seen_texts.add(div_text)

                    if bio_paragraphs:
                        bio_sections.append(
                            {
                                "name": name_text,
                                "metadata": metadata_items,
                                "paragraphs": bio_paragraphs,
                            }
                        )

    # If we found bio sections, format them
    if bio_sections:
        result_parts = []
        for section in bio_sections:
            if section["name"]:
                result_parts.append(f"\n**{section['name']}**\n")
            for item in section.get("metadata", []):  # type: ignore
                result_parts.append(f"- {item}")
            if section["metadata"]:
                result_parts.append("")  # Blank line after metadata
            for para in section.get("paragraphs", []):  # type: ignore
                result_parts.append(para)
                result_parts.append("")  # Blank line after each paragraph
        if result_parts:
            return "\n".join(result_parts)

    # ===== PATTERN 2: Multi-column table with headers and bullet content in SAME row =====
    # Check if this is a table with header column + bullet column
    result_sections = []

    for row in rows:
        cells = row.find_all(["td", "th"])
        if not cells:
            continue

        # Find cells with content
        header_cell = None
        bullet_cell = None

        for cell in cells:
            cell_text = cell.get_text(strip=True)
            if not cell_text or cell_text in ["\xa0", " "]:
                continue

            # Check if this cell contains bullet items
            bullet_items = extract_bullet_items(cell)
            if bullet_items:
                bullet_cell = (cell, bullet_items)
            else:
                # Check if this looks like a header cell (bold, short text)
                bold = cell.find(["b", "strong"]) or cell.find(
                    style=re.compile(r"font-weight:\s*bold", re.IGNORECASE)
                )
                if bold and len(cell_text) < 200:
                    header_cell = cell

        if bullet_cell:
            header_anchor = None
            header_text = ""
            if header_cell:
                header_anchor, header_text = extract_header_text(header_cell)

            result_sections.append((header_anchor, header_text, bullet_cell[1]))

    # If we found header+bullet sections (same row), format them
    # Only use this pattern if we found headers for at least some rows
    if result_sections:
        has_headers = any(h for _, h, _ in result_sections)
        if has_headers:
            result_parts = []
            for header_anchor, header_text, bullet_items in result_sections:
                if header_text:
                    if header_anchor:
                        result_parts.append(
                            f'\n<a id="{header_anchor}"></a>**{header_text}**\n'
                        )
                    else:
                        result_parts.append(f"\n**{header_text}**\n")
                for item in bullet_items:
                    result_parts.append(f"- {item}")
                result_parts.append("")

            if result_parts:
                return "\n".join(result_parts)

    # ===== PATTERN 3: Alternating header rows and bullet rows =====
    # Process rows in sequence, building sections
    sections = []
    current_header = ""
    current_anchor = None
    current_bullets = []

    for row in rows:
        cells = row.find_all(["td", "th"])
        if not cells:
            continue

        row_text = "".join(c.get_text(strip=True) for c in cells)
        if not row_text or row_text in ["\xa0", " "]:
            continue

        # Collect all bullet items from this row
        row_bullets = []
        for cell in cells:
            row_bullets.extend(extract_bullet_items(cell))

        if row_bullets:
            # This is a bullet row
            current_bullets.extend(row_bullets)
        elif is_header_row(row):
            # This is a header row
            # Save previous section if exists
            if current_bullets:
                sections.append((current_anchor, current_header, current_bullets))
                current_bullets = []

            # Get header text and anchor from this row
            header_parts = []
            current_anchor = None
            for cell in cells:
                anchor_id, text = extract_header_text(cell)
                if anchor_id and not current_anchor:
                    current_anchor = anchor_id
                if text and text not in ["\xa0", " "]:
                    header_parts.append(text)
            current_header = " ".join(header_parts)

    # Don't forget the last section
    if current_bullets:
        sections.append((current_anchor, current_header, current_bullets))

    # If we found alternating sections, format them
    if sections and len(sections) >= 1:
        # Verify this looks like a structured document (not just random bullets)
        total_bullets = sum(len(s[2]) for s in sections)
        if total_bullets >= 3:
            result_parts = []
            for header_anchor, header_text, bullet_items in sections:
                if header_text:
                    if header_anchor:
                        result_parts.append(
                            f'\n<a id="{header_anchor}"></a>**{header_text}**\n'
                        )
                    else:
                        result_parts.append(f"\n**{header_text}**\n")
                for item in bullet_items:
                    result_parts.append(f"- {item}")
                result_parts.append("")

            if result_parts:
                return "\n".join(result_parts)

    # ===== PATTERN 1: Single column with multi-div cells (checkmark lists) =====
    # First, find the header row (if any) and content rows
    header_cells: list = []
    content_cells: list = []

    for row in rows:
        cells = row.find_all(["td", "th"])

        # Check if this row looks like a header row
        is_header = False
        if row.find("th"):
            is_header = True
        else:
            # Check if cells have bold text and minimal content (header-like)
            for cell in cells:
                text = cell.get_text(strip=True)
                if text and len(text) < 80:
                    bold = cell.find(["b", "strong"]) or cell.find(
                        style=re.compile(r"font-weight:\s*bold", re.IGNORECASE)
                    )
                    if bold:
                        is_header = True
                        break

        if is_header and not header_cells:
            for cell in cells:
                text = cell.get_text(strip=True)
                if text and text not in ["\xa0", " "]:
                    header_cells.append(text)
        else:
            # This is a content row - check for multi-line cells
            for cell in cells:
                # Count meaningful divs in this cell
                content_divs = []
                for div in cell.find_all("div", recursive=False):
                    div_text = div.get_text(strip=True)
                    if div_text and div_text not in ["\xa0", " ", ""]:
                        content_divs.append(div)

                if len(content_divs) >= 3:
                    # This cell has multiple items - extract them
                    items = []
                    for div in content_divs:
                        # Convert images in this div
                        for img in div.find_all("img"):
                            img.replace_with(_convert_image_to_html(img, base_url))

                        text = div.get_text(separator=" ", strip=True)
                        text = _clean_html_entities(text)
                        text = re.sub(r"\s+", " ", text).strip()
                        if text:
                            items.append(text)

                    if items:
                        content_cells.append(items)

    # If we didn't find any multi-line content cells, this isn't a layout table
    if not content_cells:
        return None

    # Build the output: pair headers with their content lists
    result_parts = []

    for i, items in enumerate(content_cells):
        if i < len(header_cells):
            # Add header
            result_parts.append(f"\n**{header_cells[i]}**\n")

        # Add items as bullet list
        for item in items:
            result_parts.append(f"- {item}")
        result_parts.append("")  # Blank line after each section

    if result_parts:
        return "\n".join(result_parts)

    return None


def _extract_header_text(table_elem) -> str | None:
    """Extract single-cell header table as markdown header, preserving anchors."""
    rows = table_elem.find_all("tr")
    for row in rows:
        cells = row.find_all(["td", "th"])
        for cell in cells:
            text = cell.get_text(strip=True)
            if text:
                text = _clean_html_entities(text)
                text = re.sub(r"\s+", " ", text).strip()

                # Look for anchor id on the cell or nested divs
                anchor_id = cell.get("id")
                if not anchor_id:
                    # Check nested divs for id attribute
                    for div in cell.find_all("div"):
                        div_id = div.get("id")
                        if div_id:
                            anchor_id = div_id
                            break

                # Return as bold header with anchor if present
                if anchor_id:
                    return f'\n<a id="{anchor_id}"></a>**{text}**\n'
                return f"\n**{text}**\n"
    return None


def _extract_cell_text(
    cell, base_url: str = "", preserve_line_breaks: bool = False
) -> str:
    """Extract text from a table cell, preserving links and images as markdown.

    If preserve_line_breaks is True, detects cells with multiple block elements
    (like divs with checkmark images) and preserves them as separate lines.

    Always preserves <br> tags within cells as HTML line breaks.
    """
    # Check if this cell contains ONLY a footnote reference (sup tag with a number)
    # These appear in SEC tables as separate cells and should be merged with the label
    sup_tags = cell.find_all("sup")
    if sup_tags:
        # Get all text content excluding sup tags and invisible content
        non_sup_text = ""
        for elem in cell.descendants:
            if isinstance(elem, NavigableString):
                parent = elem.parent
                # Skip text inside sup tags
                is_in_sup = False
                while parent:
                    if parent.name == "sup":
                        is_in_sup = True
                        break
                    parent = parent.parent
                if not is_in_sup:
                    # Not inside a sup tag - check if it's visible text
                    text = str(elem).strip()
                    # Skip hidden/invisible content (zero-width spaces, nbsp, etc)
                    if text and text not in ["\u200b", "\xa0", " ", ""]:
                        non_sup_text += text

        non_sup_text = non_sup_text.strip()
        if not non_sup_text:
            # Cell only has sup content - check if it's a footnote reference (small number)
            sup_text = " ".join(sup.get_text(strip=True) for sup in sup_tags)
            # Footnote references are typically 1-3 digit numbers
            if re.match(r"^\s*\d{1,3}\s*$", sup_text):
                # Return as superscript HTML - will be merged with previous cell later
                return f"<sup>{sup_text.strip()}</sup>"

    # Work on a copy so we don't mutate the original
    cell_copy = copy(cell)

    # Convert BR tags to a space so they don't leak as literal "<br>" into markdown.
    # In preserve_line_breaks mode keep a newline marker instead.
    for br in cell_copy.find_all("br"):
        br.replace_with(" " if not preserve_line_breaks else "\n")

    # Check if this cell has multiple block-level divs with content (like bullet lists)
    # This detects layout cells that should NOT be flattened
    content_divs = []
    for div in cell_copy.find_all("div", recursive=False):
        div_text = div.get_text(strip=True)
        # Skip empty divs and spacer divs (just nbsp)
        if div_text and div_text not in ["\xa0", " ", ""]:
            content_divs.append(div)

    # If cell has 3+ content divs, treat as multi-line content
    if preserve_line_breaks and len(content_divs) >= 3:
        lines = []
        for div in content_divs:
            # Convert images in this div
            for img in div.find_all("img"):
                img.replace_with(_convert_image_to_html(img, base_url))
            # Convert links in this div
            for a in div.find_all("a"):
                href = a.get("href", "")
                link_text = a.get_text(strip=True)
                if href and link_text:
                    if base_url and not href.startswith(("#", "http://", "https://")):
                        href = urljoin(base_url, href)
                    a.replace_with(f"[{link_text}]({href})")
                elif link_text:
                    a.replace_with(link_text)

            text = div.get_text(separator=" ", strip=True)
            text = _clean_html_entities(text)
            text = re.sub(r"\s+", " ", text).strip()
            if text:
                lines.append(text)

        if lines:
            # Return with special marker for multi-line cells
            return "\n".join(lines)

    # Standard single-line extraction
    # Convert links to markdown format
    for a in cell_copy.find_all("a"):
        href = a.get("href", "")
        link_text = a.get_text(strip=True)
        if href and link_text:
            if base_url and not href.startswith(("#", "http://", "https://")):
                href = urljoin(base_url, href)
            a.replace_with(f"[{link_text}]({href})")
        elif link_text:
            a.replace_with(link_text)

    # Strip images from table cells — SEC filings use <img> for decorative
    # elements (brackets, braces, spacers) that have no textual meaning.
    # Use the alt attribute only if it carries actual content (not the generic
    # "Image" placeholder that BeautifulSoup/browsers supply by default).
    for img in cell_copy.find_all("img"):
        alt = img.get("alt", "").strip()
        img.replace_with(alt if alt and alt.lower() not in ("image", "img", "") else "")

    # Get text with space separator
    text = cell_copy.get_text(separator=" ", strip=True)
    text = _clean_html_entities(text)
    text = re.sub(r"\s+", " ", text).strip()
    # Common word-fragment suffixes that indicate a broken word, not a compound
    _WORD_SUFFIXES = r"MENTS|MENT|TIONS|ATED|TING|NESS|ABLE|IBLE"
    # Rejoin words broken by line wrapping in narrow HTML columns
    # Pattern 1: "ADJUST- MENTS" → "ADJUSTMENTS" (soft hyphen, no <br>)
    text = re.sub(r"(\w)- (?!<br>)(\w)", r"\1\2", text)
    # Pattern 2a: "ADJUST- <br> MENTS" → "ADJUSTMENTS" (word-break hyphen + br)
    # When the continuation is a word fragment (suffix), remove the hyphen
    text = re.sub(rf"(\w)- (?:<br> ?)+({_WORD_SUFFIXES})\b", r"\1\2", text)
    # Pattern 2b: "PERCENTAGE- <br> POINT" → "PERCENTAGE-POINT" (compound + br)
    # When the continuation is a full word, keep the hyphen
    text = re.sub(r"(\w)- (?:<br> ?)+(\w)", r"\1-\2", text)
    # Pattern 3: "ADJUST MENTS" → "ADJUSTMENTS" (space from word-wrap in source)
    text = re.sub(
        rf"\b([A-Z]{{2,}}) ({_WORD_SUFFIXES})\b",
        r"\1\2",
        text,
    )
    # Normalize <br> spacing: " <br> " → "<br>"
    text = re.sub(r"\s*<br>\s*", "<br>", text)
    return text


def _clean_html_entities(text: str) -> str:
    """Clean common HTML entities."""
    replacements = {
        "&nbsp;": " ",
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
        "&quot;": '"',
        "&#39;": "'",
        "&apos;": "'",
        "&#149;": "•",
        "&#160;": " ",
        "\xa0": " ",
        "\u200b": "",
        "Ø": "•",
    }

    for entity, replacement in replacements.items():
        text = text.replace(entity, replacement)

    return text
