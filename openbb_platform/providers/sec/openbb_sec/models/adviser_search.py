"""SEC investment adviser firm and individual searches."""

from __future__ import annotations

from datetime import date
from html import unescape
from typing import Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_sec.utils.adviser_info import (
    IAPD_RESULT_LIMIT,
    clean_date,
    clean_int,
    clean_text,
    embedded_object,
    iapd_hits,
    request_iapd,
    required_text,
    string_dict,
)

_MATCHED_NAME_KEY = "_matched_name"
_MATCHED_NAME_TYPE_KEY = "_matched_name_type"
_MATCHED_CRD_KEY = "_matched_crd"
_MATCHED_STATUS_KEY = "_matched_status"

SecRegistrationType = Literal[
    "SEC Registered",
    "SEC Exempt Reporting Adviser",
]
FirmMatchedNameType = Literal["Alternate Name", "Relying Adviser"]


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
        le=IAPD_RESULT_LIMIT,
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
    sec_registration_type: SecRegistrationType | None = Field(
        default=None,
        description="Registration category identified by the SEC adviser number.",
    )
    name: str = Field(
        description="Investment adviser firm name.",
    )
    matched_name: str | None = Field(
        default=None,
        description="Alternate or relying-adviser name that matched the query.",
    )
    matched_name_type: FirmMatchedNameType | None = Field(
        default=None,
        description="Relationship of the matched name to the returned firm.",
    )
    matched_crd: str | None = Field(
        default=None,
        description="CRD number of the matched relying adviser.",
    )
    matched_status: str | None = Field(
        default=None,
        description="Registration status of the matched relying adviser.",
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
    suffix: str | None = Field(
        default=None,
        description="Name suffix.",
    )
    matched_name: str | None = Field(
        default=None,
        description="Alternate name that matched the query.",
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
    industry_days: int | None = Field(
        default=None,
        description="Number of securities-industry days reported by IAPD.",
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
    payload = await request_iapd(
        entity,
        {"query": query.query, "nrows": IAPD_RESULT_LIMIT},
        query.use_cache,
    )
    return _parse_iapd_sources(payload, entity=entity, query=query.query)


def _parse_iapd_sources(
    payload: object,
    entity: Literal["firm", "individual"] = "firm",
    query: str = "",
) -> list[dict[str, object]]:
    """Validate an IAPD response and return its source objects."""
    hits = iapd_hits(payload, "search")
    sources = [source for source, _ in hits]
    for source, hit_record in hits:
        if entity == "firm":
            matched = _matched_firm_details(source, hit_record.get("highlight"), query)
            if matched is not None:
                matched_name, matched_type, matched_crd, matched_status = matched
                source[_MATCHED_NAME_KEY] = matched_name
                source[_MATCHED_NAME_TYPE_KEY] = matched_type
                source[_MATCHED_CRD_KEY] = matched_crd
                source[_MATCHED_STATUS_KEY] = matched_status
        else:
            matched_name = _matched_individual_name(
                source, hit_record.get("highlight"), query
            )
            if matched_name is not None:
                source[_MATCHED_NAME_KEY] = matched_name
    return sources


def _firm_record(source: dict[str, object]) -> dict[str, object] | None:
    """Normalize one IAPD investment adviser firm hit."""
    sec_number = clean_text(source.get("firm_ia_full_sec_number"))
    status = clean_text(source.get("firm_ia_scope"))
    if sec_number is None and status is None:
        return None

    crd = required_text(source.get("firm_source_id"), "firm CRD")
    name = required_text(source.get("firm_name"), "firm name")
    matched_name = clean_text(source.get(_MATCHED_NAME_KEY))
    if matched_name is not None and matched_name.casefold() == name.casefold():
        matched_name = None
    address_details = _address_details(source.get("firm_ia_address_details"))
    office_value = address_details.get("officeAddress")
    office = (
        {}
        if office_value is None
        else string_dict(
            office_value,
            "Invalid IAPD search response: firm office address must be an object.",
        )
    )

    return {
        "crd": crd,
        "sec_number": sec_number,
        "sec_registration_type": _sec_registration_type(sec_number),
        "name": name,
        "matched_name": matched_name,
        "matched_name_type": clean_text(source.get(_MATCHED_NAME_TYPE_KEY)),
        "matched_crd": clean_text(source.get(_MATCHED_CRD_KEY)),
        "matched_status": clean_text(source.get(_MATCHED_STATUS_KEY)),
        "status": status,
        "branch_count": clean_int(source.get("firm_branches_count")),
        "address_line_1": clean_text(office.get("street1")),
        "address_line_2": clean_text(office.get("street2")),
        "city": clean_text(office.get("city")),
        "state": clean_text(office.get("state")),
        "postal_code": clean_text(office.get("postalCode")),
        "country": clean_text(office.get("country")),
    }


def _individual_records(source: dict[str, object]) -> list[dict[str, object]]:
    """Normalize one IAPD investment adviser individual hit."""
    status = clean_text(source.get("ind_ia_scope"))
    if status is None or status.casefold() == "notinscope":
        return []

    record: dict[str, object] = {
        "crd": required_text(source.get("ind_source_id"), "individual CRD"),
        "first_name": required_text(source.get("ind_firstname"), "first name"),
        "middle_name": clean_text(source.get("ind_middlename")),
        "last_name": required_text(source.get("ind_lastname"), "last name"),
        "suffix": clean_text(source.get("ind_namesuffix")),
        "matched_name": clean_text(source.get(_MATCHED_NAME_KEY)),
        "status": status,
        "broker_dealer_status": clean_text(source.get("ind_bc_scope")),
        "industry_start_date": clean_date(source.get("ind_industry_cal_date_iapd")),
        "industry_days": clean_int(source.get("ind_industry_days_iapd")),
        "employment_count": clean_int(source.get("ind_employments_count")),
        "finra_registration_count": clean_int(
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
        employment = string_dict(
            employment_item,
            "Invalid IAPD search response: current employment must be an object.",
        )
        firm_crd = required_text(employment.get("firm_id"), "current firm CRD")
        firm_name = required_text(employment.get("firm_name"), "current firm name")
        firm_ia_sec_number = clean_text(employment.get("firm_ia_full_sec_number"))
        firm_bd_sec_number = clean_text(employment.get("firm_bd_full_sec_number"))
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


def _matched_firm_details(
    source: dict[str, object],
    value: object,
    query: str,
) -> tuple[str, FirmMatchedNameType, str | None, str | None] | None:
    """Return details for an alternate firm name that caused a match."""
    if value is None:
        return None
    highlights = string_dict(
        value,
        "Invalid IAPD search response: highlight must be an object.",
    )
    candidates = _highlighted_names(
        highlights,
        (
            ("firm_name", None),
            ("firm_relying_advisors.name", "Relying Adviser"),
            ("firm_other_names", "Alternate Name"),
        ),
    )
    if not candidates:
        return None
    matched_name, matched_type = max(
        candidates,
        key=lambda candidate: _name_match_score(candidate[0], query),
    )
    firm_name = required_text(source.get("firm_name"), "firm name")
    if matched_type is None or matched_name.casefold() == firm_name.casefold():
        return None

    relying_name = _without_relying_suffix(matched_name)
    if relying_name != matched_name:
        matched_type = "Relying Adviser"
    if matched_type != "Relying Adviser":
        return matched_name, matched_type, None, None

    for relying in _optional_object_list(
        source.get("firm_relying_advisors"), "relying advisers"
    ):
        name = required_text(relying.get("name"), "relying adviser name")
        if _without_relying_suffix(name).casefold() == relying_name.casefold():
            return (
                matched_name,
                matched_type,
                clean_text(relying.get("firmId")),
                clean_text(relying.get("status")),
            )
    return matched_name, matched_type, None, None


def _matched_individual_name(
    source: dict[str, object],
    value: object,
    query: str,
) -> str | None:
    """Return the alternate individual name that caused a match."""
    if value is None:
        return None
    highlights = string_dict(
        value,
        "Invalid IAPD search response: highlight must be an object.",
    )
    candidates = _highlighted_names(
        highlights,
        (("ind_other_names", "Alternate Name"),),
    )
    if not candidates:
        return None
    matched_name = max(
        candidates,
        key=lambda candidate: _name_match_score(candidate[0], query),
    )[0]
    canonical_name = " ".join(
        part
        for part in (
            clean_text(source.get("ind_firstname")),
            clean_text(source.get("ind_middlename")),
            clean_text(source.get("ind_lastname")),
            clean_text(source.get("ind_namesuffix")),
        )
        if part is not None
    )
    return (
        None if matched_name.casefold() == canonical_name.casefold() else matched_name
    )


def _highlighted_names(
    highlights: dict[str, object],
    fields: tuple[tuple[str, FirmMatchedNameType | None], ...],
) -> list[tuple[str, FirmMatchedNameType | None]]:
    """Return cleaned name highlights with their relationship type."""
    candidates: list[tuple[str, FirmMatchedNameType | None]] = []
    for field, match_type in fields:
        matches = highlights.get(field)
        if matches is None:
            continue
        if not isinstance(matches, list) or not matches:
            raise OpenBBError(
                "Invalid IAPD search response: name highlights must be a non-empty list."
            )
        for value in matches:
            match = required_text(value, "highlighted name")
            candidates.append(
                (unescape(match.replace("<em>", "").replace("</em>", "")), match_type)
            )
    return candidates


def _name_match_score(name: str, query: str) -> tuple[int, int]:
    """Rank an IAPD highlight by how directly it represents the query."""
    normalized_name = _without_relying_suffix(name).casefold()
    normalized_query = " ".join(query.casefold().split())
    if not normalized_query:
        return 0, -len(normalized_name)
    if normalized_name == normalized_query:
        return 3, -len(normalized_name)
    if normalized_query in normalized_name:
        return 2, -len(normalized_name)
    query_tokens = normalized_query.split()
    if query_tokens and all(token in normalized_name for token in query_tokens):
        return 1, -len(normalized_name)
    return 0, -len(normalized_name)


def _without_relying_suffix(name: str) -> str:
    """Remove the IAPD display suffix used for relying advisers."""
    suffix = " (RELYING ADVISER)"
    return name[: -len(suffix)] if name.upper().endswith(suffix) else name


def _optional_object_list(value: object, field: str) -> list[dict[str, object]]:
    """Validate an optional list of IAPD objects."""
    if value is None:
        return []
    if not isinstance(value, list):
        raise OpenBBError(f"Invalid IAPD search response: {field} must be a list.")
    return [
        string_dict(
            item,
            f"Invalid IAPD search response: {field} entries must be objects.",
        )
        for item in value
    ]


def _sec_registration_type(sec_number: str | None) -> SecRegistrationType | None:
    """Classify the SEC registration from its official number prefix."""
    if sec_number is None:
        return None
    prefix = sec_number.partition("-")[0]
    if prefix == "801":
        return "SEC Registered"
    if prefix == "802":
        return "SEC Exempt Reporting Adviser"
    raise OpenBBError(
        f"Invalid IAPD search response: unknown SEC adviser number prefix {prefix}."
    )


def _address_details(value: object) -> dict[str, object]:
    """Decode the optional IAPD address object."""
    return embedded_object(value, "firm address details")
