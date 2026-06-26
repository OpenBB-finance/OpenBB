"""SEC EDGAR filing index metadata."""

from __future__ import annotations

from datetime import date
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

from openbb_sec.utils.definitions import HEADERS
from openbb_sec.utils.ratelimit import sec_make_request

SEC_ARCHIVES_URL = "https://www.sec.gov/Archives"
SEC_FULL_INDEX_URL = "https://www.sec.gov/Archives/edgar/full-index"


class SecFilingIndexQueryParams(QueryParams):
    """SEC filing index query."""

    form_type: str | None = Field(
        default=None,
        description="Exact SEC form type to return. Amendments are controlled separately.",
    )
    start_date: date = Field(
        description="Start date for indexed filing dates.",
    )
    end_date: date | None = Field(
        default=None,
        description="End date for indexed filing dates. Defaults to today.",
    )
    include_amendments: bool = Field(
        default=True,
        description="Whether to include amendment forms such as D/A.",
    )
    limit: int | None = Field(
        default=None,
        description="Maximum number of index rows to return.",
        ge=1,
    )
    use_cache: bool = Field(
        default=True,
        description="Whether or not to use cache.",
    )


class SecFilingIndexData(Data):
    """SEC filing index row."""

    cik: str = Field(description="Central Index Key (CIK) for the filing entity.")
    company_name: str = Field(description="Company name from the SEC filing index.")
    form_type: str = Field(description="Exact SEC form type from the filing index.")
    filing_date: date = Field(description="Date the filing was submitted to EDGAR.")
    accession_number: str | None = Field(
        default=None,
        description="SEC accession number parsed from the index path.",
    )
    archive_path: str = Field(description="SEC Archives-relative filing path.")
    complete_submission_url: str = Field(
        description="URL for the complete SEC submission text file.",
    )
    filing_detail_url: str | None = Field(
        default=None,
        description="URL for the SEC filing detail/index page.",
    )


class SecFilingIndexFetcher(
    Fetcher[
        SecFilingIndexQueryParams,
        list[SecFilingIndexData],
    ]
):
    """SEC filing index fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecFilingIndexQueryParams:
        """Transform query parameters."""
        return SecFilingIndexQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecFilingIndexQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return SEC filing index metadata rows."""
        end_date = query.end_date or date.today()
        records: list[dict[str, Any]] = []
        for year, quarter in _quarters_between(query.start_date, end_date):
            records.extend(
                _load_quarter_index(
                    year,
                    quarter,
                    base_url=kwargs.get("base_url", SEC_FULL_INDEX_URL),
                    session=kwargs.get("session"),
                )
            )

        records = [
            record
            for record in records
            if query.start_date <= record["filing_date"] <= end_date
            and _matches_form_type(
                record["form_type"],
                query.form_type,
                include_amendments=query.include_amendments,
            )
        ]
        records = sorted(
            records,
            key=lambda record: (record["filing_date"], record["accession_number"] or ""),
            reverse=True,
        )
        return records[: query.limit] if query.limit is not None else records

    @staticmethod
    def transform_data(
        query: SecFilingIndexQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[SecFilingIndexData]:
        """Transform raw data to the model format."""
        return [SecFilingIndexData.model_validate(d) for d in data]


def _load_quarter_index(
    year: int,
    quarter: int,
    *,
    base_url: str = SEC_FULL_INDEX_URL,
    session: Any | None = None,
) -> list[dict[str, Any]]:
    """Load and parse one SEC quarterly master index."""
    url = f"{base_url.rstrip('/')}/{year}/QTR{quarter}/master.idx"
    request_kwargs: dict[str, Any] = {"headers": HEADERS}
    if session is not None:
        request_kwargs["session"] = session
    response = sec_make_request(url, **request_kwargs)
    response.raise_for_status()
    return parse_master_index(response.text)


def parse_master_index(text: str) -> list[dict[str, Any]]:
    """Parse an SEC master.idx document into flat filing index rows."""
    records: list[dict[str, Any]] = []
    in_rows = False
    for line in text.splitlines():
        if not in_rows:
            in_rows = line.startswith("-----")
            continue
        parts = line.split("|")
        if len(parts) != 5:
            continue
        cik, company_name, form_type, filing_date, archive_path = (
            part.strip() for part in parts
        )
        if not (cik and company_name and form_type and filing_date and archive_path):
            continue
        parsed_date = date.fromisoformat(filing_date)
        accession_number = _accession_from_archive_path(archive_path)
        records.append(
            {
                "cik": _normalize_cik(cik),
                "company_name": company_name,
                "form_type": form_type,
                "filing_date": parsed_date,
                "accession_number": accession_number,
                "archive_path": archive_path,
                "complete_submission_url": f"{SEC_ARCHIVES_URL}/{archive_path}",
                "filing_detail_url": _filing_detail_url(cik, accession_number),
            }
        )
    return records


def _quarters_between(start_date: date, end_date: date) -> list[tuple[int, int]]:
    """Return SEC calendar quarters intersecting the date range."""
    quarters = []
    for year in range(start_date.year, end_date.year + 1):
        first_quarter = _quarter(start_date.month) if year == start_date.year else 1
        last_quarter = _quarter(end_date.month) if year == end_date.year else 4
        quarters.extend((year, quarter) for quarter in range(first_quarter, last_quarter + 1))
    return quarters


def _quarter(month: int) -> int:
    return ((month - 1) // 3) + 1


def _matches_form_type(
    value: str,
    form_type: str | None,
    *,
    include_amendments: bool,
) -> bool:
    if not form_type:
        return True
    allowed = {
        form.strip().upper()
        for form in form_type.replace("_", " ").split(",")
        if form.strip()
    }
    current = value.strip().upper()
    if current in allowed:
        return True
    return include_amendments and current.endswith("/A") and current[:-2] in allowed


def _accession_from_archive_path(archive_path: str) -> str | None:
    file_name = archive_path.rsplit("/", 1)[-1]
    if not file_name.endswith(".txt"):
        return None
    accession = file_name[:-4]
    return accession or None


def _filing_detail_url(cik: str, accession_number: str | None) -> str | None:
    if not accession_number:
        return None
    return (
        f"{SEC_ARCHIVES_URL}/edgar/data/{int(cik)}/"
        f"{accession_number.replace('-', '')}/{accession_number}-index.htm"
    )


def _normalize_cik(value: str) -> str:
    digits = "".join(character for character in str(value) if character.isdigit())
    return digits.zfill(10) if digits else value
