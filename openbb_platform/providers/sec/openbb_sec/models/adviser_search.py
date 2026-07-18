"""SEC investment adviser firm and individual searches."""

from __future__ import annotations

from datetime import date
from html import unescape
from json import JSONDecodeError, loads
from typing import Literal
from urllib.parse import urlencode

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_sec.utils.definitions import HEADERS

IAPD_SEARCH_URL = "https://api.adviserinfo.sec.gov/search"
_CACHE_SECONDS = 24 * 60 * 60
_IAPD_RESULT_LIMIT = 100
_MATCHED_NAME_KEY = "_matched_name"


class _AdviserSearchQueryParams(QueryParams):
    """Shared IAPD adviser search query."""

    query: str = Field(
        description="Name or CRD number to search for.",
        min_length=1,
    )
    limit: int = Field(
        default=20,
        description="Maximum number of matching firms or individuals to return.",
        ge=1,
        le=_IAPD_RESULT_LIMIT,
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use cached SEC responses.",
    )

    @field_validator("query")
    @classmethod
    def normalize_query(cls, value: str) -> str:
        """Strip search text and reject whitespace-only queries."""
        value = value.strip()
        if not value:
            raise ValueError("query must not be blank")
        return value


class SecAdviserFirmsQueryParams(_AdviserSearchQueryParams):
    """SEC investment adviser firm search query."""

    query: str = Field(
        description="Firm name, CRD number, or SEC number to search for.",
        min_length=1,
    )


class SecAdviserFirmsData(Data):
    """SEC investment adviser firm search result."""

    crd: str = Field(
        description="Central Registration Depository (CRD) number.",
    )
    sec_number: str | None = Field(
        default=None,
        description="SEC investment adviser number.",
    )
    name: str = Field(
        description="Investment adviser firm name.",
    )
    matched_name: str | None = Field(
        default=None,
        description="Alias that matched the query when different from the firm name.",
    )
    status: str | None = Field(
        default=None,
        description="Investment adviser registration status.",
    )
    branch_count: int | None = Field(
        default=None,
        description="Number of branches associated with the firm.",
    )
    address_line_1: str | None = Field(
        default=None,
        description="First line of the firm's office address.",
    )
    address_line_2: str | None = Field(
        default=None,
        description="Second line of the firm's office address.",
    )
    city: str | None = Field(
        default=None,
        description="Office city.",
    )
    state: str | None = Field(
        default=None,
        description="Office state or region.",
    )
    postal_code: str | None = Field(
        default=None,
        description="Office postal code.",
    )
    country: str | None = Field(
        default=None,
        description="Office country.",
    )


class SecAdviserFirmsFetcher(
    Fetcher[
        SecAdviserFirmsQueryParams,
        list[SecAdviserFirmsData],
    ]
):
    """SEC investment adviser firm search fetcher."""

    @staticmethod
    def transform_query(params: dict[str, object]) -> SecAdviserFirmsQueryParams:
        """Transform query parameters."""
        return SecAdviserFirmsQueryParams.model_validate(params)

    @staticmethod
    async def aextract_data(
        query: SecAdviserFirmsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: object,
    ) -> list[dict[str, object]]:
        """Search IAPD for investment adviser firms."""
        sources = await _search_iapd("firm", query)
        records = [
            record for source in sources if (record := _firm_record(source)) is not None
        ]
        if not records:
            raise EmptyDataError(
                f"No investment adviser firms were found for '{query.query}'."
            )
        return records[: query.limit]

    @staticmethod
    def transform_data(
        query: SecAdviserFirmsQueryParams,
        data: list[dict[str, object]],
        **kwargs: object,
    ) -> list[SecAdviserFirmsData]:
        """Transform raw records to the public model."""
        return [SecAdviserFirmsData.model_validate(record) for record in data]


class SecAdviserIndividualsQueryParams(_AdviserSearchQueryParams):
    """SEC investment adviser individual search query."""

    query: str = Field(
        description="Individual name or CRD number to search for.",
        min_length=1,
    )


class SecAdviserIndividualsData(Data):
    """SEC adviser individual and current-employer search result."""

    crd: str = Field(
        description="Central Registration Depository (CRD) number.",
    )
    first_name: str = Field(
        description="First name.",
    )
    middle_name: str | None = Field(
        default=None,
        description="Middle name.",
    )
    last_name: str = Field(
        description="Last name.",
    )
    status: str = Field(
        description="Investment adviser registration status.",
    )
    broker_dealer_status: str | None = Field(
        default=None,
        description="Broker-dealer registration status.",
    )
    industry_start_date: date | None = Field(
        default=None,
        description="Date the individual entered the securities industry.",
    )
    employment_count: int | None = Field(
        default=None,
        description="Number of employments reported by IAPD.",
    )
    finra_registration_count: int | None = Field(
        default=None,
        description="Number of approved FINRA registrations.",
    )
    current_firm_crd: str | None = Field(
        default=None,
        description="CRD number of a current employer.",
    )
    current_firm_name: str | None = Field(
        default=None,
        description="Name of a current employer.",
    )
    current_firm_ia_sec_number: str | None = Field(
        default=None,
        description="Investment adviser SEC number of the current employer.",
    )
    current_firm_bd_sec_number: str | None = Field(
        default=None,
        description="Broker-dealer SEC number of the current employer.",
    )


