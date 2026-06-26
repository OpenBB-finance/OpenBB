"""SEC Form 13F structured data set helpers."""

from __future__ import annotations

import csv
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urljoin, urlparse
from zipfile import ZipFile

from openbb_sec.utils.definitions import HEADERS
from openbb_sec.utils.ratelimit import sec_make_request

SEC_13F_DATA_SETS_URL = (
    "https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets"
)
DEFAULT_YEARS = 5

_PERIOD_PATTERN = re.compile(r"\b(20\d{2}|2013)\s*[- ]?\s*[Qq]([1-4])\b")
_FILE_PERIOD_PATTERN = re.compile(r"(20\d{2}|2013)\s*[Qq]?([1-4])")
_DATE_RANGE_FILE_PATTERN = re.compile(
    r"\d{2}[a-z]{3}\d{4}-(\d{2}[a-z]{3}\d{4})",
    flags=re.IGNORECASE,
)
_QUARTER_END_MONTH_DAY = {
    1: (3, 31),
    2: (6, 30),
    3: (9, 30),
    4: (12, 31),
}


@dataclass(frozen=True)
class Sec13FDataSet:
    """Discovered SEC 13F structured data set ZIP link."""

    period_label: str
    url: str
    file_name: str
    size_text: str | None = None
    size_bytes: int | None = None
    period_date: date | None = None


@dataclass(frozen=True)
class Extracted13FDataSet:
    """Normalized records extracted from a 13F structured data set ZIP."""

    filers: list[dict[str, Any]]
    holdings: list[dict[str, Any]]


@dataclass
class _LinkCandidate:
    href: str
    label: str
    row_text: str


class _DataSetPageParser(HTMLParser):
    """Small table-aware parser for SEC data-set pages."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._tag_stack: list[str] = []
        self._current_link_href: str | None = None
        self._current_link_text: list[str] = []
        self._current_row_text: list[str] | None = None
        self._current_row_links: list[tuple[str, str]] = []
        self.links: list[_LinkCandidate] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Collect row and anchor context."""
        self._tag_stack.append(tag)
        if tag == "tr":
            self._current_row_text = []
            self._current_row_links = []
        if tag != "a":
            return
        attrs_dict = dict(attrs)
        href = attrs_dict.get("href")
        if href:
            self._current_link_href = href
            self._current_link_text = []

    def handle_endtag(self, tag: str) -> None:
        """Finalize link and row context."""
        if tag == "a" and self._current_link_href:
            label = _normalize_space(" ".join(self._current_link_text))
            if self._current_row_text is None:
                self.links.append(_LinkCandidate(self._current_link_href, label, ""))
            else:
                self._current_row_links.append((self._current_link_href, label))
            self._current_link_href = None
            self._current_link_text = []
        if tag == "tr":
            row_text = _normalize_space(" ".join(self._current_row_text or []))
            for href, label in self._current_row_links:
                self.links.append(_LinkCandidate(href, label, row_text))
            self._current_row_text = None
            self._current_row_links = []
        if self._tag_stack:
            self._tag_stack.pop()

    def handle_data(self, data: str) -> None:
        """Collect visible text."""
        if self._current_row_text is not None:
            self._current_row_text.append(data)
        if self._current_link_href:
            self._current_link_text.append(data)


def parse_13f_data_set_page(
    html: str,
    *,
    base_url: str = SEC_13F_DATA_SETS_URL,
) -> list[Sec13FDataSet]:
    """Parse SEC 13F structured data set links from a HTML page."""
    parser = _DataSetPageParser()
    parser.feed(html)
    data_sets: list[Sec13FDataSet] = []
    seen_urls: set[str] = set()

    for candidate in parser.links:
        href_lower = candidate.href.lower()
        label_lower = candidate.label.lower()
        if ".zip" not in href_lower:
            continue
        if "13f" not in href_lower and "13f" not in label_lower:
            continue

        url = urljoin(base_url, candidate.href)
        if url in seen_urls:
            continue
        seen_urls.add(url)

        file_name = _file_name_from_url(url)
        period_label = candidate.label or file_name
        period_date = _infer_period_date(period_label, file_name)
        size_text = _extract_size_text(candidate.row_text, period_label)

        data_sets.append(
            Sec13FDataSet(
                period_label=period_label,
                url=url,
                file_name=file_name,
                size_text=size_text,
                size_bytes=_parse_size_bytes(size_text),
                period_date=period_date,
            )
        )

    return data_sets


def filter_13f_data_sets(
    data_sets: Iterable[Sec13FDataSet],
    *,
    years: int = DEFAULT_YEARS,
    as_of: date | None = None,
    all_history: bool = False,
) -> list[Sec13FDataSet]:
    """Filter data sets to a recent horizon unless all history is requested."""
    items = list(data_sets)
    if all_history:
        return items
    if years <= 0:
        raise ValueError("years must be positive unless all_history=True")

    reference_date = as_of or date.today()
    cutoff = _subtract_years(reference_date, years)
    return [
        item
        for item in items
        if item.period_date is not None and item.period_date >= cutoff
    ]


