"""SEC investment adviser records."""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
from re import sub
from typing import Any
from urllib.parse import urljoin, urlparse
from zipfile import ZipFile

import pandas as pd
from defusedxml import ElementTree
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

from openbb_sec.utils.definitions import HEADERS

ADVISER_REPORTS_URL = "https://www.sec.gov/help/foiadocsinvafoiahtm.html"


@dataclass(frozen=True)
class AdviserReportLink:
    """Machine-readable investment adviser report link."""

    url: str
    format: str
    text: str = ""


class SecInvestmentAdvisersQueryParams(QueryParams):
    """SEC investment advisers query.

    Source: https://www.sec.gov/help/foiadocsinvafoiahtm.html
    """

    query: str | None = Field(
        default=None,
        description="Search text matched against adviser names.",
    )
    crd: str | None = Field(
        default=None,
        description="Central Registration Depository (CRD) number.",
    )
    sec_number: str | None = Field(
        default=None,
        description="SEC adviser number, such as 801-12345.",
    )
    limit: int = Field(
        default=100,
        description="Maximum number of adviser records to return.",
        ge=1,
    )
    use_cache: bool = Field(
        default=True,
        description="Whether or not to use cache.",
    )


class SecInvestmentAdvisersData(Data):
    """SEC investment adviser data."""

    crd: str | None = Field(
        default=None,
        description="Central Registration Depository (CRD) number.",
    )
    sec_number: str | None = Field(
        default=None,
        description="SEC adviser number.",
    )
    legal_name: str | None = Field(
        default=None,
        description="Legal name of the investment adviser.",
    )
    primary_business_name: str | None = Field(
        default=None,
        description="Primary business name of the investment adviser.",
    )
    status: str | None = Field(
        default=None,
        description="Registration status when available.",
    )
    regulatory_assets_under_management: int | None = Field(
        default=None,
        description="Regulatory assets under management from Form ADV data.",
    )
    discretionary_aum: int | None = Field(
        default=None,
        description="Discretionary regulatory assets under management.",
    )
    non_discretionary_aum: int | None = Field(
        default=None,
        description="Non-discretionary regulatory assets under management.",
    )
    separately_managed_accounts_aum: int | None = Field(
        default=None,
        description="Regulatory assets under management for separately managed accounts.",
    )
    pooled_investment_vehicles_aum: int | None = Field(
        default=None,
        description="Regulatory assets under management for pooled investment vehicles.",
    )
    employees: int | None = Field(
        default=None,
        description="Total employees when available.",
    )
    phone: str | None = Field(
        default=None,
        description="Main office phone number.",
    )
    city: str | None = Field(
        default=None,
        description="Main office city.",
    )
    state: str | None = Field(
        default=None,
        description="Main office state.",
    )
    country: str | None = Field(
        default=None,
        description="Main office country.",
    )
    website: str | None = Field(
        default=None,
        description="Website URL when available.",
    )


