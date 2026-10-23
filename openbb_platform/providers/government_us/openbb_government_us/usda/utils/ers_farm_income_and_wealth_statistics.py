"""USDA ERS Farm Income and Wealth Statistics catalog, fetch, and CSV parser."""

import csv
import io
import re
import zipfile
from io import StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = (
    "data-products/farm-income-and-wealth-statistics/"
    "data-files-us-and-state-level-farm-income-and-wealth-statistics"
)
RELEASE_ZIP = "/media/20808/february-5-2026-release.zip"

DOWNLOAD_HEADING = "Download All Data in CSV File Format"
RELEASE_ZIP_PATTERN = re.compile(r'href="([^"?]+\.zip)"')
NULL_UNIT_TOKENS = ("�", "\xa0")

TABLE_PREFIXES: dict[str, tuple[str, ...]] = {
    "income_statement": ("FI",),
    "production_expenses": ("EX",),
    "cash_receipts": ("CR",),
    "government_payments": ("GP",),
    "farm_related_income": ("FR",),
    "home_consumption": ("HC",),
    "inventory_change": ("IY",),
    "balance_sheet": ("FA", "FD", "FE"),
    "financial_ratios": ("RT",),
    "farm_business_income": ("FB",),
}

TABLE_LABELS: dict[str, str] = {
    "income_statement": "Income statement (value added)",
    "production_expenses": "Production expenses",
    "cash_receipts": "Cash receipts",
    "government_payments": "Government payments",
    "farm_related_income": "Farm-related income",
    "home_consumption": "Home consumption",
    "inventory_change": "Inventory change",
    "balance_sheet": "Balance sheet (U.S.)",
    "financial_ratios": "Financial ratios (U.S.)",
    "farm_business_income": "Farm business income (U.S.)",
}

US_ONLY_TABLES: frozenset[str] = frozenset(
    {"balance_sheet", "financial_ratios", "farm_business_income"}
)

STATE_LABELS: dict[str, str] = {
    "US": "United States",
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
}

STATE_CODES: tuple[str, ...] = tuple(STATE_LABELS)


def allowed_states(table: str) -> tuple[str, ...]:
    """Return the state codes a table is published for.

    Parameters
    ----------
    table : str
        Table key from TABLE_PREFIXES.

    Returns
    -------
    tuple[str, ...]
        ('US',) for the U.S.-only tables, otherwise every state code led by
        the national aggregate.
    """
    return ("US",) if table in US_ONLY_TABLES else STATE_CODES


def state_options(table: str) -> list[dict]:
    """Build the labeled state options a table is published for.

    Parameters
    ----------
    table : str
        Table key from TABLE_PREFIXES.

    Returns
    -------
    list[dict]
        Label/value option dictionaries for the widget's state selector.
    """
    return [
        {"label": STATE_LABELS[code], "value": code} for code in allowed_states(table)
    ]


def extract_release_zip(html: str) -> str | None:
    """Extract the latest release-zip media path from the data-files subpage.

    Parameters
    ----------
    html : str
        Decoded HTML of the U.S. and State-level data-files subpage.

    Returns
    -------
    str | None
        The first ``.zip`` link under the 'Download All Data in CSV File
        Format' heading, which is the most recent release, or None when the
        heading or a link is absent.
    """
    start = html.find(DOWNLOAD_HEADING)
    if start == -1:
        return None
    tail = html[start:]
    end = tail.find("</ul>")
    segment = tail[:end] if end != -1 else tail
    match = RELEASE_ZIP_PATTERN.search(segment)
    if not match:
        return None
    path = match.group(1)
    return path if path.startswith("/") else "/" + path


def clean_unit(unit: str) -> str:
    """Strip mis-decoded no-break-space bytes from a published unit label.

    Parameters
    ----------
    unit : str
        Raw unit_desc value, e.g. '$1,000' trailed by replacement bytes.

    Returns
    -------
    str
        Cleaned unit, e.g. '$1,000', '$1,000 per farm', 'Ratio', 'Percent',
        or '1,000 acres'.
    """
    cleaned = unit
    for token in NULL_UNIT_TOKENS:
        cleaned = cleaned.replace(token, "")
    return cleaned.strip()