def download_13f_data_set(
    data_set: Sec13FDataSet,
    destination_dir: str | Path,
    *,
    session: Any | None = None,
    force: bool = False,
    timeout: int = 60,
) -> Path:
    """Download a raw SEC 13F ZIP, skipping an existing same-size file."""
    destination = Path(destination_dir)
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / data_set.file_name

    if (
        not force
        and data_set.size_bytes is not None
        and target.exists()
        and target.stat().st_size == data_set.size_bytes
    ):
        return target

    request_kwargs: dict[str, Any] = {"headers": HEADERS, "timeout": timeout}
    if session is not None:
        request_kwargs["session"] = session
    response = sec_make_request(data_set.url, **request_kwargs)
    response.raise_for_status()
    target.write_bytes(response.content)
    return target


def extract_13f_data_set_zip(
    zip_path: str | Path,
    *,
    period_date: date | None = None,
) -> Extracted13FDataSet:
    """Extract normalized filer and holding records from a SEC 13F ZIP file."""
    path = Path(zip_path)
    with ZipFile(path) as archive:
        members = archive.namelist()
        submission_member = _find_member(members, _SUBMISSION_MEMBER_NAMES)
        coverpage_member = _find_member(members, _COVERPAGE_MEMBER_NAMES)
        info_member = _find_member(members, _INFO_MEMBER_NAMES)
        if not (submission_member or coverpage_member) or not info_member:
            raise ValueError(
                "13F ZIP must contain submission and information table members"
            )

        submission_rows = (
            _read_tabular_member(archive, submission_member)
            if submission_member
            else []
        )
        coverpage_rows = (
            _read_tabular_member(archive, coverpage_member)
            if coverpage_member
            else []
        )
        info_rows = _read_tabular_member(archive, info_member)

    filer_rows = _merge_filer_rows(submission_rows, coverpage_rows)
    filers = [_normalize_filer(row, period_date) for row in filer_rows]
    filers_by_accession = {
        filer["accession_number"]: filer
        for filer in filers
        if filer.get("accession_number")
    }
    totals_by_accession = _holding_totals_by_accession(info_rows)
    holdings = [
        _normalize_holding(row, filers_by_accession, totals_by_accession, period_date)
        for row in info_rows
    ]

    return Extracted13FDataSet(filers=filers, holdings=holdings)


_SUBMISSION_MEMBER_NAMES = (
    "submission.tsv",
    "submission.csv",
    "submissions.tsv",
    "submissions.csv",
)
_COVERPAGE_MEMBER_NAMES = (
    "coverpage.tsv",
    "coverpage.csv",
)
_INFO_MEMBER_NAMES = (
    "infotable.tsv",
    "infotable.csv",
    "informationtable.tsv",
    "informationtable.csv",
    "information_table.tsv",
    "information_table.csv",
    "information-table.tsv",
    "information-table.csv",
)


def _normalize_space(value: str) -> str:
    return " ".join(value.split())


def _file_name_from_url(url: str) -> str:
    path = urlparse(url).path
    name = unquote(Path(path).name)
    return name or "13f-data-set.zip"


def _extract_size_text(row_text: str, period_label: str) -> str | None:
    size_match = re.search(
        r"\b\d+(?:\.\d+)?\s*(?:bytes?|kb|kib|mb|mib|gb|gib)\b",
        row_text,
        flags=re.IGNORECASE,
    )
    if size_match:
        return size_match.group(0)

    without_label = row_text.replace(period_label, " ")
    size_match = re.search(
        r"\b\d+(?:\.\d+)?\s*(?:bytes?|kb|kib|mb|mib|gb|gib)\b",
        without_label,
        flags=re.IGNORECASE,
    )
    return size_match.group(0) if size_match else None


