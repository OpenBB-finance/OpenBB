"""SEC investment adviser firm and individual searches."""

from __future__ import annotations

from datetime import date
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
    iapd_sources,
    request_iapd,
    required_text,
    string_dict,
)


class SecAdviserSearchQueryParams(QueryParams):
    """SEC investment adviser search query."""

    query: str = Field(
        description="Firm or individual name or CRD number to search for.",
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
        SecAdviserSearchQueryParams,
        list[SecAdviserFirmsData],
    ]
):
    """SEC investment adviser firm search fetcher."""

    @staticmethod
    def transform_query(params: dict[str, object]) -> SecAdviserSearchQueryParams:
        """Transform query parameters."""
        return SecAdviserSearchQueryParams.model_validate(params)

    @staticmethod
    async def aextract_data(
        query: SecAdviserSearchQueryParams,
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
        query: SecAdviserSearchQueryParams,
        data: list[dict[str, object]],
        **kwargs: object,
    ) -> list[SecAdviserFirmsData]:
        """Transform raw records to the public model."""
        return [SecAdviserFirmsData.model_validate(record) for record in data]


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
        SecAdviserSearchQueryParams,
        list[SecAdviserIndividualsData],
    ]
):
    """SEC investment adviser individual search fetcher."""

    @staticmethod
    def transform_query(params: dict[str, object]) -> SecAdviserSearchQueryParams:
        """Transform query parameters."""
        return SecAdviserSearchQueryParams.model_validate(params)

    @staticmethod
    async def aextract_data(
        query: SecAdviserSearchQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: object,
    ) -> list[dict[str, object]]:
        """Search IAPD for investment adviser individuals."""
        sources = await _search_iapd("individual", query)
        records: list[dict[str, object]] = []
        for source in sources:
            records.extend(_individual_records(source))
            if len(records) >= query.limit:
                break
        if not records:
            raise EmptyDataError(
                f"No investment adviser individuals were found for '{query.query}'."
            )
        return records[: query.limit]

    @staticmethod
    def transform_data(
        query: SecAdviserSearchQueryParams,
        data: list[dict[str, object]],
        **kwargs: object,
    ) -> list[SecAdviserIndividualsData]:
        """Transform raw records to the public model."""
        return [SecAdviserIndividualsData.model_validate(record) for record in data]


async def _search_iapd(
    entity: Literal["firm", "individual"],
    query: SecAdviserSearchQueryParams,
) -> list[dict[str, object]]:
    """Return validated IAPD search source objects."""
    payload = await request_iapd(
        entity,
        {"query": query.query, "nrows": IAPD_RESULT_LIMIT},
        query.use_cache,
    )
    return iapd_sources(payload, "search")


def _firm_record(source: dict[str, object]) -> dict[str, object] | None:
    """Normalize one IAPD investment adviser firm hit."""
    sec_number = clean_text(source.get("firm_ia_full_sec_number"))
    status = clean_text(source.get("firm_ia_scope"))
    if sec_number is None and status is None:
        return None

    crd = required_text(source.get("firm_source_id"), "firm CRD")
    name = required_text(source.get("firm_name"), "firm name")
    address_details = embedded_object(
        source.get("firm_ia_address_details"),
        "firm address details",
    )
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
        "name": name,
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