def parse_amount(value: str | None) -> float | None:
    """Parse a raw Amount string to a float, keeping full precision.

    Parameters
    ----------
    value : str | None
        Raw Amount cell.

    Returns
    -------
    float | None
        The numeric value, or None when the cell is blank or non-numeric.
    """
    text = (value or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_rows(text: str, prefixes: tuple[str, ...], state: str) -> list[dict]:
    """Parse the tidy CSV into records for one table's prefixes and one state.

    Parameters
    ----------
    text : str
        Decoded CSV text of the release file.
    prefixes : tuple[str, ...]
        The artificialKey two-character prefixes that make up the table.
    state : str
        Two-letter state code, or 'US', to keep.

    Returns
    -------
    list[dict]
        Records with prefix, order, year, state, line_item, part_1, part_2,
        unit, and amount keys, in source file order.
    """
    wanted = set(prefixes)
    records: list[dict] = []
    order = 0
    for row in csv.DictReader(StringIO(text)):
        prefix = (row.get("artificialKey") or "")[:2]
        if prefix not in wanted:
            continue
        row_state = (row.get("State") or "").strip().upper()
        if row_state != state:
            continue
        records.append(
            {
                "prefix": prefix,
                "order": order,
                "year": int((row.get("Year") or "").strip()),
                "state": row_state,
                "line_item": (row.get("VariableDescriptionTotal") or "").strip(),
                "part_1": (row.get("VariableDescriptionPart1") or "").strip() or None,
                "part_2": (row.get("VariableDescriptionPart2") or "").strip() or None,
                "unit": clean_unit(row.get("unit_desc") or ""),
                "amount": parse_amount(row.get("Amount")),
            }
        )
        order += 1
    return records


def extract_csv_text(zip_bytes: bytes) -> str:
    """Extract and decode the single CSV member from the release zip bytes.

    Parameters
    ----------
    zip_bytes : bytes
        Raw bytes of the release zip archive.

    Returns
    -------
    str
        The decoded CSV text of the archive's single .csv member.
    """
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        name = next(n for n in archive.namelist() if n.lower().endswith(".csv"))
        raw = archive.read(name)
    return raw.decode("utf-8-sig", errors="replace")


async def aresolve_release_zip() -> str:
    """Resolve the latest release-zip media path, cached for a day.

    Returns
    -------
    str
        The media path of the most recent release zip, falling back to the
        hardcoded RELEASE_ZIP when the subpage cannot be parsed.
    """
    from openbb_government_us.usda.utils.ers_client import (
        PAGE_TTL,
        _download,
        get_cache,
    )

    key = f"page:{PRODUCT_PAGE}:release-zip"
    with get_cache() as cache:
        cached = cache.get(key)
        if cached is not None:
            return cached
    html = (await _download(f"{BASE_URL}/{PRODUCT_PAGE}")).decode(
        "utf-8", errors="replace"
    )
    path = extract_release_zip(html) or RELEASE_ZIP
    with get_cache() as cache:
        cache.set(key, path, expire=PAGE_TTL)
    return path


async def afetch_dataset() -> str:
    """Download and decode the release CSV through the ERS disk cache.

    Returns
    -------
    str
        The decoded tidy CSV text of the current release.
    """
    from openbb_government_us.usda.utils.ers_client import afetch_ers_file

    zip_path = await aresolve_release_zip()
    content = await afetch_ers_file(zip_path)
    return extract_csv_text(content)


async def afetch_table(table: str, state: str) -> list[dict]:
    """Download the release CSV and parse one table's rows for one state.

    Parameters
    ----------
    table : str
        Table key from TABLE_PREFIXES.
    state : str
        Two-letter state code, or 'US'.

    Returns
    -------
    list[dict]
        Row records from parse_rows for the selected table and state.
    """
    text = await afetch_dataset()
    return parse_rows(text, TABLE_PREFIXES[table], state)
