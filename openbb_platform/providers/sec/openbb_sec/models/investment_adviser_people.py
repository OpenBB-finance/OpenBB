"""SEC investment adviser related people from Form ADV Part 1 data."""

from __future__ import annotations

import csv
from calendar import monthrange
from datetime import date, timedelta
from io import BytesIO, TextIOWrapper
from typing import Any
from zipfile import ZipFile

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, model_validator

from openbb_sec.utils.definitions import HEADERS

ADV_PART1_ARCHIVE_URL = (
    "https://www.sec.gov/files/adv-filing-data-20111105-20241231-part1.zip"
)
ADV_MONTHLY_BASE_URL = "https://reports.adviserinfo.sec.gov/reports/foia/advFilingData"
ADV_HISTORICAL_END_DATE = date(2024, 12, 31)


class SecInvestmentAdviserPeopleQueryParams(QueryParams):
    """SEC investment adviser people query.

    Source: https://www.sec.gov/foia-services/frequently-requested-documents/form-adv-data
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
    start_date: date | None = Field(
        default=None,
        description="Start date for ADV filing submission dates.",
    )
    end_date: date | None = Field(
        default=None,
        description="End date for ADV filing submission dates.",
    )
    limit: int = Field(
        default=100,
        description="Maximum number of related-person records to return.",
        ge=1,
    )
    use_cache: bool = Field(
        default=True,
        description="Whether or not to use cache.",
    )

    @model_validator(mode="after")
    def validate_selector(self) -> SecInvestmentAdviserPeopleQueryParams:
        """Require at least one business selector."""
        if not any((self.query, self.crd, self.sec_number, self.start_date, self.end_date)):
            raise ValueError(
                "At least one of query, crd, sec_number, start_date, or end_date "
                "is required."
            )
        return self


class SecInvestmentAdviserPeopleData(Data):
    """SEC investment adviser related-person row."""

    crd: str | None = Field(
        default=None,
        description="Central Registration Depository (CRD) number.",
    )
    sec_number: str | None = Field(
        default=None,
        description="SEC adviser number.",
    )
    adviser_name: str | None = Field(
        default=None,
        description="Investment adviser name from the ADV filing metadata.",
    )
    filing_id: str | None = Field(
        default=None,
        description="SEC Form ADV archive filing identifier.",
    )
    person_name: str = Field(description="Person name disclosed in Form ADV Part 1.")
    role: str | None = Field(
        default=None,
        description="Normalized role inferred from the ADV source field.",
    )
    schedule: str | None = Field(
        default=None,
        description="ADV Schedule A/B schedule code when applicable.",
    )
    title_or_status: str | None = Field(
        default=None,
        description="Schedule A/B title or status when disclosed.",
    )
    ownership_code: str | None = Field(
        default=None,
        description="Schedule A/B ownership code when disclosed.",
    )
    control_person: bool | None = Field(
        default=None,
        description="Whether Schedule A/B marks the person as a control person.",
    )
    owner_id: str | None = Field(
        default=None,
        description="Schedule A/B owner identifier when disclosed.",
    )
    source_table: str = Field(description="Source ADV archive table name.")


class SecInvestmentAdviserPeopleFetcher(
    Fetcher[
        SecInvestmentAdviserPeopleQueryParams,
        list[SecInvestmentAdviserPeopleData],
    ]
):
    """SEC investment adviser people fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecInvestmentAdviserPeopleQueryParams:
        """Transform query parameters."""
        return SecInvestmentAdviserPeopleQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecInvestmentAdviserPeopleQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return normalized ADV related-person rows."""
        records = load_investment_adviser_people_records(
            start_date=query.start_date,
            end_date=query.end_date,
            use_cache=query.use_cache,
            **kwargs,
        )
        records = _filter_people_records(records, query)
        return records[: query.limit]

    @staticmethod
    def transform_data(
        query: SecInvestmentAdviserPeopleQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[SecInvestmentAdviserPeopleData]:
        """Transform raw data to the model format."""
        return [SecInvestmentAdviserPeopleData.model_validate(d) for d in data]


def load_investment_adviser_people_records(
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    use_cache: bool = True,
    **kwargs: Any,
) -> list[dict[str, Any]]:
    """Load SEC Form ADV Part 1 related-person records."""
    from openbb_sec.utils.ratelimit import sec_make_request

    session = kwargs.get("session")
    request_kwargs: dict[str, Any] = {"headers": HEADERS}
    if session is not None:
        request_kwargs["session"] = session
    records: list[dict[str, Any]] = []
    for url in _adv_archive_urls(start_date=start_date, end_date=end_date, **kwargs):
        response = sec_make_request(url, **request_kwargs)
        response.raise_for_status()
        records.extend(normalize_adv_part1_people_zip(response.content))
    return _filter_by_filing_date(records, start_date=start_date, end_date=end_date)


def normalize_adv_part1_people_zip(content: bytes) -> list[dict[str, Any]]:
    """Normalize ADV Part 1 Schedule A/B and 1J/1K rows from a SEC ZIP file."""
    with ZipFile(BytesIO(content)) as archive:
        firm_rows = _load_firm_rows(archive)
        people_rows: list[dict[str, Any]] = []
        for name in archive.namelist():
            if _is_schedule_ab_file(name):
                people_rows.extend(_schedule_ab_rows(archive, name, firm_rows))
            elif _is_adv_1j_1k_file(name):
                people_rows.extend(_adv_1j_1k_rows(archive, name, firm_rows))
    return people_rows


def _load_firm_rows(archive: ZipFile) -> dict[str, dict[str, str | None]]:
    rows: dict[str, dict[str, str | None]] = {}
    for name in archive.namelist():
        if not _is_firm_metadata_file(name):
            continue
        for row in _csv_rows(archive, name):
            filing_id = _clean(row.get("FilingID"))
            if not filing_id:
                continue
            rows[filing_id] = {
                "crd": _clean(
                    row.get("1J2 CRD Number")
                    or row.get("CRD Number")
                    or row.get("Organization CRD#")
                    or row.get("1E1")
                ),
                "sec_number": _clean(
                    row.get("1J1 SEC Number")
                    or row.get("SEC Number")
                    or row.get("SEC#")
                    or row.get("1D")
                ),
                "adviser_name": _clean(
                    row.get("1A")
                    or row.get("Legal Name")
                    or row.get("1C-Legal")
                    or row.get("Primary Business Name")
                    or row.get("1C-Business")
                ),
                "filing_date": _date_value(row.get("DateSubmitted")),
            }
    return rows


def _schedule_ab_rows(
    archive: ZipFile,
    name: str,
    firm_rows: dict[str, dict[str, str | None]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in _csv_rows(archive, name):
        filing_id = _clean(row.get("FilingID"))
        person_name = _clean(row.get("Full Legal Name"))
        if not filing_id or not person_name:
            continue
        control_person = _bool_value(row.get("Control Person"))
        rows.append(
            {
                **_firm_fields(firm_rows, filing_id),
                "filing_id": filing_id,
                "person_name": person_name,
                "role": "Control Person" if control_person else "Owner",
                "schedule": _clean(row.get("Schedule")),
                "title_or_status": _clean(row.get("Title or Status")),
                "ownership_code": _clean(row.get("Ownership Code")),
                "control_person": control_person,
                "owner_id": _clean(row.get("OwnerID")),
                "source_table": _source_table_name(name),
            }
        )
    return rows


def _adv_1j_1k_rows(
    archive: ZipFile,
    name: str,
    firm_rows: dict[str, dict[str, str | None]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    fields = (
        ("1J1 Name", "Chief Compliance Officer"),
        ("1J2 Name", "Additional Regulatory Contact"),
        ("1K Name", "Control Person Contact"),
    )
    for row in _csv_rows(archive, name):
        filing_id = _clean(row.get("FilingID"))
        if not filing_id:
            continue
        for field, role in fields:
            person_name = _clean(row.get(field))
            if not person_name:
                continue
            rows.append(
                {
                    **_firm_fields(firm_rows, filing_id),
                    "filing_id": filing_id,
                    "person_name": person_name,
                    "role": role,
                    "schedule": None,
                    "title_or_status": None,
                    "ownership_code": None,
                    "control_person": None,
                    "owner_id": None,
                    "source_table": _source_table_name(name),
                }
            )
    return rows


def _filter_people_records(
    records: list[dict[str, Any]],
    query: SecInvestmentAdviserPeopleQueryParams,
) -> list[dict[str, Any]]:
    filtered = records
    if query.crd:
        filtered = [row for row in filtered if str(row.get("crd") or "") == query.crd]
    if query.sec_number:
        filtered = [
            row for row in filtered if str(row.get("sec_number") or "") == query.sec_number
        ]
    if query.query:
        needle = query.query.casefold()
        filtered = [
            row
            for row in filtered
            if needle in str(row.get("adviser_name") or "").casefold()
        ]
    return filtered


def _csv_rows(archive: ZipFile, name: str) -> list[dict[str, str]]:
    with archive.open(name) as file:
        wrapper = TextIOWrapper(file, encoding="utf-8-sig", errors="replace")
        return list(csv.DictReader(wrapper))


def _firm_fields(
    firm_rows: dict[str, dict[str, str | None]],
    filing_id: str,
) -> dict[str, Any]:
    firm = firm_rows.get(filing_id, {})
    return {
        "crd": firm.get("crd"),
        "sec_number": firm.get("sec_number"),
        "adviser_name": firm.get("adviser_name"),
        **({"filing_date": firm["filing_date"]} if firm.get("filing_date") else {}),
    }


def _adv_archive_urls(
    *,
    start_date: date | None,
    end_date: date | None,
    **kwargs: Any,
) -> list[str]:
    if archive_url := kwargs.get("archive_url"):
        return [archive_url]
    urls: list[str] = []
    today = kwargs.get("today") or date.today()
    latest_month_end = _latest_complete_month_end(today)
    effective_end = min(end_date or latest_month_end, latest_month_end)
    if start_date is None or start_date <= ADV_HISTORICAL_END_DATE:
        urls.append(ADV_PART1_ARCHIVE_URL)
    if effective_end > ADV_HISTORICAL_END_DATE:
        monthly_start = max(start_date or date(2025, 1, 1), date(2025, 1, 1))
        urls.extend(
            _monthly_adv_archive_url(month_start)
            for month_start in _month_starts(monthly_start, effective_end)
        )
    return urls


def _monthly_adv_archive_url(month_start: date) -> str:
    month_end = date(
        month_start.year,
        month_start.month,
        monthrange(month_start.year, month_start.month)[1],
    )
    return (
        f"{ADV_MONTHLY_BASE_URL}/{month_start.year}/"
        f"ADV_Filing_Data_{month_start:%Y%m%d}_{month_end:%Y%m%d}.zip"
    )


def _latest_complete_month_end(today: date) -> date:
    first_day = date(today.year, today.month, 1)
    return first_day.replace(day=1) - timedelta(days=1)


def _month_starts(start_date: date, end_date: date) -> list[date]:
    current = date(start_date.year, start_date.month, 1)
    final = date(end_date.year, end_date.month, 1)
    starts: list[date] = []
    while current <= final:
        starts.append(current)
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)
    return starts


def _filter_by_filing_date(
    records: list[dict[str, Any]],
    *,
    start_date: date | None,
    end_date: date | None,
) -> list[dict[str, Any]]:
    if not start_date and not end_date:
        return records
    filtered = []
    for row in records:
        filing_date = row.get("filing_date")
        if not isinstance(filing_date, date):
            filtered.append(row)
            continue
        if start_date and filing_date < start_date:
            continue
        if end_date and filing_date > end_date:
            continue
        filtered.append(row)
    return filtered


def _is_firm_metadata_file(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    return (
        "FIRM_SEC_Feed" in name
        or name.startswith("IA_ADV_Base_A")
        or name.startswith("ERA_ADV_Base")
    )


def _source_table_name(path: str) -> str:
    name = path.rsplit("/", 1)[-1]
    if "Schedule_A_B" in name:
        return "IA_Schedule_A_B" if name.startswith("IA_") else "ERA_Schedule_A_B"
    return "IA_ADV_1J_1K" if name.startswith("IA_") else "ERA_ADV_1J_1K"


def _is_schedule_ab_file(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    return name.startswith(("IA_Schedule_A_B", "ERA_Schedule_A_B"))


def _is_adv_1j_1k_file(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    return name.startswith(("IA_ADV_1J_1K", "ERA_ADV_1J_1K"))


def _clean(value: Any) -> str | None:
    cleaned = str(value or "").strip()
    return cleaned or None


def _date_value(value: Any) -> date | None:
    cleaned = _clean(value)
    if not cleaned:
        return None
    try:
        return date.fromisoformat(cleaned[:10])
    except ValueError:
        return None


def _bool_value(value: Any) -> bool | None:
    cleaned = str(value or "").strip().casefold()
    if cleaned in {"y", "yes", "true", "1"}:
        return True
    if cleaned in {"n", "no", "false", "0"}:
        return False
    return None