class SecAdviserIndividualsFetcher(
    Fetcher[
        SecAdviserIndividualsQueryParams,
        list[SecAdviserIndividualsData],
    ]
):
    """SEC investment adviser individual search fetcher."""

    @staticmethod
    def transform_query(params: dict[str, object]) -> SecAdviserIndividualsQueryParams:
        """Transform query parameters."""
        return SecAdviserIndividualsQueryParams.model_validate(params)

    @staticmethod
    async def aextract_data(
        query: SecAdviserIndividualsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: object,
    ) -> list[dict[str, object]]:
        """Search IAPD for investment adviser individuals."""
        sources = await _search_iapd("individual", query)
        records: list[dict[str, object]] = []
        matches = 0
        for source in sources:
            individual_records = _individual_records(source)
            if not individual_records:
                continue
            records.extend(individual_records)
            matches += 1
            if matches == query.limit:
                break
        if not records:
            raise EmptyDataError(
                f"No investment adviser individuals were found for '{query.query}'."
            )
        return records

    @staticmethod
    def transform_data(
        query: SecAdviserIndividualsQueryParams,
        data: list[dict[str, object]],
        **kwargs: object,
    ) -> list[SecAdviserIndividualsData]:
        """Transform raw records to the public model."""
        return [SecAdviserIndividualsData.model_validate(record) for record in data]


async def _search_iapd(
    entity: Literal["firm", "individual"],
    query: _AdviserSearchQueryParams,
) -> list[dict[str, object]]:
    """Return validated IAPD search source objects."""
    from openbb_sec.utils.cache import cached_request

    url = (
        f"{IAPD_SEARCH_URL}/{entity}?"
        f"{urlencode({'query': query.query, 'nrows': _IAPD_RESULT_LIMIT})}"
    )
    payload = await cached_request(
        url,
        headers=HEADERS,
        use_cache=query.use_cache,
        expire=_CACHE_SECONDS,
    )
    return _parse_iapd_sources(payload)


def _parse_iapd_sources(payload: object) -> list[dict[str, object]]:
    """Validate an IAPD response and return its source objects."""
    payload = _string_dict(
        payload,
        "Invalid IAPD search response: expected a JSON object.",
    )

    error_code = _clean_text(payload.get("errorCode"))
    if error_code is not None:
        error_message = _clean_text(payload.get("errorMessage")) or "Unknown error"
        raise OpenBBError(
            f"IAPD search failed with error {error_code}: {error_message}"
        )

    hits_container = _string_dict(
        payload.get("hits"),
        "Invalid IAPD search response: missing the hits object.",
    )
    hits = hits_container.get("hits")
    if not isinstance(hits, list):
        raise OpenBBError(
            "Invalid IAPD search response: expected hits.hits to be a list."
        )

    sources: list[dict[str, object]] = []
    for hit in hits:
        hit_record = _string_dict(
            hit,
            "Invalid IAPD search response: each hit must be an object.",
        )
        sources.append(
            _string_dict(
                hit_record.get("_source"),
                "Invalid IAPD search response: each hit must contain a source object.",
            )
        )
        matched_name = _matched_firm_name(hit_record.get("highlight"))
        if matched_name is not None:
            sources[-1][_MATCHED_NAME_KEY] = matched_name
    return sources


def _firm_record(source: dict[str, object]) -> dict[str, object] | None:
    """Normalize one IAPD investment adviser firm hit."""
    sec_number = _clean_text(source.get("firm_ia_full_sec_number"))
    status = _clean_text(source.get("firm_ia_scope"))
    if sec_number is None and status is None:
        return None

    crd = _required_text(source.get("firm_source_id"), "firm CRD")
    name = _required_text(source.get("firm_name"), "firm name")
    matched_name = _clean_text(source.get(_MATCHED_NAME_KEY))
    if matched_name is not None and matched_name.casefold() == name.casefold():
        matched_name = None
    address_details = _address_details(source.get("firm_ia_address_details"))
    office_value = address_details.get("officeAddress")
    office = (
        {}
        if office_value is None
        else _string_dict(
            office_value,
            "Invalid IAPD search response: firm office address must be an object.",
        )
    )

    return {
        "crd": crd,
        "sec_number": sec_number,
        "name": name,
        "matched_name": matched_name,
        "status": status,
        "branch_count": _clean_int(source.get("firm_branches_count")),
        "address_line_1": _clean_text(office.get("street1")),
        "address_line_2": _clean_text(office.get("street2")),
        "city": _clean_text(office.get("city")),
        "state": _clean_text(office.get("state")),
        "postal_code": _clean_text(office.get("postalCode")),
        "country": _clean_text(office.get("country")),
    }


