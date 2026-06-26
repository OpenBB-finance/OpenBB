"""SEC institutional holdings from Form 13F structured data."""

from __future__ import annotations

from datetime import date
from tempfile import TemporaryDirectory
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, model_validator

from openbb_sec.utils.definitions import HEADERS
from openbb_sec.utils.form_13f_datasets import (
    SEC_13F_DATA_SETS_URL,
    download_13f_data_set,
    extract_13f_data_set_zip,
    parse_13f_data_set_page,
)
from openbb_sec.utils.ratelimit import sec_make_request

_EXTRACTED_PERIOD_CACHE: dict[tuple[str, date | None], Any] = {}
_INDEXED_PERIOD_CACHE: dict[tuple[str, date | None], dict[str, Any]] = {}
_DATA_SETS_PAGE_CACHE: dict[str, list[Any]] = {}


class SecInstitutionalHoldingsQueryParams(QueryParams):
    """SEC institutional holdings query.

    Source: https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets
    """

    period: date = Field(
        description="Calendar quarter end date for one SEC structured 13F period.",
    )
    cik: str | None = Field(
        default=None,
        description="Central Index Key (CIK) for a 13F institutional manager.",
    )
    accession_number: str | None = Field(
        default=None,
        description="SEC accession number for a 13F filing.",
    )
    limit: int | None = Field(
        default=None,
        description="Maximum number of holding rows to return.",
        ge=1,
    )
    use_cache: bool = Field(
        default=True,
        description="Whether or not to use cache for the selected SEC data.",
    )

    @model_validator(mode="after")
    def validate_selector(self) -> SecInstitutionalHoldingsQueryParams:
        """Require a manager or filing selector to avoid full-quarter output."""
        if not self.cik and not self.accession_number:
            raise ValueError("Either cik or accession_number must be provided.")
        return self


class SecInstitutionalHoldingsData(Data):
    """SEC institutional holding row."""

    period_end: date | None = Field(
        default=None,
        description="Calendar quarter end date for the 13F report.",
    )
    accession_number: str | None = Field(
        default=None,
        description="SEC accession number for the 13F filing.",
    )
    manager_cik: str | None = Field(
        default=None,
        description="Central Index Key (CIK) for the institutional manager.",
    )
    manager_name: str | None = Field(
        default=None,
        description="Name of the institutional manager filing Form 13F.",
    )
    issuer: str | None = Field(
        default=None,
        description="Issuer name reported in the information table.",
    )
    cusip: str | None = Field(
        default=None,
        description="CUSIP reported in the information table.",
    )
    value: float | None = Field(
        default=None,
        description="Reported holding value.",
    )
    shares: float | None = Field(
        default=None,
        description="Reported share or principal amount.",
    )
    weight: float | None = Field(
        default=None,
        description="Holding weight within the filing when available.",
    )
    sector: str | None = Field(
        default=None,
        description="Issuer sector when provided by the SEC structured data.",
    )


