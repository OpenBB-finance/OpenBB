"""Current SEC Form ADV Part 1 data."""

from __future__ import annotations

import asyncio
import csv
import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from io import BytesIO, TextIOWrapper
from typing import Literal
from zipfile import BadZipFile, ZipFile

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_sec.utils.cache import cached_bytes, cached_request
from openbb_sec.utils.definitions import SEC_HEADERS

SEC_DATA_CATALOG_URL = "https://www.sec.gov/data.json"
ADVISER_DATASET_TITLE = (
    "Information About Registered Investment Advisers and Exempt Reporting Advisers"
)
CATALOG_CACHE_SECONDS = 24 * 60 * 60
REPORT_CACHE_SECONDS = 35 * 24 * 60 * 60

AdviserUniverseType = Literal["registered", "exempt"]
_REPORT_MONTH = re.compile(r"([A-Z][a-z]+ \d{4})")
_REQUIRED_COLUMNS = {
    "Organization CRD#",
    "SEC#",
    "Firm Type",
    "Primary Business Name",
    "Legal Name",
    "SEC Current Status",
    "Latest ADV Filing Date",
}

_COLUMN_NAMES = {
    "Organization CRD#": "crd",
    "Additional CRD Number": "additional_crd",
    "Total number of additional CRD numbers": "additional_crd_count",
    "SEC#": "sec_number",
    "Total number of relying advisers": "relying_adviser_count",
    "Total number of CIK numbers": "cik_count",
    "Main Office Street Address 1": "main_office_address_line_1",
    "Main Office Street Address 2": "main_office_address_line_2",
    "Main Office Private Residence Flag": "main_office_private_residence",
    "Main Office Telephone Number": "main_office_phone",
    "Main Office Facsimile Number": "main_office_fax",
    "Total number of offices, other than your Principal Office and place of business": (
        "other_office_count"
    ),
    "Mail Office Street Address 1": "mail_office_address_line_1",
    "Mail Office Street Address 2": "mail_office_address_line_2",
    "Mail Office Private Residence Flag": "mail_office_private_residence",
    "SEC Current Status": "status",
    "SEC Status Effective Date": "status_effective_date",
    "Website Address": "website",
    "Total Number of Website Addresses": "website_count",
    "Total Number of Books and Records Locations": "books_and_records_location_count",
    "Total Number of Acquired Firms": "acquired_firm_count",
    "5A": "employee_count",
    "5F(2)(a)": "discretionary_aum",
    "5F(2)(b)": "non_discretionary_aum",
    "5F(2)(c)": "regulatory_assets_under_management",
    "5F(2)(d)": "discretionary_account_count",
    "5F(2)(e)": "non_discretionary_account_count",
    "5F(2)(f)": "account_count",
    "5F(3)": "non_us_clients_aum",
    "Count of IA Affiliates": "investment_adviser_affiliate_count",
    "Count of IA/BD Affiliates": "investment_adviser_broker_dealer_affiliate_count",
    "Count of BD Affiliates": "broker_dealer_affiliate_count",
    "Count of Private Funds - 7B(1)": "private_fund_count",
    "Total Gross Assets of Private Funds": "private_fund_gross_assets",
    "Count of Private Funds - 7B(2)": "private_fund_adviser_count",
    "Total Custody Amount": "custody_amount",
    "Count of Control person Public Reporting Company": (
        "public_reporting_company_control_person_count"
    ),
}

_DATE_FIELDS = {
    "status_effective_date",
    "latest_adv_filing_date",
}
_INTEGER_FIELDS = {
    "additional_crd_count",
    "relying_adviser_count",
    "cik_count",
    "other_office_count",
    "website_count",
    "books_and_records_location_count",
    "acquired_firm_count",
    "employee_count",
    "discretionary_account_count",
    "non_discretionary_account_count",
    "account_count",
    "investment_adviser_affiliate_count",
    "investment_adviser_broker_dealer_affiliate_count",
    "broker_dealer_affiliate_count",
    "private_fund_count",
    "private_fund_adviser_count",
    "public_reporting_company_control_person_count",
}
_NUMBER_FIELDS = {
    "discretionary_aum",
    "non_discretionary_aum",
    "regulatory_assets_under_management",
    "non_us_clients_aum",
    "private_fund_gross_assets",
    "custody_amount",
}


@dataclass(frozen=True)
class AdviserReport:
    """One published SEC adviser universe report."""

    registration_type: AdviserUniverseType
    report_date: date
    media_type: str
    url: str


