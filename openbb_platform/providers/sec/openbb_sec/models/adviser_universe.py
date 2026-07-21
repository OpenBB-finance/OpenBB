"""Current SEC investment adviser universe."""

from __future__ import annotations

import asyncio
import csv
import re
from dataclasses import dataclass
from datetime import date, datetime
from io import BytesIO, TextIOWrapper
from typing import Literal, Protocol
from zipfile import BadZipFile, ZipFile

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_sec.utils.cache import cached_request
from openbb_sec.utils.definitions import SEC_HEADERS

SEC_DATA_CATALOG_URL = "https://www.sec.gov/data.json"
ADVISER_DATASET_TITLE = (
    "Information About Registered Investment Advisers and Exempt Reporting Advisers"
)
CATALOG_CACHE_SECONDS = 24 * 60 * 60
REPORT_CACHE_SECONDS = 35 * 24 * 60 * 60

AdviserUniverseType = Literal["registered", "exempt"]
AdviserRegistrationType = Literal[
    "SEC Registered",
    "SEC Exempt Reporting Adviser",
]

_REPORT_MONTH = re.compile(r"([A-Z][a-z]+ \d{4})")
_REQUIRED_COLUMNS = {
    "Organization CRD#",
    "SEC#",
    "CIK#",
    "Total number of CIK numbers",
    "Primary Business Name",
    "Legal Name",
    "SEC Current Status",
}


class _ReadableResponse(Protocol):
    async def read(self) -> bytes:
        """Return the response body."""


@dataclass(frozen=True)
class AdviserReport:
    """One published SEC adviser universe report."""

    registration_type: AdviserUniverseType
    report_date: date
    media_type: str
    url: str


class SecAdviserUniverseQueryParams(QueryParams):
    """SEC investment adviser universe query."""

    registration_type: AdviserUniverseType = Field(
        description="Adviser registration population to return.",
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use cached SEC responses.",
    )


class SecAdviserUniverseData(Data):
    """One firm in the current SEC investment adviser universe."""

    crd: str = Field(description="Central Registration Depository (CRD) number.")
    sec_number: str = Field(description="SEC investment adviser number.")
    cik: str | None = Field(
        default=None,
        description="First reported CIK, zero-padded to 10 digits.",
    )
    reported_cik_count: int | None = Field(
        default=None,
        description=(
            "Number of CIKs reported by the firm. The cik field contains only "
            "the first."
        ),
    )
    name: str = Field(description="Primary business name.")
    legal_name: str = Field(description="Legal name.")
    registration_type: AdviserRegistrationType = Field(
        description="SEC adviser registration category."
    )
    status: str = Field(description="Current SEC registration status.")
    report_period: date = Field(
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
        """Download and parse the latest SEC adviser universe report."""
        catalog = await cached_request(
            SEC_DATA_CATALOG_URL,
            headers=SEC_HEADERS,
            use_cache=query.use_cache,
            expire=CATALOG_CACHE_SECONDS,
        )
        report = _latest_report(catalog, query.registration_type)
        content = await cached_request(
            report.url,
            headers=SEC_HEADERS,
            response_callback=_read_response,
            use_cache=query.use_cache,
            expire=REPORT_CACHE_SECONDS,
            timeout=180,
        )
        if not isinstance(content, bytes):
            raise OpenBBError("Invalid SEC adviser report response: expected bytes.")
        records = await asyncio.to_thread(_parse_report, content, report)
        if not records:
            raise EmptyDataError(
                f"The {report.report_date:%B %Y} SEC adviser report was empty."
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


async def _read_response(response: _ReadableResponse, session: object) -> bytes:
    """Read a binary SEC response."""
    return await response.read()


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
) -> list[dict[str, object]]:
    """Parse the identity columns from one SEC adviser report archive."""
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
            return [_universe_record(row, report) for row in reader]


def _universe_record(
    row: dict[str, str | None],
    report: AdviserReport,
) -> dict[str, object]:
    """Map one SEC report row to the public universe model."""
    cik = _optional_text(row.get("CIK#"))
    if cik is not None:
        if not cik.isdigit():
            raise OpenBBError("Invalid SEC adviser report: CIK must be numeric.")
        cik = cik.zfill(10)
    return {
        "crd": _required_text(row.get("Organization CRD#"), "Organization CRD#"),
        "sec_number": _required_text(row.get("SEC#"), "SEC#"),
        "cik": cik,
        "reported_cik_count": _optional_int(row.get("Total number of CIK numbers")),
        "name": _required_text(
            row.get("Primary Business Name"), "Primary Business Name"
        ),
        "legal_name": _required_text(row.get("Legal Name"), "Legal Name"),
        "registration_type": (
            "SEC Registered"
            if report.registration_type == "registered"
            else "SEC Exempt Reporting Adviser"
        ),
        "status": _required_text(row.get("SEC Current Status"), "SEC Current Status"),
        "report_period": report.report_date,
    }


def _required_text(value: object, field: str) -> str:
    """Normalize a required SEC report value."""
    cleaned = _optional_text(value)
    if cleaned is None:
        raise OpenBBError(f"Invalid SEC adviser report: {field} is required.")
    return cleaned


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
    if not cleaned.isdigit():
        raise OpenBBError("Invalid SEC adviser report: expected an integer value.")
    return int(cleaned)


def _object_record(value: object, error_message: str) -> dict[str, object]:
    """Validate a string-keyed object from the SEC data catalog."""
    if not isinstance(value, dict):
        raise OpenBBError(error_message)
    return {key: item for key, item in value.items() if isinstance(key, str)}