class SecInstitutionalHoldingsFetcher(
    Fetcher[
        SecInstitutionalHoldingsQueryParams,
        list[SecInstitutionalHoldingsData],
    ]
):
    """SEC institutional holdings fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> SecInstitutionalHoldingsQueryParams:
        """Transform query parameters."""
        return SecInstitutionalHoldingsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecInstitutionalHoldingsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return structured 13F holdings for one requested period."""
        page_url = kwargs.get("page_url", SEC_13F_DATA_SETS_URL)
        session = kwargs.get("session")
        data_sets = _load_data_sets_page(
            page_url,
            session=session,
            use_cache=query.use_cache,
        )
        selected = next(
            (data_set for data_set in data_sets if data_set.period_date == query.period),
            None,
        )
        if selected is None:
            raise EmptyDataError(
                f"No SEC structured 13F data was found for period {query.period}."
            )

        indexed = _load_indexed_period(
            selected,
            session=session,
            use_cache=query.use_cache,
        )
        records = _selected_holding_records(indexed, query)
        return records[: query.limit] if query.limit is not None else records

    @staticmethod
    def transform_data(
        query: SecInstitutionalHoldingsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[SecInstitutionalHoldingsData]:
        """Transform raw data to the model format."""
        return [SecInstitutionalHoldingsData.model_validate(d) for d in data]


def _load_extracted_period(
    data_set: Any,
    *,
    session: Any | None,
    use_cache: bool,
) -> Any:
    """Load one structured 13F period, reusing parsed data within the process."""
    cache_key = (data_set.url, data_set.period_date)
    if use_cache and cache_key in _EXTRACTED_PERIOD_CACHE:
        return _EXTRACTED_PERIOD_CACHE[cache_key]

    with TemporaryDirectory() as temporary_dir:
        zip_path = download_13f_data_set(
            data_set,
            temporary_dir,
            session=session,
            force=not use_cache,
        )
        extracted = extract_13f_data_set_zip(
            zip_path,
            period_date=data_set.period_date,
        )

    if use_cache:
        _EXTRACTED_PERIOD_CACHE.clear()
        _EXTRACTED_PERIOD_CACHE[cache_key] = extracted
    return extracted


def _load_indexed_period(
    data_set: Any,
    *,
    session: Any | None,
    use_cache: bool,
) -> dict[str, Any]:
    """Load and index one structured 13F period by selector fields."""
    cache_key = (data_set.url, data_set.period_date)
    if use_cache and cache_key in _INDEXED_PERIOD_CACHE:
        return _INDEXED_PERIOD_CACHE[cache_key]

    extracted = _load_extracted_period(
        data_set,
        session=session,
        use_cache=use_cache,
    )
    indexed = _index_holding_records(extracted.holdings, period=data_set.period_date)
    if use_cache:
        _INDEXED_PERIOD_CACHE.clear()
        _INDEXED_PERIOD_CACHE[cache_key] = indexed
    return indexed


def _index_holding_records(
    holdings: list[dict[str, Any]],
    *,
    period: date | None,
) -> dict[str, Any]:
    """Normalize and index holding rows for selector lookups."""
    by_cik: dict[str, list[dict[str, Any]]] = {}
    by_accession: dict[str, list[dict[str, Any]]] = {}
    for holding in holdings:
        row = {
            "period_end": holding.get("period_date") or period,
            "accession_number": holding.get("accession_number"),
            "manager_cik": holding.get("cik"),
            "manager_name": holding.get("filer_name"),
            "issuer": holding.get("issuer"),
            "cusip": holding.get("cusip"),
            "value": holding.get("value"),
            "shares": holding.get("shares"),
            "weight": holding.get("weight"),
            "sector": holding.get("sector"),
        }
        if row["manager_cik"]:
            by_cik.setdefault(_normalize_cik(row["manager_cik"]), []).append(row)
        if row["accession_number"]:
            by_accession.setdefault(str(row["accession_number"]), []).append(row)
    return {"by_cik": by_cik, "by_accession": by_accession}


def _selected_holding_records(
    indexed: dict[str, Any],
    query: SecInstitutionalHoldingsQueryParams,
) -> list[dict[str, Any]]:
    """Return indexed records matching the required selector."""
    if query.accession_number:
        return list(indexed["by_accession"].get(query.accession_number, []))
    if query.cik:
        return list(indexed["by_cik"].get(_normalize_cik(query.cik), []))
    return []


def _load_data_sets_page(
    page_url: str,
    *,
    session: Any | None,
    use_cache: bool,
) -> list[Any]:
    """Load the SEC structured 13F dataset listing."""
    if use_cache and page_url in _DATA_SETS_PAGE_CACHE:
        return _DATA_SETS_PAGE_CACHE[page_url]

    request_kwargs: dict[str, Any] = {"headers": HEADERS}
    if session is not None:
        request_kwargs["session"] = session
    response = sec_make_request(page_url, **request_kwargs)
    response.raise_for_status()
    data_sets = parse_13f_data_set_page(response.text, base_url=page_url)
    if use_cache:
        _DATA_SETS_PAGE_CACHE.clear()
        _DATA_SETS_PAGE_CACHE[page_url] = data_sets
    return data_sets


def _normalize_cik(value: Any) -> str:
    """Normalize a CIK for comparison while preserving display values."""
    normalized = str(value or "").strip()
    return normalized.lstrip("0") or normalized