class SecAdviserUniverseQueryParams(QueryParams):
    """Current SEC Form ADV Part 1 dataset query."""

    registration_type: AdviserUniverseType = Field(
        description="Registered or exempt adviser population to return.",
    )
    crd: str | None = Field(
        default=None,
        description="Central Registration Depository (CRD) number to return.",
        pattern=r"^\d+$",
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use cached SEC responses.",
    )


class SecAdviserUniverseData(Data):
    """Current Form ADV Part 1 data for one SEC investment adviser.

    Stable identifiers and metrics are typed explicitly. Every additional column
    from the registered or exempt SEC report is retained as a dynamic flat field.
    Form item headings are normalized with an ``item_`` prefix.
    """

    crd: str = Field(description="Central Registration Depository (CRD) number.")
    sec_number: str = Field(description="SEC investment adviser number.")
    cik: str | None = Field(
        default=None,
        description="First reported CIK, zero-padded to 10 digits.",
    )
    cik_count: int | None = Field(
        default=None,
        description="Total number of CIKs reported by the firm.",
    )
    primary_business_name: str = Field(description="Primary business name.")
    legal_name: str = Field(description="Legal name.")
    firm_type: str = Field(
        description="Registration category reported in the SEC data file."
    )
    status: str = Field(description="Current SEC registration status.")
    latest_adv_filing_date: date = Field(
        description="Date of the latest Form ADV filing."
    )
    employee_count: int | None = Field(
        default=None,
        description="Number of employees reported in Form ADV Item 5.A.",
    )
    discretionary_aum: int | float | None = Field(
        default=None,
        description="Discretionary regulatory assets under management.",
    )
    non_discretionary_aum: int | float | None = Field(
        default=None,
        description="Non-discretionary regulatory assets under management.",
    )
    regulatory_assets_under_management: int | float | None = Field(
        default=None,
        description="Total regulatory assets under management.",
    )
    discretionary_account_count: int | None = Field(
        default=None,
        description="Number of discretionary accounts.",
    )
    non_discretionary_account_count: int | None = Field(
        default=None,
        description="Number of non-discretionary accounts.",
    )
    account_count: int | None = Field(
        default=None,
        description="Total number of accounts.",
    )
    report_date: date = Field(
        description="Report month, represented by its first calendar day."
    )


class SecAdviserUniverseFetcher(
    Fetcher[SecAdviserUniverseQueryParams, list[SecAdviserUniverseData]]
):
    """SEC investment adviser universe fetcher."""

    @staticmethod
    def transform_query(params: dict[str, object]) -> SecAdviserUniverseQueryParams:
        """Transform query parameters."""
        return SecAdviserUniverseQueryParams.model_validate(params)

    @staticmethod
    async def aextract_data(
        query: SecAdviserUniverseQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: object,
    ) -> list[dict[str, object]]:
        """Download and parse the latest SEC Form ADV report."""
        catalog = await cached_request(
            SEC_DATA_CATALOG_URL,
            headers=SEC_HEADERS,
            use_cache=query.use_cache,
            expire=CATALOG_CACHE_SECONDS,
        )
        report = _latest_report(catalog, query.registration_type)
        content = await asyncio.to_thread(
            cached_bytes,
            report.url,
            headers=SEC_HEADERS,
            use_cache=query.use_cache,
            expire=REPORT_CACHE_SECONDS,
            timeout=180,
        )
        records = await asyncio.to_thread(
            _parse_report,
            content,
            report,
            query.crd,
        )
        if not records:
            if query.crd is not None:
                raise EmptyDataError(
                    f"No {query.registration_type} investment adviser with CRD "
                    f"{query.crd} was found."
                )
            raise EmptyDataError(
                f"The {report.report_date:%B %Y} SEC "
                f"{query.registration_type} adviser report was empty."
            )
        return records

    @staticmethod
    def transform_data(
        query: SecAdviserUniverseQueryParams,
        data: list[dict[str, object]],
        **kwargs: object,
    ) -> list[SecAdviserUniverseData]:
        """Transform raw records to the public model."""
        return [SecAdviserUniverseData.model_validate(record) for record in data]