def _individual_records(source: dict[str, object]) -> list[dict[str, object]]:
    """Normalize one IAPD investment adviser individual hit."""
    status = _clean_text(source.get("ind_ia_scope"))
    if status is None or status.casefold() == "notinscope":
        return []

    record: dict[str, object] = {
        "crd": _required_text(source.get("ind_source_id"), "individual CRD"),
        "first_name": _required_text(source.get("ind_firstname"), "first name"),
        "middle_name": _clean_text(source.get("ind_middlename")),
        "last_name": _required_text(source.get("ind_lastname"), "last name"),
        "status": status,
        "broker_dealer_status": _clean_text(source.get("ind_bc_scope")),
        "industry_start_date": _clean_date(source.get("ind_industry_cal_date_iapd")),
        "employment_count": _clean_int(source.get("ind_employments_count")),
        "finra_registration_count": _clean_int(
            source.get("ind_approved_finra_registration_count")
        ),
    }
    employments = source.get("ind_ia_current_employments")
    if employments is None or employments == []:
        return [record]
    if not isinstance(employments, list):
        raise OpenBBError(
            "Invalid IAPD search response: current employments must be a list."
        )

    records: list[dict[str, object]] = []
    seen_firms: set[tuple[str, str, str | None, str | None]] = set()
    for employment_item in employments:
        employment = _string_dict(
            employment_item,
            "Invalid IAPD search response: current employment must be an object.",
        )
        firm_crd = _required_text(employment.get("firm_id"), "current firm CRD")
        firm_name = _required_text(employment.get("firm_name"), "current firm name")
        firm_ia_sec_number = _clean_text(employment.get("firm_ia_full_sec_number"))
        firm_bd_sec_number = _clean_text(employment.get("firm_bd_full_sec_number"))
        firm_key = (firm_crd, firm_name, firm_ia_sec_number, firm_bd_sec_number)
        if firm_key in seen_firms:
            continue
        seen_firms.add(firm_key)
        records.append(
            record
            | {
                "current_firm_crd": firm_crd,
                "current_firm_name": firm_name,
                "current_firm_ia_sec_number": firm_ia_sec_number,
                "current_firm_bd_sec_number": firm_bd_sec_number,
            }
        )
    return records or [record]


def _matched_firm_name(value: object) -> str | None:
    """Return the firm name or alias highlighted by IAPD."""
    if value is None:
        return None
    highlights = _string_dict(
        value,
        "Invalid IAPD search response: highlight must be an object.",
    )
    for field in ("firm_name", "firm_other_names"):
        matches = highlights.get(field)
        if matches is None:
            continue
        if not isinstance(matches, list) or not matches:
            raise OpenBBError(
                "Invalid IAPD search response: firm name highlights must be a list."
            )
        match = _required_text(matches[0], "highlighted firm name")
        return unescape(match.replace("<em>", "").replace("</em>", ""))
    return None


def _address_details(value: object) -> dict[str, object]:
    """Decode the optional IAPD address object."""
    if value is None or value == "":
        return {}
    if isinstance(value, dict):
        return _string_dict(
            value,
            "Invalid IAPD search response: firm address details must be an object.",
        )
    if not isinstance(value, str):
        raise OpenBBError(
            "Invalid IAPD search response: firm address details must be an object."
        )
    try:
        decoded = loads(value)
    except JSONDecodeError as exc:
        raise OpenBBError(
            "Invalid IAPD search response: firm address details contain invalid JSON."
        ) from exc
    return _string_dict(
        decoded,
        "Invalid IAPD search response: firm address details must be an object.",
    )


def _string_dict(value: object, error_message: str) -> dict[str, object]:
    """Validate an object and retain its string-keyed fields."""
    if not isinstance(value, dict):
        raise OpenBBError(error_message)
    return {key: item for key, item in value.items() if isinstance(key, str)}


def _required_text(value: object, field: str) -> str:
    """Return required text or raise a response error."""
    cleaned = _clean_text(value)
    if cleaned is None:
        raise OpenBBError(
            f"Invalid IAPD search response: adviser hit is missing {field}."
        )
    return cleaned


def _clean_text(value: object) -> str | None:
    """Normalize optional text."""
    if value is None:
        return None
    if not isinstance(value, (str, int)):
        raise OpenBBError("Invalid IAPD search response: expected a scalar text value.")
    cleaned = " ".join(str(value).split())
    return cleaned or None


def _clean_int(value: object) -> int | None:
    """Normalize an optional integer."""
    if value is None or value == "":
        return None
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise OpenBBError("Invalid IAPD search response: expected an integer value.")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise OpenBBError(
            "Invalid IAPD search response: expected an integer value."
        ) from exc


def _clean_date(value: object) -> date | None:
    """Normalize an optional ISO date."""
    cleaned = _clean_text(value)
    if cleaned is None:
        return None
    try:
        return date.fromisoformat(cleaned)
    except ValueError as exc:
        raise OpenBBError(
            "Invalid IAPD search response: expected an ISO date value."
        ) from exc