def _parse_size_bytes(size_text: str | None) -> int | None:
    if not size_text:
        return None
    match = re.fullmatch(
        r"\s*(\d+(?:\.\d+)?)\s*(bytes?|kb|kib|mb|mib|gb|gib)\s*",
        size_text,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    value = float(match.group(1))
    unit = match.group(2).lower()
    multipliers = {
        "byte": 1,
        "bytes": 1,
        "kb": 1024,
        "kib": 1024,
        "mb": 1024**2,
        "mib": 1024**2,
        "gb": 1024**3,
        "gib": 1024**3,
    }
    return int(value * multipliers[unit])


def _infer_period_date(*values: str) -> date | None:
    for value in values:
        date_range_match = _DATE_RANGE_FILE_PATTERN.search(value)
        if date_range_match:
            try:
                return datetime.strptime(
                    date_range_match.group(1).lower(),
                    "%d%b%Y",
                ).date()
            except ValueError:
                pass

        match = _PERIOD_PATTERN.search(value) or _FILE_PERIOD_PATTERN.search(value)
        if not match:
            continue
        year = int(match.group(1))
        quarter = int(match.group(2))
        month, day = _QUARTER_END_MONTH_DAY[quarter]
        return date(year, month, day)
    return None


def _subtract_years(value: date, years: int) -> date:
    try:
        return value.replace(year=value.year - years)
    except ValueError:
        return value.replace(year=value.year - years, day=28)


def _find_member(members: Iterable[str], accepted_names: Iterable[str]) -> str | None:
    accepted = set(accepted_names)
    for member in members:
        member_name = Path(member).name.lower()
        if member_name in accepted:
            return member
    for member in members:
        member_name = Path(member).name.lower()
        if member_name.endswith((".tsv", ".csv")) and any(
            accepted_name.removesuffix(".tsv").removesuffix(".csv") in member_name
            for accepted_name in accepted
        ):
            return member
    return None


def _read_tabular_member(archive: ZipFile, member: str) -> list[dict[str, str]]:
    delimiter = "\t" if member.lower().endswith(".tsv") else ","
    with archive.open(member) as raw:
        text = raw.read().decode("utf-8-sig")
    reader = csv.DictReader(text.splitlines(), delimiter=delimiter)
    return [
        {_normalize_header(key): _clean_cell(value) for key, value in row.items()}
        for row in reader
    ]


def _merge_filer_rows(
    submission_rows: Iterable[dict[str, str]],
    coverpage_rows: Iterable[dict[str, str]],
) -> list[dict[str, str]]:
    rows_by_accession: dict[str, dict[str, str]] = {}
    ordered_accessions: list[str] = []

    for row in submission_rows:
        accession = _first_value(row, "accession_number", "accession")
        if not accession:
            continue
        rows_by_accession[accession] = dict(row)
        ordered_accessions.append(accession)

    for row in coverpage_rows:
        accession = _first_value(row, "accession_number", "accession")
        if not accession:
            continue
        if accession not in rows_by_accession:
            rows_by_accession[accession] = {}
            ordered_accessions.append(accession)
        merged = rows_by_accession[accession]
        for key, value in row.items():
            if value and not merged.get(key):
                merged[key] = value

    return [rows_by_accession[accession] for accession in ordered_accessions]


def _normalize_header(value: str | None) -> str:
    if value is None:
        return ""
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def _clean_cell(value: str | None) -> str:
    return "" if value is None else value.strip()


def _normalize_filer(
    row: dict[str, str],
    fallback_period_date: date | None,
) -> dict[str, Any]:
    period = _first_value(
        row,
        "reportcalendarorquarter",
        "report_calendar_or_quarter",
        "periodofreport",
        "period_of_report",
        "period",
        "period_date",
    )
    filed = _first_value(row, "datefiled", "filed_date", "filing_date")
    return {
        "accession_number": _first_value(row, "accession_number", "accession"),
        "cik": _first_value(row, "cik", "filer_cik", "filingmanager_cik"),
        "name": _first_value(
            row,
            "filingmanager_name",
            "filer_name",
            "manager_name",
            "name",
        ),
        "period_date": _parse_date(period) or fallback_period_date,
        "filed_date": _parse_date(filed),
    }


def _normalize_holding(
    row: dict[str, str],
    filers_by_accession: dict[str, dict[str, Any]],
    totals_by_accession: dict[str, float],
    fallback_period_date: date | None,
) -> dict[str, Any]:
    accession = _first_value(row, "accession_number", "accession")
    filer = filers_by_accession.get(accession, {})
    value = _parse_float(_first_value(row, "value", "value_usd", "market_value"))
    total = totals_by_accession.get(accession, 0.0)
    return {
        "accession_number": accession,
        "cik": filer.get("cik") or _first_value(row, "cik", "filer_cik"),
        "filer_name": filer.get("name") or _first_value(row, "filer_name"),
        "issuer": _first_value(row, "nameofissuer", "name_of_issuer", "issuer"),
        "cusip": _first_value(row, "cusip"),
        "value": value,
        "shares": _parse_float(
            _first_value(row, "sshprnamt", "shares", "share_count")
        ),
        "weight": value / total if value is not None and total else None,
        "sector": _first_value(row, "sector") or None,
        "period_date": filer.get("period_date") or fallback_period_date,
    }


def _holding_totals_by_accession(rows: Iterable[dict[str, str]]) -> dict[str, float]:
    totals: dict[str, float] = {}
    for row in rows:
        accession = _first_value(row, "accession_number", "accession")
        value = _parse_float(_first_value(row, "value", "value_usd", "market_value"))
        if not accession or value is None:
            continue
        totals[accession] = totals.get(accession, 0.0) + value
    return totals


def _first_value(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = row.get(key)
        if value:
            return value
    return ""


def _parse_float(value: str) -> float | None:
    if not value:
        return None
    normalized = value.replace(",", "")
    try:
        return float(normalized)
    except ValueError:
        return None


def _parse_date(value: str) -> date | None:
    if not value:
        return None
    for fmt in (
        "%Y-%m-%d",
        "%m-%d-%Y",
        "%m/%d/%Y",
        "%Y%m%d",
        "%d-%b-%Y",
        "%d-%B-%Y",
    ):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return _infer_period_date(value)