def _latest_report(
    catalog: object,
    registration_type: AdviserUniverseType,
) -> AdviserReport:
    """Select the latest requested report from the SEC data catalog."""
    catalog_record = _object_record(
        catalog,
        "Invalid SEC data catalog response: expected an object.",
    )
    datasets = catalog_record.get("dataset")
    if not isinstance(datasets, list):
        raise OpenBBError("Invalid SEC data catalog response: expected a dataset list.")

    distributions: object = None
    for dataset in datasets:
        dataset_record = _object_record(
            dataset,
            "Invalid SEC data catalog response: dataset entries must be objects.",
        )
        if dataset_record.get("title") == ADVISER_DATASET_TITLE:
            distributions = dataset_record.get("distribution")
            break
    if not isinstance(distributions, list):
        raise OpenBBError(
            "The SEC data catalog is missing the investment adviser dataset."
        )

    reports = [
        report
        for item in distributions
        if (report := _report_from_distribution(item)) is not None
        and report.registration_type == registration_type
    ]
    if not reports:
        raise EmptyDataError(
            f"No {registration_type} investment adviser reports were found "
            "in the SEC data catalog."
        )

    latest_date = max(report.report_date for report in reports)
    latest = [report for report in reports if report.report_date == latest_date]
    if len(latest) != 1:
        raise OpenBBError(
            f"The SEC data catalog contains multiple {registration_type} adviser "
            f"reports for {latest_date:%B %Y}."
        )
    report = latest[0]
    if report.media_type != "application/zip" or not report.url.lower().endswith(
        ".zip"
    ):
        raise OpenBBError(
            f"The latest {registration_type} adviser report uses unsupported "
            f"media type '{report.media_type or 'unknown'}'."
        )
    return report


def _report_from_distribution(item: object) -> AdviserReport | None:
    """Parse one SEC data catalog distribution."""
    record = _object_record(
        item,
        "Invalid SEC data catalog response: distributions must be objects.",
    )
    title = record.get("title")
    media_type = record.get("mediaType")
    url = record.get("downloadURL")
    if (
        not isinstance(title, str)
        or not isinstance(media_type, str)
        or not isinstance(url, str)
    ):
        return None
    title = title.strip()
    media_type = media_type.strip()
    url = url.strip()

    registration_type: AdviserUniverseType
    if title.startswith("Registered Investment Advisers"):
        registration_type = "registered"
    elif title.startswith(("Exempt Investment Advisers", "Exempt Reporting Advisers")):
        registration_type = "exempt"
    else:
        return None

    match = _REPORT_MONTH.search(title)
    if match is None:
        raise OpenBBError(
            f"Invalid SEC adviser report title: unable to read date from '{title}'."
        )
    try:
        report_date = datetime.strptime(match.group(1), "%B %Y").date()  # noqa: DTZ007
    except ValueError as exc:
        raise OpenBBError(f"Invalid SEC adviser report date in '{title}'.") from exc
    return AdviserReport(
        registration_type=registration_type,
        report_date=report_date,
        media_type=media_type,
        url=url,
    )


def _parse_report(
    content: bytes,
    report: AdviserReport,
    crd: str | None = None,
) -> list[dict[str, object]]:
    """Parse current Form ADV rows from one SEC adviser report archive."""
    try:
        archive = ZipFile(BytesIO(content))
    except BadZipFile as exc:
        raise OpenBBError(
            "Invalid SEC adviser report: expected a ZIP archive."
        ) from exc

    with archive:
        csv_files = [
            item
            for item in archive.infolist()
            if not item.is_dir() and item.filename.lower().endswith(".csv")
        ]
        if len(csv_files) != 1:
            raise OpenBBError(
                "Invalid SEC adviser report: expected exactly one CSV file."
            )
        with (
            archive.open(csv_files[0]) as raw_file,
            TextIOWrapper(raw_file, encoding="cp1252", newline="") as text_file,
        ):
            reader = csv.DictReader(text_file)
            columns = set(reader.fieldnames or ())
            missing = sorted(_REQUIRED_COLUMNS - columns)
            if missing:
                raise OpenBBError(
                    "Invalid SEC adviser report: missing required columns "
                    + ", ".join(missing)
                    + "."
                )
            column_names = _public_column_names(reader.fieldnames or [])
            records: list[dict[str, object]] = []
            for row in reader:
                if (
                    crd is not None
                    and _optional_text(row.get("Organization CRD#")) != crd
                ):
                    continue
                records.append(_adviser_record(row, report, column_names))
                if crd is not None:
                    break
            return records


