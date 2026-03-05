"""
Non-XBRL Statement Parser

A completely separate module for parsing pre-XBRL SEC filings (pre-2009).
These filings embed financial data in HTML tables without structured XBRL tagging.

This module is intentionally isolated from the XBRL parsing logic.
"""

import re

import pandas as pd
from bs4 import BeautifulSoup


def parse_non_xbrl_statement(
    html_content: str,
    statement_type: str = "income",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Parse financial statements from non-XBRL HTML filings.

    Parameters
    ----------
    html_content : str
        The raw HTML content of the filing document.
    statement_type : str
        Type of statement to extract: 'income', 'balance', 'cash', 'equity'

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        A tuple of (statement_df, meta_df).
        - statement_df: One row per line item, columns for label + each period's value
        - meta_df: Metadata about the statement (title, periods, scale, etc.)
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Find the statement table based on keywords
    statement_keywords = _get_statement_keywords(statement_type)

    # Get all tables
    all_tables = soup.find_all("table")

    best_table = None
    best_score = 0

    for table in all_tables:
        table_text = table.get_text(separator=" ", strip=True).lower()

        # Score based on keyword matches
        score = sum(1 for kw in statement_keywords if kw.lower() in table_text)

        # Skip tables that are likely table of contents or index
        if score > 0:
            # Skip tables that look like table of contents
            if "page no" in table_text or "item 1:" in table_text:
                # This is probably a TOC - penalize heavily
                score = max(0, score - 5)
                if score <= 0:
                    continue

            # Must have substantial numeric content (at least 10 numbers)
            numbers = re.findall(r"\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b", table_text)
            if len(numbers) < 10:
                continue

            # Bonus score for having scale indicator (in millions, etc.)
            if "in millions" in table_text or "in thousands" in table_text or "in billions" in table_text:
                score += 2

            # Bonus for having dollar signs (actual values)
            dollar_count = table_text.count("$")
            if dollar_count > 5:
                score += 1

            # Bonus for more numbers (more data)
            if len(numbers) > 30:
                score += 1

        if score > best_score:
            best_table = table
            best_score = score

    if best_table is None:
        return pd.DataFrame(), pd.DataFrame()

    # Extract data from the table
    result = _extract_table_data(best_table)
    if result is None:
        return pd.DataFrame(), pd.DataFrame()

    line_items, periods, multiplier, title = result

    if not line_items:
        return pd.DataFrame(), pd.DataFrame()

    # Build the statement DataFrame - one row per line item
    statement_df = _build_statement_dataframe(line_items, periods, multiplier)

    # Build the metadata DataFrame
    meta_df = _build_meta_dataframe(title, periods, multiplier)

    return statement_df, meta_df


def _get_statement_keywords(statement_type: str) -> list[str]:
    """Get keywords to identify statement type."""
    keywords = {
        "income": [
            "statements of earnings",
            "statements of income",
            "statements of operations",
            "net earnings",
            "net income",
            "total revenues",
        ],
        "balance": [
            "balance sheet",
            "financial condition",
            "financial position",
            "total assets",
            "total liabilities",
            "stockholders equity",
            "shareholders equity",
            "cash and cash equivalents",
        ],
        "cash": [
            "cash flows",
            "operating activities",
            "investing activities",
            "financing activities",
        ],
        "equity": [
            "stockholders equity",
            "shareholders equity",
            "changes in equity",
        ],
    }
    return keywords.get(statement_type, keywords["income"])


def _detect_multiplier(table) -> tuple[int, str]:
    """
    Detect value multiplier from table text.

    Returns (multiplier, scale_name).
    """
    table_text = table.get_text(separator=" ", strip=True).lower()

    if "in millions" in table_text or "(millions)" in table_text:
        return 1_000_000, "millions"
    elif "in thousands" in table_text or "(thousands)" in table_text:
        return 1_000, "thousands"
    elif "in billions" in table_text or "(billions)" in table_text:
        return 1_000_000_000, "billions"

    return 1, "units"


def _extract_table_data(
    table,
) -> tuple[list[dict], list[str], int, str | None] | None:
    """
    Extract structured data from a financial table.

    Returns tuple of (line_items, periods, multiplier, title) or None.
    Each line_item is a dict with 'label', 'section', and 'values' (list of floats).
    """
    rows = table.find_all("tr")
    if len(rows) < 5:
        return None

    multiplier, _ = _detect_multiplier(table)

    # Parse header rows to get period labels
    periods = _extract_periods(rows[:20])
    # Don't use placeholder garbage - if no headers found, we'll figure it out from data
    if not periods:
        # Count actual value columns from first few data rows
        for row in rows[1:10]:
            cells = row.find_all(["td", "th"])
            cell_texts = [_clean_cell_text(c) for c in cells]
            values = [c for c in cell_texts if c and re.match(r"^[\d,.\$\(\)-]+$", c.replace(",", "").replace("$", ""))]
            if len(values) >= 2:
                periods = [f"Col {i + 1}" for i in range(len(values))]
                break
        if not periods:
            periods = ["Value"]

    num_periods = len(periods)

    # Parse data rows
    line_items = []
    current_section = None
    title = None

    for row in rows:
        cells = row.find_all(["td", "th"])

        # Skip rows with too many cells (corrupted)
        if len(cells) > 50 or len(cells) == 0:
            continue

        cell_texts = [_clean_cell_text(c) for c in cells]

        # Skip empty rows
        if not any(cell_texts):
            continue

        # Skip header rows that contain period labels (e.g., "Year Ended June 30" with years)
        row_text = " ".join(cell_texts).lower()
        if _is_header_row(row_text, cell_texts):
            continue

        # Check for section header (single non-empty cell, ends with : or no numbers)
        non_empty = [c for c in cell_texts if c]
        if len(non_empty) == 1:
            text = non_empty[0].rstrip(":")
            if text and not re.search(r"\d", text) and len(text) < 100:
                current_section = text
                continue

        # Try to parse as data row
        parsed = _parse_data_row(cell_texts, num_periods)
        if parsed:
            label, values, skip_multiplier = parsed
            line_items.append(
                {
                    "label": label,
                    "section": current_section,
                    "values": values,
                    "skip_multiplier": skip_multiplier,
                }
            )

    if not line_items:
        return None

    return line_items, periods, multiplier, title


def _is_header_row(row_text: str, cell_texts: list[str]) -> bool:
    """
    Detect if a row is a header row that should be skipped.

    Header rows contain period descriptions like "Year Ended June 30"
    combined with year numbers like "1999", "2000", etc.
    """
    # Check for period descriptor phrases
    period_phrases = [
        "year ended",
        "years ended",
        "months ended",
        "month ended",
        "quarter ended",
        "quarters ended",
        "fiscal year",
        "fiscal years",
        "in millions",
        "in thousands",
        "in billions",
        "(except",
        "except per share",
    ]

    has_period_phrase = any(phrase in row_text for phrase in period_phrases)

    # Check if row contains standalone year numbers (4-digit years)
    year_pattern = r"\b(19|20)\d{2}\b"
    years_in_row = re.findall(year_pattern, " ".join(cell_texts))
    has_multiple_years = len(years_in_row) >= 2

    # It's a header if it has period phrases OR multiple years as standalone values
    if has_period_phrase:
        return True

    if has_multiple_years:
        # Check if the years appear as separate cell values (not embedded in text)
        standalone_years = 0
        for text in cell_texts:
            text = text.strip()
            # Year with optional footnote like "2001(2)" or "2001"
            if re.match(r"^(19|20)\d{2}(\s*\(\d+\))?$", text):
                standalone_years += 1
        if standalone_years >= 2:
            return True

    return False


def _extract_periods(header_rows) -> list[str]:
    """
    Extract column headers from header rows.

    Looks for patterns like:
    - Row with "Three Months Ended May" / "Six Months Ended May"
    - Row with years "1999" / "1998" / "1999" / "1998"
    - Row with column titles like "GROSS CARRYING AMOUNT", "NET VALUE"

    Combines them into full period labels.
    """
    period_prefixes = []  # e.g., ["Three Months Ended May", "Six Months Ended May"]
    years = []  # e.g., ["1999", "1998", "1999", "1998"]
    column_headers = []  # Non-period headers like "GROSS CARRYING AMOUNT"

    for row in header_rows:
        cells = row.find_all(["td", "th"])
        if len(cells) > 50:
            continue

        cell_texts = [_clean_cell_text(c) for c in cells]
        non_empty = [c for c in cell_texts if c]

        if not non_empty:
            continue

        row_text = " ".join(non_empty)

        # Look for period descriptions (e.g., "Three Months Ended")
        if re.search(r"(months? ended|year ended|quarter ended)", row_text, re.I):
            period_prefixes = [c for c in non_empty if re.search(r"(months?|year|quarter)", c, re.I)]

        # Look for years
        year_matches = re.findall(r"\b((?:19|20)\d{2})\b", row_text)
        if len(year_matches) >= 2 and not years:
            years = year_matches

        # Look for column headers (not years, not empty, likely uppercase or title case)
        # These are headers like "GROSS CARRYING AMOUNT", "BALANCE", "ADDITIONS"
        if not column_headers:
            header_keywords = [
                "amount",
                "balance",
                "value",
                "gross",
                "net",
                "carrying",
                "accumulated",
                "additions",
                "segment",
                "adjustments",
                "divestitures",
                "translation",
            ]

            potential_headers = []
            has_keyword = False
            for c in non_empty:
                # Skip if it's just a year
                if re.match(r"^(19|20)\d{2}$", c):
                    continue
                # Skip if it's a number
                if re.match(r"^[\d,.\$\(\)-]+$", c.replace(",", "")):
                    continue
                # Skip very short text
                if len(c) < 3:
                    continue
                # Skip common non-header text
                if c.lower() in ("$", "for the", "at"):
                    continue
                potential_headers.append(c)
                # Check if this header contains keywords
                if any(kw in c.lower() for kw in header_keywords):
                    has_keyword = True

            # If we found headers with keywords, use them (skip first column which is usually row labels)
            if has_keyword and len(potential_headers) >= 2:
                # First column is usually the row label header, skip it
                column_headers = potential_headers[1:] if len(potential_headers) > 2 else potential_headers

    # Combine prefixes with years
    if period_prefixes and years:
        # Match prefixes to years
        periods = []
        prefix_idx = 0
        for i, year in enumerate(years):
            if prefix_idx < len(period_prefixes):
                prefix = period_prefixes[prefix_idx]
                periods.append(f"{prefix} {year}")
                # Advance prefix index every 2 years (assuming 2 years per period type)
                if (i + 1) % 2 == 0:
                    prefix_idx += 1
            else:
                periods.append(year)
        return periods
    elif column_headers:
        # Prefer column headers over bare years
        return column_headers
    elif years:
        return years

    return []


def _clean_cell_text(cell) -> str:
    """Extract clean text from a cell."""
    text = cell.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _is_bullet_table(table_elem) -> bool:
    """Check if table is a bullet list (• in first column)."""
    rows = table_elem.find_all("tr")
    bullet_count = 0
    for row in rows[:5]:  # Check first 5 rows
        cells = row.find_all("td")
        if cells:
            first_cell = cells[0].get_text(strip=True)
            if first_cell in ("•", "&#149;", "*", "-", "—"):
                bullet_count += 1
    return bullet_count >= 1


def _extract_bullet_list(table_elem) -> str | None:
    """Extract bullet list from table format."""
    bullets = []
    rows = table_elem.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 2:
            first_cell = cells[0].get_text(strip=True)
            if first_cell in ("•", "&#149;", "*", "-", "—", ""):
                text = " ".join(c.get_text(separator=" ", strip=True) for c in cells[1:])
                text = _clean_html_entities(text)
                text = re.sub(r"\s+", " ", text).strip()
                if text and len(text) > 5:
                    bullets.append(f"- {text}")
    return "\n\n".join(bullets) if bullets else None


def _is_financial_table(table_elem) -> bool:
    """Check if table has numeric data (financial table)."""
    text = table_elem.get_text()
    # Count numbers with commas (financial values)
    numbers = re.findall(r"\d{1,3}(?:,\d{3})+", text)
    return len(numbers) >= 3


def _get_direct_text(elem) -> str:
    """Get text from direct children only, not nested P or TABLE."""
    from bs4.element import NavigableString

    parts = []
    for child in elem.children:
        if isinstance(child, NavigableString):
            text = str(child).strip()
            if text:
                parts.append(text)
        elif hasattr(child, "name") and child.name not in ["p", "table"]:
            text = child.get_text(strip=True)
            if text:
                parts.append(text)
    return " ".join(parts)


def _clean_paragraph_text(text: str) -> str | None:
    """Clean paragraph text for disclosure extraction."""
    if not text:
        return None
    text = _clean_html_entities(text)
    # Skip boilerplate and very short text
    if re.match(r"^\d+$", text):
        return None
    if len(text) < 5:
        return None
    if text in ("(UNAUDITED)", "(Continued)") or text.endswith("(Continued)"):
        return None
    if "PAGEBREAK" in text:
        return None
    # Skip page headers/footers
    if "page" in text.lower() and len(text) < 50:
        return None
    # Skip garbled table data (cells concatenated without spaces)
    if re.search(r"19\d{2}19\d{2}", text):
        return None
    if re.search(r"\$[\d,]+\$[\d,]+", text):
        return None
    if text.count("$") > 3:
        return None
    text = re.sub(r"\s+", " ", text)
    return text


def _is_section_header(elem) -> bool:
    """Check if P element is a section header (short bold text only)."""
    # Get direct B tags
    b_tags = [c for c in elem.children if hasattr(c, "name") and c.name == "b"]
    if len(b_tags) != 1:
        return False
    b_text = b_tags[0].get_text(strip=True)
    # Check length and that it's the only content
    direct_text = _get_direct_text(elem)
    if direct_text == b_text and 3 < len(b_text) < 60:
        # Exclude numbered items like "1. Former Partner..."
        return not re.match(r"^\d+\.", b_text)
    return False


def _parse_data_row(cell_texts: list[str], expected_values: int) -> tuple[str, list[float | None], bool] | None:
    """
    Parse a row into (label, values, is_per_share).

    Returns None if not a valid data row.
    is_per_share indicates if values should NOT have multiplier applied.
    """
    if not cell_texts:
        return None

    label = None
    values = []
    pending_negative = None  # Track numbers like "(14" waiting for ")"

    for cell in cell_texts:
        if not cell or cell in ("$", "—", "-", ""):
            continue

        # Handle closing paren for negative number from previous cell
        if cell == ")" and pending_negative is not None:
            values.append(-float(pending_negative))
            pending_negative = None
            continue

        # Check for opening paren negative like "(14"
        if cell.startswith("(") and not cell.endswith(")"):
            # Try to parse the number part
            num_part = cell[1:].replace(",", "")
            try:
                pending_negative = float(num_part)
                continue
            except ValueError:
                pass

        # Try to parse as number
        num = _parse_number(cell)
        if num is not None:
            values.append(num)
        elif label is None:
            # First text is the label
            label = cell

    # Must have a label
    if label is None:
        return None

    # Label sanity check - reject labels that are too long or contain embedded data
    if len(label) > 100:
        return None

    # Skip malformed labels that contain numbers (corrupted nested cells)
    # e.g., "Basic 474,712,271 474,712,271 Diluted 479,908,301"
    if re.search(r"\d{3},\d{3}", label):
        return None

    # Must have at least 1 value
    if not values:
        return None

    # Detect per-share items (EPS, etc.) - don't apply multiplier
    label_lower = label.lower()
    is_per_share = any(kw in label_lower for kw in ["per share", "basic", "diluted", "eps"])

    # Detect share count items - don't apply multiplier
    is_share_count = any(kw in label_lower for kw in ["shares", "share count", "units issued", "units outstanding"])

    # Skip multiplier for per-share or share count items
    skip_multiplier = is_per_share or is_share_count

    # Pad or truncate values to expected count
    if len(values) < expected_values:
        values.extend([None] * (expected_values - len(values)))
    elif len(values) > expected_values:
        values = values[:expected_values]

    return label, values, skip_multiplier


def _parse_number(text: str) -> float | None:
    """Parse text as a number, handling parentheses for negatives."""
    if not text:
        return None

    text = text.strip()

    # Handle parentheses for negative
    is_negative = text.startswith("(") and text.endswith(")")
    if is_negative:
        text = text[1:-1]

    # Remove commas
    cleaned = text.replace(",", "")

    # Must be numeric
    if not re.match(r"^-?\d+(\.\d+)?$", cleaned):
        return None

    value = float(cleaned)
    if is_negative:
        value = -value
    return value


def _build_statement_dataframe(line_items: list[dict], periods: list[str], multiplier: int) -> pd.DataFrame:
    """
    Build a DataFrame in long format matching XBRL output structure.

    Columns: order, tag, parent_tag, preferred_label, balance, weight, decimals,
             context_ref, period_beginning, period_ending, unit, label, value

    Each (line_item, period) combination becomes one row.
    Values are multiplied by the scale factor (except per-share items).
    """
    rows = []

    for order, item in enumerate(line_items, start=1):
        label = item["label"]
        section = item["section"]
        values = item["values"]
        skip_multiplier = item.get("skip_multiplier", False)

        # Apply multiplier unless per-share or share count
        scale = 1 if skip_multiplier else multiplier

        # Determine unit based on label
        label_lower = label.lower() if label else ""
        if any(kw in label_lower for kw in ["per share", "eps", "shares", "share count"]):
            unit = "shares" if "share" in label_lower and "per" not in label_lower else "USD/shares"
        else:
            unit = "USD"

        # Create one row per period
        for i, period in enumerate(periods):
            value = values[i] * scale if i < len(values) and values[i] is not None else None

            # Parse period_ending from period string (extract year)
            period_ending = _extract_period_ending(period)

            rows.append(
                {
                    "order": order,
                    "tag": None,  # No XBRL tag for non-XBRL filings
                    "parent_tag": section,  # Section heading is the parent
                    "preferred_label": None,
                    "balance": None,
                    "weight": None,
                    "decimals": None,
                    "context_ref": period,  # Use full period description
                    "period_beginning": None,  # Could be derived for income/cash statements
                    "period_ending": period_ending,
                    "unit": unit,
                    "label": label,
                    "value": value,
                }
            )

    return pd.DataFrame(rows)


def _extract_period_ending(period: str) -> str | None:
    """Extract a date string from a period label like 'Year Ended June 30 2003'."""
    # Try to find a 4-digit year
    year_match = re.search(r"\b(19|20)\d{2}\b", period)
    if not year_match:
        return None

    year = year_match.group(0)

    # Try to find month
    months = {
        "january": "01",
        "february": "02",
        "march": "03",
        "april": "04",
        "may": "05",
        "june": "06",
        "july": "07",
        "august": "08",
        "september": "09",
        "october": "10",
        "november": "11",
        "december": "12",
        "jan": "01",
        "feb": "02",
        "mar": "03",
        "apr": "04",
        "jun": "06",
        "jul": "07",
        "aug": "08",
        "sep": "09",
        "oct": "10",
        "nov": "11",
        "dec": "12",
    }

    period_lower = period.lower()
    for month_name, month_num in months.items():
        if month_name in period_lower:
            # Try to find day
            day_match = re.search(rf"{month_name}\s+(\d{{1,2}})", period_lower)
            if day_match:
                day = day_match.group(1).zfill(2)
            else:
                # Default to end of month
                day = "30" if month_num in ("04", "06", "09", "11") else "31"
                if month_num == "02":
                    day = "28"
            return f"{year}-{month_num}-{day}"

    # Just return year-12-31 as default (fiscal year end)
    return f"{year}-12-31"


def _build_meta_dataframe(title: str | None, periods: list[str], multiplier: int) -> pd.DataFrame:
    """Build metadata DataFrame."""
    if multiplier == 1_000_000_000:
        scale = "billions"
    elif multiplier == 1_000_000:
        scale = "millions"
    elif multiplier == 1_000:
        scale = "thousands"
    else:
        scale = "units"

    return pd.DataFrame(
        {
            "title": [title or "Financial Statement"],
            "periods": [periods],
            "num_periods": [len(periods)],
            "is_xbrl": [False],
            "source": ["HTML Table"],
            "scale": [scale],
            "multiplier": [multiplier],
        }
    )


def find_all_statements(
    html_content: str,
) -> dict[str, tuple[pd.DataFrame, pd.DataFrame]]:
    """
    Find and parse all financial statements in a filing.

    Returns a dict mapping statement type to (data_df, meta_df).
    """
    results = {}

    for stmt_type in ["income", "balance", "cash", "equity"]:
        data_df, meta_df = parse_non_xbrl_statement(html_content, stmt_type)
        if not data_df.empty:
            results[stmt_type] = (data_df, meta_df)

    return results


def extract_toc(html_content: str) -> dict[str, str]:
    """
    Extract table of contents from a non-XBRL filing.

    Returns a dict mapping item numbers (e.g., '1', '1A', '7') to titles.
    Also captures PART I/II and sub-items under Item 1 for financial statements.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    toc_dict: dict = {}

    # Valid SEC filing item numbers: 1-15 with optional A/B/C suffix
    # Excludes regulatory references like Item 405, Item 601
    valid_item_pattern = re.compile(r"^ITEM\s*(1[0-5]?|[2-9])(A|B|C)?[.:]?$", re.IGNORECASE)

    # Method 1: Group links by href - TOC has "ITEM 1." in one cell and title in another
    href_to_texts: dict = {}
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        if not href or not str(href).startswith("#"):
            continue
        link_text = link.get_text(strip=True)
        if not link_text:
            continue
        if href not in href_to_texts:
            href_to_texts[href] = []
        href_to_texts[href].append(link_text)

    # Find pairs: one text matches "ITEM X." pattern, another is the title
    for href, texts in href_to_texts.items():
        item_num = None
        title = None
        for text in texts:
            # Check if it's a valid item number pattern
            item_match = valid_item_pattern.match(text.strip())
            if item_match:
                num = item_match.group(1)
                suffix = item_match.group(2) or ""
                item_num = f"{num}{suffix}".upper()
            elif text and not re.match(r"^\d+$", text):  # Not just a page number
                # Skip short words like "of" that are fragments
                if title is None and len(text) > 5:
                    title = text

        if item_num and title and item_num not in toc_dict:
            toc_dict[item_num] = title

    # Method 2: Parse table-based TOC (common in pre-2000 filings)
    if not toc_dict:
        toc_dict = _extract_toc_from_table(soup)

    # Method 3: Fall back to text pattern matching
    if not toc_dict:
        text = soup.get_text(separator="\n", strip=True)
        # Look for patterns like "ITEM 1. BUSINESS" or "ITEM 1A. RISK FACTORS"
        # Only match valid item numbers (1-15 with optional A/B/C suffix)
        matches = re.findall(
            r"ITEM\s+(1[0-5]?|[2-9])(A|B|C)?[\.\s]+([A-Z][A-Z\s,\-\']+?)(?:\n|$)",
            text,
            re.IGNORECASE,
        )
        for num, suffix, title in matches:
            item_num = f"{num}{suffix or ''}".upper()
            if item_num not in toc_dict:
                toc_dict[item_num] = title.strip()

    return toc_dict


def _extract_toc_from_table(soup: BeautifulSoup) -> dict:
    """
    Extract TOC from table-based layout (common in older SEC filings).

    Looks for tables containing PART I/II and Item patterns with page numbers.
    """
    toc_dict: dict = {}
    current_part = "I"  # Default to Part I

    # Find tables that contain TOC markers
    for table in soup.find_all("table"):
        table_text = table.get_text()
        if "PART I" not in table_text.upper() and "Item" not in table_text:
            continue

        # Process each row
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            cell_texts = [c.get_text(strip=True) for c in cells]
            # Filter out empty cells and deduplicate
            cell_texts = list(dict.fromkeys([t for t in cell_texts if t]))

            if not cell_texts:
                continue

            # Only process "clean" rows - those with 2-3 short cells
            # Rows with many cells are complex nested structures
            short_cells = [t for t in cell_texts if len(t) <= 100]
            if len(cell_texts) > 5:
                # This is a complex row with many cells - only use the last few clean ones
                # The pattern in these tables is that the last 2-3 cells are the "clean" values
                short_cells = [t for t in cell_texts if len(t) <= 100][-5:]
                cell_texts = short_cells

            # Check for PART pattern in this clean set
            for text in cell_texts:
                # Skip cells that are too long to be just "PART X:"
                if len(text) > 20:
                    continue
                part_match = re.match(
                    r"PART\s+(I{1,2}|[12])\s*:?$",
                    text.replace("\xa0", " "),
                    re.IGNORECASE,
                )
                if part_match:
                    part_num = part_match.group(1)
                    # Normalize to Roman numerals
                    if part_num == "1":
                        part_num = "I"
                    elif part_num == "2":
                        part_num = "II"
                    # Only update current_part if this looks like a primary row
                    # (not a row that just happens to have PART II in nested cells)
                    has_title_cell = any(len(t) < 50 and not t.isdigit() and t != text for t in cell_texts)
                    if has_title_cell and len(short_cells) <= 5:
                        current_part = part_num
                        # Find the part title in remaining cells
                        for other_text in cell_texts:
                            if other_text != text and not other_text.isdigit() and len(other_text) < 50:
                                clean_title = other_text.replace("\n", " ").strip()
                                clean_title = re.sub(r"\s+", " ", clean_title)
                                if clean_title and len(clean_title) > 3:
                                    toc_dict[f"PART_{part_num}"] = clean_title
                                    break
                    break

            # Look for clean rows with [Item X:, Title, Page] pattern
            # These appear as short rows at the end of complex nested cells
            if len(cell_texts) >= 2 and len(cell_texts) <= 5:
                # Check for Item pattern
                for i, text in enumerate(cell_texts):
                    # Skip cells that are too long
                    if len(text) > 15:
                        continue
                    # Match "Item X:" pattern (with non-breaking space)
                    item_match = re.match(
                        r"Item\s*(\d+[A-Za-z]?)\s*:?$",
                        text.replace("\xa0", " "),
                        re.IGNORECASE,
                    )
                    if item_match and i + 1 < len(cell_texts):
                        item_num = item_match.group(1).upper()
                        # Next cell should be the title (not a page number)
                        title = cell_texts[i + 1].replace("\n", " ").replace("\t", " ").strip()
                        # Clean up multi-line titles
                        title = re.sub(r"\s+", " ", title)
                        # Skip if it looks like page number or garbage
                        if title and not title.isdigit() and len(title) > 3:
                            # Truncate at page number if embedded
                            if re.search(r"\d{2}$", title):
                                title = re.sub(r"\d+$", "", title).strip()
                            # Use part prefix for Part II items to disambiguate
                            key = f"II_{item_num}" if current_part == "II" else item_num
                            if key not in toc_dict:
                                toc_dict[key] = title
                        break

    return toc_dict


def _find_notes_in_section(html_content: str) -> list:
    """
    Find notes within the Notes to Financial Statements section.

    Uses the TOC to identify note letters and titles, then finds where
    each note's content actually starts.
    Returns list of tuples: (content_start_pos, note_id, title, content_end_pos)
    """
    matches = []

    # Find the Notes to Financial Statements section
    notes_match = re.search(
        r"Notes?\s+to\s+(?:Consolidated\s+)?Financial\s+Statements?",
        html_content,
        re.IGNORECASE,
    )
    if not notes_match:
        return matches

    notes_start = notes_match.start()

    # First, find note entries in the TOC (wide cells with letter + title)
    # TOC pattern: cell with letter, cell with title, cell with page number
    toc_pattern = re.compile(
        r"<td[^>]*>\s*<p[^>]*>\s*(?:<font[^>]*>)?\s*([A-Z])\s*(?:</font>)?\s*</p>\s*</td>\s*"
        r'<td[^>]*width="8[0-9]%"[^>]*>.*?<font[^>]*>([^<]{5,80})</font>',
        re.IGNORECASE | re.DOTALL,
    )

    # Build list of (letter, title) from TOC
    toc_notes = []
    seen_letters = set()
    for m in toc_pattern.finditer(html_content[notes_start : notes_start + 50000]):
        letter = m.group(1).upper()
        title = m.group(2).strip()
        title = re.sub(r"\s+", " ", title)
        title = _clean_html_entities(title)
        if letter not in seen_letters and len(title) >= 5:
            seen_letters.add(letter)
            toc_notes.append((letter, title))

    if not toc_notes:
        return matches

    # Now find where each note's content actually starts
    # Look for bold headers like "A. Significant Accounting Policies"
    for letter, title in toc_notes:
        # Search for the actual note header in content (after TOC)
        # Pattern: bold letter followed by period and title
        content_pattern = re.compile(
            rf"<b[^>]*>\s*(?:<font[^>]*>)?\s*{letter}\.\s+[^<]*(?:</font>)?\s*</b>",
            re.IGNORECASE,
        )
        # Search after position 100000 (skip TOC area)
        search_start = notes_start + 100000
        m = content_pattern.search(html_content[search_start:])
        if m:
            content_start = search_start + m.end()
            matches.append((content_start, letter, title, None))  # end_pos filled later

    # Fill in end positions (each note ends where next begins)
    for i in range(len(matches)):
        if i + 1 < len(matches):
            matches[i] = (
                matches[i][0],
                matches[i][1],
                matches[i][2],
                matches[i + 1][0],
            )
        else:
            matches[i] = (matches[i][0], matches[i][1], matches[i][2], None)

    return matches


def extract_text_blocks(html_content: str) -> dict[str, dict]:
    """
    Extract text blocks (notes/disclosures) from a non-XBRL filing.

    These are the Notes to Financial Statements - the footnotes that
    explain the numbers in the financial statements.

    Returns a dict mapping note identifiers to their text content,
    with structure matching XBRL text_blocks: {key: {"name": ..., "text": ...}}
    """
    text_blocks: dict = {}

    # Strategy 1: Find "Note X. Title" pattern (common in many filings)
    note_pattern = re.compile(r"<[Bb]>Note\s*(\d+)[.\s](?:&nbsp;)?([^<]+)</[Bb]>", re.IGNORECASE)

    matches = list(note_pattern.finditer(html_content))

    # Strategy 2: Find Notes section and extract note headers from wide cells
    if not matches:
        matches = _find_notes_in_section(html_content)

    if not matches:
        return text_blocks

    # Extract each note section
    for i, match in enumerate(matches):
        # Handle both regex match objects and tuples
        if hasattr(match, "group"):
            note_id = match.group(1)
            title = match.group(2).strip()
            title = title.replace("&nbsp;", " ").replace("&#151;", "—")
            title = re.sub(r"&\w+;", "", title)
            start_pos: int = match.end()
            next_start = matches[i + 1].start() if i + 1 < len(matches) else None
        else:
            # Tuple: (content_start_pos, note_id, title, content_end_pos)
            _start_pos, note_id, title, next_start = match
            start_pos = int(_start_pos)  # Ensure int type

        # Get HTML from end of this match to start of next note
        if next_start:
            end_pos = next_start
        else:
            # Last note - find end at Review Report, Item 2, or PART II
            # Various patterns for Item 2 header
            end_patterns = [
                r"<[Bb]>Review Report",
                r"<[Bb]>Item\s*(?:&nbsp;)?2[:\s.]",
                r"<[Bb]>PART\s+II",
            ]
            earliest_end = len(html_content)
            for pattern in end_patterns:
                end_match = re.search(pattern, html_content[start_pos:], re.IGNORECASE)
                if end_match:
                    pos = start_pos + end_match.start()
                    earliest_end = min(earliest_end, pos)
            end_pos = earliest_end

        # Extract the HTML section
        section_html = html_content[start_pos:end_pos]

        # Parse this section - process elements in order
        soup = BeautifulSoup(section_html, "html.parser")

        # Process content in document order
        content_parts: list[str] = []
        tables_data: list[dict] = []
        processed_tables: set[int] = set()
        processed_texts: set[str] = set()

        # Process elements in document order
        for elem in soup.find_all(["p", "table"]):
            if elem.name == "table":
                if elem.find_parent("table"):
                    continue
                # Process table
                table_id = id(elem)
                if table_id in processed_tables:
                    continue
                processed_tables.add(table_id)

                # Check for bullet list first
                if _is_bullet_table(elem):
                    result = _extract_bullet_list(elem)
                else:
                    # Parse table using financial statement logic
                    headers, data_rows = _parse_html_table_for_notes(elem)
                    if data_rows:
                        tables_data.append({"headers": headers, "data": data_rows})
                        result = _table_to_markdown_notes(headers, data_rows)
                    else:
                        result = None

                # Add content avoiding duplicates
                if result:
                    text_key = result[:200] if len(result) > 200 else result
                    if text_key not in processed_texts:
                        content_parts.append(result)
                        processed_texts.add(text_key)

            elif elem.name == "p":
                if elem.find_parent("table"):
                    continue
                # Get direct text only (handles nested P in malformed HTML)
                text = _get_direct_text(elem)
                text = _clean_paragraph_text(text)
                # Add content avoiding duplicates
                if text:
                    text_key = text[:200] if len(text) > 200 else text
                    if text_key not in processed_texts:
                        content_parts.append(text)
                        processed_texts.add(text_key)

        # Join with proper spacing
        full_text = "\n\n".join(content_parts)

        key = f"note_{note_id}"
        text_blocks[key] = {
            "name": title,
            "disclosure": [key],
            "text": full_text,
        }
        if tables_data:
            text_blocks[key]["tables"] = tables_data

    return text_blocks


def extract_items(html_content: str, filing_type: str | None = None) -> dict[str, dict]:
    """
    Extract SEC filing items (MD&A, Risk Factors, etc.) from HTML content.

    Works for 10-K, 10-Q, and 8-K filings. Handles different company HTML formats.

    Args:
        html_content: HTML content of the filing
        filing_type: Optional filing type (10-K, 10-Q, 8-K) to help determine patterns

    Returns a dict mapping item identifiers to their content:
    {
        "item_1": {"name": "Financial Statements", "text": "...", "part": "I"},
        "item_2": {"name": "Management's Discussion and Analysis", "text": "...", "part": "I"},
        ...
    }

    For 8-K filings:
    {
        "item_1.01": {"name": "Entry into a Material Definitive Agreement", "text": "...", "section": "1"},
        "item_8.01": {"name": "Other Events", "text": "...", "section": "8"},
        ...
    }
    """
    items: dict = {}

    # Detect if this is an 8-K based on content or filing_type
    is_8k = filing_type and "8-K" in filing_type.upper()
    if not is_8k:
        # Check content for 8-K indicators (Item X.XX patterns)
        is_8k = bool(re.search(r"Item[\s\u2009]+\d+\.\d+", html_content, re.IGNORECASE))

    if is_8k:
        return _extract_8k_items(html_content)

    # Find all Item headers in the document
    # Pattern matches: <B>Item 2:</B>, <B>Item&nbsp;2:&nbsp;</B>, etc.
    # Use .+? to allow <BR> tags inside the title (some filings have <BR> before </B>)
    item_pattern_bold = re.compile(
        r"<[Bb]>Item\s*(?:&nbsp;)?(\d+[A-Za-z]?)\s*[:\s.]\s*(?:&nbsp;)?(.+?)</[Bb]>",
        re.IGNORECASE | re.DOTALL,
    )

    # Also match multi-cell format: <B>Item&nbsp;2:&nbsp;</B></TD><TD><B>Title</B>
    item_pattern_split = re.compile(
        r"<[Bb]>Item\s*(?:&nbsp;)?(\d+[A-Za-z]?)\s*[:\s.]\s*(?:&nbsp;)?</[Bb]>\s*</TD>\s*<TD[^>]*>\s*<[Bb]>([^<]+)</[Bb]>",
        re.IGNORECASE,
    )

    # Non-bold pattern: ITEM 7.&nbsp;&nbsp;&nbsp;&nbsp;TITLE (Microsoft style)
    # Some have title on same line, others have title after <A NAME=...> on next line
    item_pattern_nonbold = re.compile(
        r">ITEM\s*(\d+[A-Za-z]?)\s*[.\s](?:&nbsp;)*\s*(?:<[^>]*>)*\s*([A-Z][^<]{5,100}?)\s*</FONT>",
        re.IGNORECASE | re.DOTALL,
    )

    def clean_item_title(raw_title: str) -> str:
        """Clean up item title by removing BR tags, trailing colons, and extra whitespace."""
        title = re.sub(r"<[Bb][Rr]\s*/?>", " ", raw_title)  # Remove <BR> tags
        title = re.sub(r"<[^>]+>", "", title)  # Remove any HTML tags
        title = _clean_html_entities(title)
        title = re.sub(r":?\s*$", "", title)  # Remove trailing colon
        title = re.sub(r"\s+", " ", title).strip()  # Collapse whitespace
        return title

    # Find all matches
    matches = []

    # Try split pattern first (more specific)
    for m in item_pattern_split.finditer(html_content):
        item_num = m.group(1).upper()
        title = clean_item_title(m.group(2))
        matches.append((m.start(), item_num, title))

    # Then try bold pattern
    for m in item_pattern_bold.finditer(html_content):
        item_num = m.group(1).upper()
        title = clean_item_title(m.group(2))
        # Skip if we already got this position from split pattern
        if not any(abs(pos - m.start()) < 100 for pos, _, _ in matches):
            matches.append((m.start(), item_num, title))

    # Try non-bold pattern (Microsoft style)
    for m in item_pattern_nonbold.finditer(html_content):
        item_num = m.group(1).upper()
        title = clean_item_title(m.group(2))
        # Skip TOC entries (they're usually short or in TD cells)
        if len(title) < 10:
            continue
        # Skip if we already got this item number nearby
        if not any(abs(pos - m.start()) < 500 and num == item_num for pos, num, _ in matches):
            matches.append((m.start(), item_num, title))

    # Sort by position
    matches.sort(key=lambda x: x[0])

    if not matches:
        return items

    # Track which Part we're in (I or II) based on item sequence
    # Part I typically has Items 1-4, Part II has Items 1-6
    # Use position relative to other items to determine part
    seen_items = set()

    # Extract each item section
    for i, (pos, item_num, title) in enumerate(matches):
        # Determine part - if we see item 1 again after other items, we're in Part II
        if item_num == "1" and len(seen_items) > 0:
            part = "II"
        elif any(n in seen_items for n in ["1", "2", "3", "4"]) and item_num in [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
        ]:
            # If we've seen items from Part I and now see them again
            part = "II" if item_num in seen_items else "I"
        else:
            part = "I"

        seen_items.add(item_num)

        # Get end position (start of next item or end of document)
        end_pos = matches[i + 1][0] if i + 1 < len(matches) else len(html_content)

        # Extract the HTML section
        section_html = html_content[pos:end_pos]

        # Parse this section
        soup = BeautifulSoup(section_html, "html.parser")

        # Process content in document order
        content_parts: list[tuple[str, str]] = []
        processed_texts: set[str] = set()

        # Process elements in document order
        for elem in soup.find_all(["p", "table"]):
            if elem.name == "table":
                # Skip nested tables (already processed by parent)
                if elem.find_parent("table"):
                    continue

                # Process table - check for bullet list first
                if _is_bullet_table(elem):
                    result = _extract_bullet_list(elem)
                elif not _is_financial_table(elem):
                    # Not a financial table - extract as simple text
                    text = elem.get_text(separator=" ", strip=True)
                    text = _clean_html_entities(text)
                    text = re.sub(r"\s+", " ", text).strip()
                    result = text if len(text) > 20 else None
                else:
                    # Parse as financial table
                    headers, data_rows = _parse_html_table_for_notes(elem)
                    result = _table_to_markdown_notes(headers, data_rows) if data_rows else None

                # Add content avoiding duplicates
                if result:
                    text_key = result[:200] if len(result) > 200 else result
                    if text_key not in processed_texts:
                        content_parts.append(("table", result))
                        processed_texts.add(text_key)

            elif elem.name == "p":
                # Skip if inside a table
                if elem.find_parent("table"):
                    continue

                # Check if this is a section header
                if _is_section_header(elem):
                    header_text = _get_direct_text(elem)
                    header_text = _clean_html_entities(header_text)
                    header_text = re.sub(r"\s+", " ", header_text).strip()
                    text_key = header_text[:200] if len(header_text) > 200 else header_text
                    if text_key not in processed_texts:
                        content_parts.append(("header", f"## {header_text}"))
                        processed_texts.add(text_key)
                    continue

                # Get only direct text (handles nested P tags in malformed HTML)
                text = _get_direct_text(elem)
                text = _clean_paragraph_text(text)
                # Add content avoiding duplicates
                if text:
                    text_key = text[:200] if len(text) > 200 else text
                    if text_key not in processed_texts:
                        content_parts.append(("text", text))
                        processed_texts.add(text_key)

        # Join with proper spacing
        full_text = "\n\n".join(item[1] for item in content_parts)

        # Create key
        key = f"item_II_{item_num}" if part == "II" else f"item_{item_num}"

        items[key] = {
            "name": title or _get_item_default_name(item_num, part),
            "part": part,
            "item_num": item_num,
            "text": full_text,
        }

    return items


def _clean_html_entities(text: str) -> str:
    """Clean HTML entities and normalize special characters."""
    # HTML entities
    text = text.replace("&nbsp;", " ")
    text = text.replace("&#146;", "'")
    text = text.replace("&#147;", '"')
    text = text.replace("&#148;", '"')
    text = text.replace("&#149;", "•")  # bullet
    text = text.replace("&#150;", "-")  # en-dash
    text = text.replace("&#151;", "—")  # em-dash
    text = text.replace("&#160;", " ")  # non-breaking space
    text = text.replace("&amp;", "&")
    text = text.replace("&mdash;", "—")
    text = text.replace("&ndash;", "-")
    text = text.replace("&bull;", "•")
    text = text.replace("&rsquo;", "'")
    text = text.replace("&lsquo;", "'")
    text = text.replace("&rdquo;", '"')
    text = text.replace("&ldquo;", '"')

    # Unicode curly/smart quotes -> straight quotes
    text = text.replace('"', '"')  # left double quote
    text = text.replace('"', '"')  # right double quote
    text = text.replace(
        """, "'")  # left single quote
    text = text.replace(""",
        "'",
    )  # right single quote

    # Unicode dashes -> ASCII
    text = text.replace("–", "-")  # en-dash
    text = text.replace("—", "-")  # em-dash (to hyphen for consistency)

    # Clean remaining HTML entities
    text = re.sub(r"&\w+;", "", text)
    text = re.sub(r"&#\d+;", "", text)
    return text.strip()


def _extract_8k_items(html_content: str) -> dict[str, dict]:
    """
    Extract items from 8-K filings which use Item X.XX format.

    8-K items use a different numbering scheme:
    - Section 1: Registrant's Business and Operations
      - Item 1.01: Entry into a Material Definitive Agreement
      - Item 1.02: Termination of a Material Definitive Agreement
      - Item 1.03: Bankruptcy or Receivership
      - Item 1.04: Mine Safety - Reporting of Shutdowns and Patterns of Violations
    - Section 2: Financial Information
      - Item 2.01: Completion of Acquisition or Disposition of Assets
      - Item 2.02: Results of Operations and Financial Condition
      - Item 2.03: Creation of a Direct Financial Obligation
      - Item 2.04: Triggering Events That Accelerate or Increase a Direct Financial Obligation
      - Item 2.05: Costs Associated with Exit or Disposal Activities
      - Item 2.06: Material Impairments
    - Section 3: Securities and Trading Markets
    - Section 4: Matters Related to Accountants and Financial Statements
    - Section 5: Corporate Governance and Management
    - Section 6: [Reserved]
    - Section 7: Regulation FD
    - Section 8: Other Events
      - Item 8.01: Other Events
    - Section 9: Financial Statements and Exhibits
      - Item 9.01: Financial Statements and Exhibits
    """
    items: dict = {}

    # 8-K item pattern: Item X.XX - handles various spacing including thin space (U+2009)
    # Matches: Item 1.01, Item 8.01, Item 9.01, etc.
    item_pattern = re.compile(r"Item[\s\u2009]+(\d+\.\d+)[\s\u2009]*([^\n<]{0,100})", re.IGNORECASE)

    # Find all matches
    matches = []
    for m in item_pattern.finditer(html_content):
        item_num = m.group(1)
        title = m.group(2).strip()
        # Clean title
        title = re.sub(r"<[^>]+>", "", title)  # Remove HTML tags
        title = _clean_html_entities(title)
        title = re.sub(r"\s+", " ", title).strip()
        # Skip very short titles (likely TOC entries)
        if len(title) < 5:
            title = _get_8k_item_name(item_num)
        matches.append((m.start(), item_num, title))

    # Sort by position
    matches.sort(key=lambda x: x[0])

    if not matches:
        return items

    # Remove duplicate matches (keep first occurrence in body, skip TOC)
    # TOC entries are typically followed by page numbers or in tables
    seen_items = {}
    filtered_matches = []

    for pos, item_num, title in matches:
        if item_num in seen_items:
            # Keep the later occurrence (more likely to be the actual section, not TOC)
            # But only if there's significant content between them
            prev_pos = seen_items[item_num][0]
            if pos - prev_pos > 1000:  # Significant distance apart
                # Replace with the later occurrence
                filtered_matches = [m for m in filtered_matches if m[1] != item_num]
                filtered_matches.append((pos, item_num, title))
                seen_items[item_num] = (pos, title)
        else:
            filtered_matches.append((pos, item_num, title))
            seen_items[item_num] = (pos, title)

    matches = sorted(filtered_matches, key=lambda x: x[0])

    # Extract each item section
    for i, (pos, item_num, title) in enumerate(matches):
        # Get end position (start of next item or end of document)
        end_pos = matches[i + 1][0] if i + 1 < len(matches) else len(html_content)

        # Extract the HTML section
        section_html = html_content[pos:end_pos]

        # Parse this section
        soup = BeautifulSoup(section_html, "html.parser")

        # Process content in document order
        content_parts: list[tuple[str, str]] = []
        processed_texts: set[str] = set()

        # Process elements in document order
        for elem in soup.find_all(["p", "table", "div", "span"]):
            if elem.name == "table":
                # Skip nested tables (already processed by parent)
                if elem.find_parent("table"):
                    continue

                # Process table - check for bullet list first
                if _is_bullet_table(elem):
                    result = _extract_bullet_list(elem)
                elif not _is_financial_table(elem):
                    # Not a financial table - extract as simple text
                    text = elem.get_text(separator=" ", strip=True)
                    text = _clean_html_entities(text)
                    text = re.sub(r"\s+", " ", text).strip()
                    result = text if len(text) > 20 else None
                else:
                    # Parse as financial table
                    headers, data_rows = _parse_html_table_for_notes(elem)
                    result = _table_to_markdown_notes(headers, data_rows) if data_rows else None

                # Add content avoiding duplicates
                if result:
                    text_key = result[:200] if len(result) > 200 else result
                    if text_key not in processed_texts:
                        content_parts.append(("table", result))
                        processed_texts.add(text_key)

            elif elem.name in ("p", "div"):
                # Skip if inside a table
                if elem.find_parent("table"):
                    continue

                # Get text
                text = elem.get_text(separator=" ", strip=True)
                text = _clean_html_entities(text)
                text = re.sub(r"\s+", " ", text).strip()

                # Add content avoiding duplicates
                if text and len(text) > 10:
                    text_key = text[:200] if len(text) > 200 else text
                    if text_key not in processed_texts:
                        content_parts.append(("text", text))
                        processed_texts.add(text_key)

        # Join with proper spacing
        full_text = "\n\n".join(item[1] for item in content_parts)

        # Determine section number from item number
        section = item_num.split(".")[0]

        # Create key
        key = f"item_{item_num}"

        items[key] = {
            "name": title or _get_8k_item_name(item_num),
            "section": section,
            "item_num": item_num,
            "text": full_text,
        }

    return items


def _get_8k_item_name(item_num: str) -> str:
    """Get default name for an 8-K filing item."""
    names = {
        "1.01": "Entry into a Material Definitive Agreement",
        "1.02": "Termination of a Material Definitive Agreement",
        "1.03": "Bankruptcy or Receivership",
        "1.04": "Mine Safety - Reporting of Shutdowns and Patterns of Violations",
        "2.01": "Completion of Acquisition or Disposition of Assets",
        "2.02": "Results of Operations and Financial Condition",
        "2.03": "Creation of a Direct Financial Obligation",
        "2.04": "Triggering Events That Accelerate or Increase a Direct Financial Obligation",
        "2.05": "Costs Associated with Exit or Disposal Activities",
        "2.06": "Material Impairments",
        "3.01": "Notice of Delisting or Failure to Satisfy a Continued Listing Rule",
        "3.02": "Unregistered Sales of Equity Securities",
        "3.03": "Material Modification to Rights of Security Holders",
        "4.01": "Changes in Registrant's Certifying Accountant",
        "4.02": "Non-Reliance on Previously Issued Financial Statements",
        "5.01": "Changes in Control of Registrant",
        "5.02": "Departure of Directors or Certain Officers",
        "5.03": "Amendments to Articles of Incorporation or Bylaws",
        "5.04": "Temporary Suspension of Trading Under Registrant's Employee Benefit Plans",
        "5.05": "Amendment to Registrant's Code of Ethics",
        "5.06": "Change in Shell Company Status",
        "5.07": "Submission of Matters to a Vote of Security Holders",
        "5.08": "Shareholder Director Nominations",
        "6.01": "[Reserved]",
        "6.02": "[Reserved]",
        "6.03": "[Reserved]",
        "6.04": "[Reserved]",
        "6.05": "[Reserved]",
        "7.01": "Regulation FD Disclosure",
        "8.01": "Other Events",
        "9.01": "Financial Statements and Exhibits",
    }
    return names.get(item_num, f"Item {item_num}")


def _get_item_default_name(item_num: str, part: str) -> str:
    """Get default name for a filing item."""
    if part == "I":
        # 10-Q Part I items
        names = {
            "1": "Financial Statements",
            "2": "Management's Discussion and Analysis",
            "3": "Quantitative and Qualitative Disclosures About Market Risk",
            "4": "Controls and Procedures",
        }
    else:
        # Part II items (common to 10-K and 10-Q)
        names = {
            "1": "Legal Proceedings",
            "1A": "Risk Factors",
            "2": "Changes in Securities",
            "3": "Defaults Upon Senior Securities",
            "4": "Mine Safety Disclosures",
            "5": "Other Information",
            "6": "Exhibits",
        }
    return names.get(item_num, f"Item {item_num}")


def _extract_simple_table(table_elem) -> str | None:
    """
    Extract a simpler text representation of a table when structured parsing fails.
    Used for tables that don't follow financial statement format.
    """
    rows = table_elem.find_all("tr")
    if not rows:
        return None

    result_rows = []
    for tr in rows:
        cells = tr.find_all(["td", "th"], recursive=False)
        if not cells:
            continue

        # Get text from each cell
        cell_texts = []
        for c in cells:
            if c.find("table"):
                continue  # Skip nested tables
            text = c.get_text(strip=True)
            text = re.sub(r"\s+", " ", text)
            if text:
                cell_texts.append(text)

        if cell_texts:
            result_rows.append(" | ".join(cell_texts))

    if len(result_rows) > 1:
        return "\n".join(result_rows)
    return None


def _parse_html_table_for_notes(table_elem) -> tuple[list[str], list[list[str]]]:
    """
    Parse an HTML table for notes.
    Returns (headers, data_rows) where each row is a list of cell values.

    Uses the same extraction logic as financial statement parsing.
    """
    # Use _extract_table_data which already handles complex layouts
    result = _extract_table_data(table_elem)
    if result:
        line_items, periods, multiplier, _title = result
        headers = [""] + periods  # Empty for label column
        data_rows = []
        for item in line_items:
            label = item.get("label", "")
            values = item.get("values", [])
            # Format values
            row = [label]
            for v in values:
                if v is None:
                    row.append("")
                elif item.get("skip_multiplier"):
                    row.append(str(v))
                else:
                    row.append(str(v * multiplier) if multiplier != 1 else str(v))
            data_rows.append(row)
        return headers, data_rows

    # Fallback: simple cell extraction
    all_trs = table_elem.find_all("tr")
    if len(all_trs) < 2:
        return [], []

    headers = []
    data_rows = []
    for _i, tr in enumerate(all_trs):
        cells = tr.find_all(["td", "th"], recursive=False)
        row_data = [_clean_cell_text(c) for c in cells]
        # Skip empty rows
        if not any(row_data):
            continue
        if not headers:
            headers = row_data
        else:
            data_rows.append(row_data)

    return headers, data_rows


def _table_to_markdown_notes(headers: list[str], data_rows: list[list[str]]) -> str:
    """Convert parsed table data to markdown."""
    if not headers and not data_rows:
        return ""

    lines = []

    # Determine column count
    num_cols = len(headers) if headers else (len(data_rows[0]) if data_rows else 0)
    if num_cols == 0:
        return ""

    # Header row
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * num_cols) + " |")

    # Data rows
    for row in data_rows:
        # Ensure row has right number of cells
        row_data = list(row)
        while len(row_data) < num_cols:
            row_data.append("")
        lines.append("| " + " | ".join(row_data[:num_cols]) + " |")

    return "\n".join(lines)


def get_statement_names() -> dict[str, str]:
    """Get mapping of statement type codes to display names."""
    return {
        "income": "Consolidated Statements of Operations",
        "balance": "Consolidated Balance Sheet",
        "cash": "Consolidated Statements of Cash Flows",
        "equity": "Consolidated Statements of Stockholders' Equity",
    }