class SecInvestmentAdvisersFetcher(
    Fetcher[
        SecInvestmentAdvisersQueryParams,
        list[SecInvestmentAdvisersData],
    ]
):
    """SEC investment advisers fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecInvestmentAdvisersQueryParams:
        """Transform query parameters."""
        return SecInvestmentAdvisersQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecInvestmentAdvisersQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return raw SEC investment adviser records."""
        records = load_investment_adviser_records(
            use_cache=query.use_cache,
            **kwargs,
        )
        records = _filter_adviser_records(records, query)
        return records[: query.limit]

    @staticmethod
    def transform_data(
        query: SecInvestmentAdvisersQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[SecInvestmentAdvisersData]:
        """Transform raw data to the model format."""
        return [SecInvestmentAdvisersData.model_validate(d) for d in data]


def load_investment_adviser_records(
    *,
    use_cache: bool = True,
    **kwargs: Any,
) -> list[dict[str, Any]]:
    """Load current SEC investment adviser report records."""
    from openbb_sec.utils.ratelimit import sec_make_request

    page_url = kwargs.get("page_url", ADVISER_REPORTS_URL)
    session = kwargs.get("session")
    request_kwargs: dict[str, Any] = {"headers": HEADERS}
    if session is not None:
        request_kwargs["session"] = session
    response = sec_make_request(page_url, **request_kwargs)
    response.raise_for_status()
    links = parse_adviser_report_links(response.text, base_url=page_url)
    records: list[dict[str, Any]] = []
    for link in select_current_adviser_report_links(links):
        report_response = sec_make_request(link.url, **request_kwargs)
        report_response.raise_for_status()
        records.extend(
            normalize_adviser_report_bytes(
                report_response.content,
                file_name=_download_filename(link),
            )
        )
    return records


def parse_adviser_report_links(
    html: str,
    *,
    base_url: str = "https://www.sec.gov",
) -> list[AdviserReportLink]:
    """Parse SEC adviser report page HTML for ZIP, XLSX, and CSV links."""
    parser = _LinkParser()
    parser.feed(html)
    links: list[tuple[int, AdviserReportLink]] = []
    for index, (href, text) in enumerate(parser.links):
        url = urljoin(base_url, href)
        report_format = _link_format(url)
        if report_format is None:
            continue
        links.append(
            (index, AdviserReportLink(url=url, format=report_format, text=text))
        )

    format_rank = {"zip": 0, "xlsx": 1, "csv": 2}
    return [
        link
        for _, link in sorted(
            links,
            key=lambda item: (
                not _looks_current(item[1].url, item[1].text),
                format_rank[item[1].format],
                item[0],
            ),
        )
    ]


def normalize_adviser_report_bytes(
    content: bytes,
    *,
    file_name: str,
) -> list[dict[str, Any]]:
    """Normalize one SEC adviser report file into adviser records."""
    records: list[dict[str, Any]] = []
    for frame, _ in _read_report_frames(content, file_name):
        records.extend(_normalize_frame(frame))
    return records


def select_current_adviser_report_links(
    links: list[AdviserReportLink],
) -> list[AdviserReportLink]:
    """Select the latest registered and exempt adviser report links."""
    selected: dict[str, AdviserReportLink] = {}
    for link in links:
        category = _adviser_report_category(link)
        if category and category not in selected:
            selected[category] = link
        if set(selected) == {"registered", "exempt"}:
            break
    return [selected[key] for key in ("registered", "exempt") if key in selected]


class _LinkParser(HTMLParser):
    """Collect anchor hrefs and visible text from an HTML document."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text_parts: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        """Start collecting text for anchor tags with href attributes."""
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self._href = href
            self._text_parts = []

    def handle_data(self, data: str) -> None:
        """Collect visible anchor text."""
        if self._href is not None:
            self._text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        """Finalize one anchor record."""
        if tag.lower() != "a" or self._href is None:
            return
        text = " ".join(part.strip() for part in self._text_parts if part.strip())
        self.links.append((self._href, text))
        self._href = None
        self._text_parts = []


def _filter_adviser_records(
    records: list[dict[str, Any]],
    query: SecInvestmentAdvisersQueryParams,
) -> list[dict[str, Any]]:
    """Apply client-side name and identifier filters."""
    filtered = records
    if query.query:
        needle = query.query.casefold()
        filtered = [
            record
            for record in filtered
            if needle
            in " ".join(
                str(record.get(field) or "")
                for field in ("legal_name", "primary_business_name")
            ).casefold()
        ]
    if query.crd:
        filtered = [
            record
            for record in filtered
            if _normalize_identifier(record.get("crd")) == _normalize_identifier(query.crd)
        ]
    if query.sec_number:
        filtered = [
            record
            for record in filtered
            if _normalize_identifier(record.get("sec_number"))
            == _normalize_identifier(query.sec_number)
        ]
    return filtered


def _read_report_frames(
    content: bytes,
    file_name: str,
) -> list[tuple[pd.DataFrame, str]]:
    """Read CSV, Excel, or ZIP adviser report content into data frames."""
    suffix = Path(file_name).suffix.lower()
    if suffix == ".zip":
        frames: list[tuple[pd.DataFrame, str]] = []
        with ZipFile(BytesIO(content)) as archive:
            for name in sorted(archive.namelist()):
                nested_suffix = Path(name).suffix.lower()
                if nested_suffix not in {".csv", ".xlsx", ".xls"}:
                    continue
                frames.extend(
                    _read_report_frames(archive.read(name), f"{file_name}:{name}")
                )
        return frames
    if suffix == ".csv":
        return [(_read_csv_bytes(content), file_name)]
    if suffix in {".xlsx", ".xls"}:
        return [(_read_excel_bytes(content), file_name)]
    return []


def _read_csv_bytes(content: bytes) -> pd.DataFrame:
    """Read CSV bytes as strings."""
    for encoding in ("utf-8-sig", "cp1252", "latin1"):
        try:
            return pd.read_csv(
                BytesIO(content),
                dtype="string",
                keep_default_na=False,
                encoding=encoding,
            )
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("utf-8", content, 0, 1, "Unable to decode CSV bytes")


def _read_excel_bytes(content: bytes) -> pd.DataFrame:
    """Read Excel bytes with pandas, with a small XLSX fallback parser."""
    try:
        return pd.read_excel(BytesIO(content), dtype="string", keep_default_na=False)
    except ImportError:
        return _read_simple_xlsx_bytes(content)


def _read_simple_xlsx_bytes(content: bytes) -> pd.DataFrame:
    """Read the first worksheet from a simple XLSX workbook."""
    with ZipFile(BytesIO(content)) as archive:
        shared_strings = _xlsx_shared_strings(archive)
        worksheet_name = _xlsx_first_worksheet_name(archive)
        worksheet = ElementTree.fromstring(archive.read(worksheet_name))

    rows: list[list[str]] = []
    for row in worksheet.findall(".//{*}sheetData/{*}row"):
        values_by_index: dict[int, str] = {}
        for cell in row.findall("{*}c"):
            reference = cell.attrib.get("r", "")
            values_by_index[_xlsx_column_index(reference)] = _xlsx_cell_value(
                cell, shared_strings
            )
        if values_by_index:
            width = max(values_by_index) + 1
            rows.append([values_by_index.get(index, "") for index in range(width)])

    if not rows:
        return pd.DataFrame()
    header, *body = rows
    return pd.DataFrame(body, columns=header).astype("string")


def _normalize_frame(
    frame: pd.DataFrame,
) -> list[dict[str, Any]]:
    """Normalize one adviser report data frame."""
    columns = {_normalize_column(column): column for column in frame.columns}
    profiles: list[dict[str, Any]] = []
    for _, row in frame.iterrows():
        profile = _profile_record(row, columns)
        if profile.get("crd") or profile.get("sec_number") or profile.get("legal_name"):
            profiles.append(profile)
    return profiles


def _profile_record(
    row: pd.Series,
    columns: dict[str, Any],
) -> dict[str, Any]:
    """Normalize one adviser report row."""
    website = _clean_text(_field_value(row, columns, PROFILE_ALIASES["website"]))
    return {
        "crd": _clean_identifier(_field_value(row, columns, PROFILE_ALIASES["crd"])),
        "sec_number": _clean_identifier(
            _field_value(row, columns, PROFILE_ALIASES["sec_number"])
        ),
        "legal_name": _clean_text(_field_value(row, columns, PROFILE_ALIASES["name"])),
        "primary_business_name": _clean_text(
            _field_value(row, columns, PROFILE_ALIASES["business_name"])
        ),
        "status": _clean_text(_field_value(row, columns, PROFILE_ALIASES["status"])),
        "regulatory_assets_under_management": _clean_int(
            _field_value(row, columns, PROFILE_ALIASES["aum"])
        ),
        "discretionary_aum": _clean_int(
            _field_value(row, columns, PROFILE_ALIASES["discretionary_aum"])
        ),
        "non_discretionary_aum": _clean_int(
            _field_value(row, columns, PROFILE_ALIASES["non_discretionary_aum"])
        ),
        "separately_managed_accounts_aum": _clean_int(
            _field_value(
                row,
                columns,
                PROFILE_ALIASES["separately_managed_accounts_aum"],
            )
        ),
        "pooled_investment_vehicles_aum": _clean_int(
            _field_value(
                row,
                columns,
                PROFILE_ALIASES["pooled_investment_vehicles_aum"],
            )
        ),
        "employees": _clean_int(
            _field_value(row, columns, PROFILE_ALIASES["employees"])
        ),
        "phone": _clean_text(_field_value(row, columns, PROFILE_ALIASES["phone"])),
        "city": _clean_text(_field_value(row, columns, PROFILE_ALIASES["city"])),
        "state": _clean_text(_field_value(row, columns, PROFILE_ALIASES["state"])),
        "country": _clean_text(_field_value(row, columns, PROFILE_ALIASES["country"])),
        "website": _normalize_website(website),
    }


def _field_value(
    row: pd.Series,
    columns: dict[str, Any],
    aliases: tuple[str, ...],
) -> str:
    """Return the first non-empty field for a set of normalized aliases."""
    for alias in aliases:
        column = columns.get(_normalize_column(alias))
        if column is None:
            continue
        value = row.get(column)
        if value is not None and str(value).strip():
            return str(value)
    return ""


def _normalize_column(value: Any) -> str:
    """Normalize a source column name for alias matching."""
    return sub(r"[^a-z0-9]+", "", str(value).strip().lower())


def _clean_text(value: str) -> str | None:
    """Trim text and return None for empty values."""
    cleaned = " ".join(str(value or "").split())
    return cleaned or None


def _clean_identifier(value: str) -> str | None:
    """Trim identifier-like fields without numeric coercion."""
    cleaned = _clean_text(value)
    if cleaned is None:
        return None
    if cleaned.endswith(".0") and cleaned[:-2].isdigit():
        return cleaned[:-2]
    return cleaned


def _clean_int(value: str) -> int | None:
    """Parse integer-like SEC report fields."""
    cleaned = sub(r"[^0-9-]", "", str(value or ""))
    if not cleaned or cleaned == "-":
        return None
    return int(cleaned)


def _normalize_identifier(value: Any) -> str:
    """Normalize identifier fields for exact comparisons."""
    return str(value or "").strip().casefold()


def _normalize_website(value: str | None) -> str | None:
    """Normalize website values to absolute HTTPS URLs when possible."""
    if not value:
        return None
    if value.startswith(("http://", "https://")):
        return value
    return f"https://{value}"


def _link_format(url: str) -> str | None:
    """Return supported adviser report format from a URL."""
    suffix = Path(urlparse(url).path).suffix.lower().lstrip(".")
    if suffix == "xls":
        return "xlsx"
    if suffix in {"zip", "xlsx", "csv"}:
        return suffix
    return None


def _looks_current(url: str, text: str) -> bool:
    """Return True when a report link appears to point to current files."""
    value = f"{url} {text}".lower()
    return "current" in value or "latest" in value


def _download_filename(link: AdviserReportLink) -> str:
    """Return a stable file name for a report link."""
    filename = Path(urlparse(link.url).path).name
    return filename or f"adviser-report.{link.format}"


def _adviser_report_category(link: AdviserReportLink) -> str | None:
    """Return registered or exempt for adviser report link text."""
    text_value = link.text.casefold()
    if "exempt" in text_value:
        return "exempt"
    if "registered" in text_value:
        return "registered"

    value = Path(urlparse(link.url).path).name.casefold()
    if "exempt" in value:
        return "exempt"
    if "registered" in value:
        return "registered"
    return None


def _xlsx_shared_strings(archive: ZipFile) -> list[str]:
    """Read XLSX shared strings."""
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    shared_strings_root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
    strings: list[str] = []
    for item in shared_strings_root.findall("{*}si"):
        parts = [node.text or "" for node in item.findall(".//{*}t")]
        strings.append("".join(parts))
    return strings


def _xlsx_first_worksheet_name(archive: ZipFile) -> str:
    """Return the first worksheet path from an XLSX archive."""
    for name in archive.namelist():
        if name.startswith("xl/worksheets/") and name.endswith(".xml"):
            return name
    raise ValueError("XLSX workbook does not contain a worksheet")


def _xlsx_column_index(reference: str) -> int:
    """Convert an XLSX cell reference into a zero-based column index."""
    letters = "".join(character for character in reference if character.isalpha())
    index = 0
    for character in letters:
        index = index * 26 + ord(character.upper()) - ord("A") + 1
    return max(index - 1, 0)


def _xlsx_cell_value(cell: Any, shared_strings: list[str]) -> str:
    """Read a cell value from a simple XLSX worksheet cell."""
    if cell.attrib.get("t") == "inlineStr":
        return "".join(node.text or "" for node in cell.findall(".//{*}t"))
    value = cell.find("{*}v")
    if value is None or value.text is None:
        return ""
    if cell.attrib.get("t") == "s":
        return shared_strings[int(value.text)]
    return value.text


PROFILE_ALIASES: dict[str, tuple[str, ...]] = {
    "name": (
        "Legal Name",
        "Primary Business Name",
        "1A",
        "Organization CRD Name",
        "Firm Name",
    ),
    "business_name": (
        "Primary Business Name",
        "DBA Name",
        "Doing Business As",
    ),
    "crd": (
        "CRD Number",
        "Firm CRD Number",
        "Organization CRD#",
        "1E1",
        "CRD",
    ),
    "sec_number": (
        "SEC Number",
        "SEC File Number",
        "SEC#",
        "1E2",
    ),
    "status": (
        "Status",
        "Registration Status",
    ),
    "aum": (
        "Regulatory Assets Under Management",
        "Regulatory AUM",
        "RAUM",
        "5F2C",
    ),
    "discretionary_aum": (
        "Discretionary RAUM",
        "Discretionary AUM",
        "5F2A",
    ),
    "non_discretionary_aum": (
        "Non-Discretionary RAUM",
        "Non Discretionary RAUM",
        "Non-Discretionary AUM",
        "5F2B",
    ),
    "separately_managed_accounts_aum": (
        "Separately Managed Accounts RAUM",
        "Separately Managed Accounts AUM",
    ),
    "pooled_investment_vehicles_aum": (
        "Pooled Investment Vehicles RAUM",
        "Pooled Investment Vehicles AUM",
    ),
    "employees": (
        "Total Employees",
        "Number of Employees",
        "5A",
    ),
    "phone": (
        "Main Office Telephone Number",
        "Phone Number",
        "1F1",
    ),
    "city": (
        "Main Office City",
        "City",
        "1F2A",
    ),
    "state": (
        "Main Office State",
        "State",
        "1F2B",
    ),
    "country": (
        "Main Office Country",
        "Country",
        "1F2E",
    ),
    "website": (
        "Website Address",
        "Website",
        "1I",
    ),
}