def _adviser_record(
    row: dict[str, str | None],
    report: AdviserReport,
    column_names: dict[str, str],
) -> dict[str, object]:
    """Map one SEC Form ADV row without discarding source columns."""
    record = {
        public_name: _field_value(public_name, row.get(source_name))
        for source_name, public_name in column_names.items()
    }
    cik = record.get("cik")
    if cik is not None:
        if not isinstance(cik, str) or not cik.isdigit():
            raise OpenBBError("Invalid SEC adviser report: CIK must be numeric.")
        record["cik"] = cik.zfill(10)
    record["crd"] = _required_text(record.get("crd"), "Organization CRD#")
    record["sec_number"] = _required_text(record.get("sec_number"), "SEC#")
    record["primary_business_name"] = _required_text(
        record.get("primary_business_name"), "Primary Business Name"
    )
    record["legal_name"] = _required_text(record.get("legal_name"), "Legal Name")
    record["firm_type"] = _required_text(record.get("firm_type"), "Firm Type")
    record["status"] = _required_text(record.get("status"), "SEC Current Status")
    record["latest_adv_filing_date"] = _required_date(
        record.get("latest_adv_filing_date"), "Latest ADV Filing Date"
    )
    record["report_date"] = report.report_date
    return record


def _public_column_names(columns: Sequence[str]) -> dict[str, str]:
    """Build unique Python field names for all SEC source columns."""
    names = {
        column: _COLUMN_NAMES.get(column, _normalize_column_name(column))
        for column in columns
    }
    if len(set(names.values())) != len(names):
        raise OpenBBError(
            "Invalid SEC adviser report: source columns map to duplicate field names."
        )
    return names


def _normalize_column_name(value: str) -> str:
    """Normalize an SEC heading while retaining its Form ADV item number."""
    name = re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")
    if name and name[0].isdigit():
        name = f"item_{name}"
    if not name:
        raise OpenBBError("Invalid SEC adviser report: empty column heading.")
    return name


def _field_value(field: str, value: object) -> object:
    """Parse fields with unambiguous scalar types and retain all others as text."""
    if field in _DATE_FIELDS:
        return _optional_date(value)
    if field in _INTEGER_FIELDS:
        return _optional_int(value)
    if field in _NUMBER_FIELDS:
        return _optional_number(value)
    return _optional_text(value)


def _required_text(value: object, field: str) -> str:
    """Normalize a required SEC report value."""
    cleaned = _optional_text(value)
    if cleaned is None:
        raise OpenBBError(f"Invalid SEC adviser report: {field} is required.")
    return cleaned


def _required_date(value: object, field: str) -> date:
    """Return a required SEC report date."""
    if not isinstance(value, date):
        raise OpenBBError(f"Invalid SEC adviser report: {field} is required.")
    return value


def _optional_text(value: object) -> str | None:
    """Normalize an optional SEC report value."""
    if value is None:
        return None
    if not isinstance(value, str | int) or isinstance(value, bool):
        raise OpenBBError("Invalid SEC adviser report: expected a scalar value.")
    cleaned = " ".join(str(value).split())
    return cleaned or None


def _optional_int(value: object) -> int | None:
    """Normalize an optional SEC report integer."""
    cleaned = _optional_text(value)
    if cleaned is None:
        return None
    cleaned = cleaned.replace(",", "")
    if not cleaned.isdigit():
        raise OpenBBError("Invalid SEC adviser report: expected an integer value.")
    return int(cleaned)


def _optional_number(value: object) -> int | float | None:
    """Normalize an optional SEC numeric value."""
    cleaned = _optional_text(value)
    if cleaned is None:
        return None
    try:
        number = Decimal(cleaned.replace(",", "").replace("$", ""))
    except InvalidOperation as exc:
        raise OpenBBError(
            "Invalid SEC adviser report: expected a numeric value."
        ) from exc
    return int(number) if number == number.to_integral_value() else float(number)


def _optional_date(value: object) -> date | None:
    """Normalize an optional SEC report date."""
    cleaned = _optional_text(value)
    if cleaned is None:
        return None
    try:
        return datetime.strptime(cleaned, "%m/%d/%Y").date()  # noqa: DTZ007
    except ValueError as exc:
        raise OpenBBError("Invalid SEC adviser report: expected MM/DD/YYYY.") from exc


def _object_record(value: object, error_message: str) -> dict[str, object]:
    """Validate a string-keyed object from the SEC data catalog."""
    if not isinstance(value, dict):
        raise OpenBBError(error_message)
    return {key: item for key, item in value.items() if isinstance(key, str)}
