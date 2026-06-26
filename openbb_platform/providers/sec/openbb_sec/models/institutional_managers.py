"""SEC institutional manager records."""

from __future__ import annotations

from datetime import date
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

from openbb_sec.utils.definitions import HEADERS


class SecInstitutionalManagersQueryParams(QueryParams):
    """SEC institutional managers query.

    Source: https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets
    """

    query: str | None = Field(
        default=None,
        description="Search text matched against the manager name.",
    )
    cik: str | None = Field(
        default=None,
        description="Central Index Key (CIK) for a 13F institutional manager.",
    )
    period: date | None = Field(
        default=None,
        description="Calendar quarter end date for the 13F structured data set.",
    )
    limit: int = Field(
        default=100,
        description="Maximum number of manager records to return.",
        ge=1,
    )
    use_cache: bool = Field(
        default=True,
        description="Whether or not to use cache.",
    )


class SecInstitutionalManagersData(Data):
    """SEC institutional manager data."""

    cik: str | None = Field(
        default=None,
        description="Central Index Key (CIK) for the institutional manager.",
    )
    manager_name: str | None = Field(
        default=None,
        description="Name of the institutional manager filing Form 13F.",
    )
    period: date | None = Field(
        default=None,
        description="Calendar quarter end date for the 13F report.",
    )
    accession_number: str | None = Field(
        default=None,
        description="SEC accession number for the 13F filing.",
    )
    filed_date: date | None = Field(
        default=None,
        description="Date the filing was submitted to EDGAR.",
    )
    reported_value: float | None = Field(
        default=None,
        description="Total reported value from the structured 13F holdings table.",
    )
    holdings_count: int | None = Field(
        default=None,
        description="Number of holding rows in the 13F filing.",
    )


class SecInstitutionalManagersFetcher(
    Fetcher[
        SecInstitutionalManagersQueryParams,
        list[SecInstitutionalManagersData],
    ]
):
    """SEC institutional managers fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecInstitutionalManagersQueryParams:
        """Transform query parameters."""
        return SecInstitutionalManagersQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecInstitutionalManagersQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return raw SEC institutional manager records."""
        records = load_institutional_manager_records(
            period=query.period,
            use_cache=query.use_cache,
            **kwargs,
        )
        records = _filter_manager_records(records, query)
        return records[: query.limit]

    @staticmethod
    def transform_data(
        query: SecInstitutionalManagersQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[SecInstitutionalManagersData]:
        """Transform raw data to the model format."""
        return [SecInstitutionalManagersData.model_validate(d) for d in data]


def load_institutional_manager_records(
    *,
    period: date | None = None,
    use_cache: bool = True,
    **kwargs: Any,
) -> list[dict[str, Any]]:
    """Load 13F manager records from SEC structured data sets."""
    from tempfile import TemporaryDirectory

    from openbb_sec.utils.form_13f_datasets import (
        SEC_13F_DATA_SETS_URL,
        download_13f_data_set,
        extract_13f_data_set_zip,
        parse_13f_data_set_page,
    )
    from openbb_sec.utils.ratelimit import sec_make_request

    page_url = kwargs.get("page_url", SEC_13F_DATA_SETS_URL)
    session = kwargs.get("session")
    request_kwargs: dict[str, Any] = {"headers": HEADERS}
    if session is not None:
        request_kwargs["session"] = session
    response = sec_make_request(page_url, **request_kwargs)
    response.raise_for_status()
    data_sets = parse_13f_data_set_page(response.text, base_url=page_url)
    if not data_sets:
        return []

    selected = _select_data_set(data_sets, period)
    if selected is None:
        return []

    with TemporaryDirectory() as temporary_dir:
        zip_path = download_13f_data_set(
            selected,
            temporary_dir,
            session=session,
            force=not use_cache,
        )
        extracted = extract_13f_data_set_zip(zip_path, period_date=selected.period_date)

    totals_by_accession = _reported_values_by_accession(extracted.holdings)
    counts_by_accession = _holding_counts_by_accession(extracted.holdings)
    records: list[dict[str, Any]] = []
    for filer in extracted.filers:
        accession_number = filer.get("accession_number")
        accession_key = str(accession_number) if accession_number else ""
        records.append(
            {
                "cik": filer.get("cik"),
                "manager_name": filer.get("name"),
                "period": filer.get("period_date") or selected.period_date,
                "accession_number": accession_number,
                "filed_date": filer.get("filed_date"),
                "reported_value": totals_by_accession.get(accession_key),
                "holdings_count": counts_by_accession.get(accession_key),
            }
        )
    return records


def _select_data_set(data_sets: list[Any], period: date | None) -> Any | None:
    """Return the requested period data set or the most recent available one."""
    if period is not None:
        return next((item for item in data_sets if item.period_date == period), None)
    with_period = [item for item in data_sets if item.period_date is not None]
    if with_period:
        return max(with_period, key=lambda item: item.period_date)
    return data_sets[0]


def _reported_values_by_accession(holdings: list[dict[str, Any]]) -> dict[str, float]:
    """Sum 13F holding values by filing accession number."""
    totals: dict[str, float] = {}
    for holding in holdings:
        accession_number = holding.get("accession_number")
        value = holding.get("value")
        if not accession_number or value is None:
            continue
        totals[str(accession_number)] = totals.get(str(accession_number), 0.0) + float(
            value
        )
    return totals


def _holding_counts_by_accession(holdings: list[dict[str, Any]]) -> dict[str, int]:
    """Count 13F holding rows by filing accession number."""
    counts: dict[str, int] = {}
    for holding in holdings:
        accession_number = holding.get("accession_number")
        if not accession_number:
            continue
        accession_key = str(accession_number)
        counts[accession_key] = counts.get(accession_key, 0) + 1
    return counts


def _filter_manager_records(
    records: list[dict[str, Any]],
    query: SecInstitutionalManagersQueryParams,
) -> list[dict[str, Any]]:
    """Apply client-side query, CIK, and period filters."""
    filtered = records
    if query.query:
        needle = query.query.casefold()
        filtered = [
            record
            for record in filtered
            if needle in str(record.get("manager_name") or "").casefold()
        ]
    if query.cik:
        cik = _normalize_cik(query.cik)
        filtered = [
            record
            for record in filtered
            if _normalize_cik(record.get("cik")) == cik
        ]
    return filtered


def _normalize_cik(value: Any) -> str:
    """Normalize a CIK for comparison while preserving display values."""
    normalized = str(value or "").strip()
    return normalized.lstrip("0") or normalized
