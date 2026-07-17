"""SEC investment adviser firm search."""

from __future__ import annotations

from json import JSONDecodeError, loads
from urllib.parse import urlencode

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_sec.utils.definitions import HEADERS

IAPD_FIRM_SEARCH_URL = "https://api.adviserinfo.sec.gov/search/firm"
_CACHE_SECONDS = 24 * 60 * 60
_IAPD_RESULT_LIMIT = 100


class SecInvestmentAdvisersQueryParams(QueryParams):
    """SEC investment adviser firm search query."""

    query: str = Field(
        description="Firm name, CRD number, or SEC number to search for.",
        min_length=1,
    )
    limit: int = Field(
        default=20,
        description="Maximum number of adviser firms to return.",
        ge=1,
        le=100,
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


class SecInvestmentAdvisersData(Data):
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


class SecInvestmentAdvisersFetcher(
    Fetcher[
        SecInvestmentAdvisersQueryParams,
        list[SecInvestmentAdvisersData],
    ]
):
    """SEC investment adviser firm search fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, object],
    ) -> SecInvestmentAdvisersQueryParams:
        """Transform query parameters."""
        return SecInvestmentAdvisersQueryParams.model_validate(params)

    @staticmethod
    async def aextract_data(
        query: SecInvestmentAdvisersQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: object,
    ) -> list[dict[str, object]]:
        """Search SEC IAPD for investment adviser firms."""
        from openbb_sec.utils.cache import cached_request

        url = (
            f"{IAPD_FIRM_SEARCH_URL}?"
            f"{urlencode({'query': query.query, 'nrows': _IAPD_RESULT_LIMIT})}"
        )
        payload = await cached_request(
            url,
            headers=HEADERS,
            use_cache=query.use_cache,
            expire=_CACHE_SECONDS,
        )
        records = _parse_iapd_records(payload)
        if not records:
            raise EmptyDataError(
                f"No investment adviser firms were found for '{query.query}'."
            )
        return records[: query.limit]

    @staticmethod
    def transform_data(
        query: SecInvestmentAdvisersQueryParams,
        data: list[dict[str, object]],
        **kwargs: object,
    ) -> list[SecInvestmentAdvisersData]:
        """Transform raw records to the public model."""
        return [SecInvestmentAdvisersData.model_validate(record) for record in data]


def _parse_iapd_records(payload: object) -> list[dict[str, object]]:
    """Validate and normalize an IAPD firm search response."""
    payload = _string_dict(
        payload,
        "Invalid IAPD firm search response: expected a JSON object.",
    )

    error_code = _clean_text(payload.get("errorCode"))
    if error_code is not None:
        error_message = _clean_text(payload.get("errorMessage")) or "Unknown error"
        raise OpenBBError(
            f"IAPD firm search failed with error {error_code}: {error_message}"
        )

    hits_container = _string_dict(
        payload.get("hits"),
        "Invalid IAPD firm search response: missing the hits object.",
    )
    hits = hits_container.get("hits")
    if not isinstance(hits, list):
        raise OpenBBError(
            "Invalid IAPD firm search response: expected hits.hits to be a list."
        )

    records: list[dict[str, object]] = []
    for hit in hits:
        hit_record = _string_dict(
            hit,
            "Invalid IAPD firm search response: each hit must be an object.",
        )
        source = _string_dict(
            hit_record.get("_source"),
            "Invalid IAPD firm search response: each hit must contain a source object.",
        )
        record = _iapd_firm_record(source)
        if record is not None:
            records.append(record)
    return records


def _iapd_firm_record(
    source: dict[str, object],
) -> dict[str, object] | None:
    """Normalize one IAPD investment adviser firm hit."""
    sec_number = _clean_text(source.get("firm_ia_full_sec_number"))
    status = _clean_text(source.get("firm_ia_scope"))
    if sec_number is None and status is None:
        return None

    crd = _clean_text(source.get("firm_source_id"))
    name = _clean_text(source.get("firm_name"))
    if crd is None or name is None:
        raise OpenBBError(
            "Invalid IAPD firm search response: an adviser hit is missing its identity."
        )

    address_details = _address_details(source.get("firm_ia_address_details"))
    office_value = address_details.get("officeAddress")
    office = (
        {}
        if office_value is None
        else _string_dict(
            office_value,
            "Invalid IAPD firm search response: firm office address must be an object.",
        )
    )

    return {
        "crd": crd,
        "sec_number": sec_number,
        "name": name,
        "status": status,
        "address_line_1": _clean_text(office.get("street1")),
        "address_line_2": _clean_text(office.get("street2")),
        "city": _clean_text(office.get("city")),
        "state": _clean_text(office.get("state")),
        "postal_code": _clean_text(office.get("postalCode")),
        "country": _clean_text(office.get("country")),
    }


def _address_details(value: object) -> dict[str, object]:
    """Decode the optional IAPD address object."""
    if value is None or value == "":
        return {}
    if isinstance(value, dict):
        return _string_dict(
            value,
            "Invalid IAPD firm search response: firm address details must be an object.",
        )
    if not isinstance(value, str):
        raise OpenBBError(
            "Invalid IAPD firm search response: firm address details must be an object."
        )
    try:
        decoded = loads(value)
    except JSONDecodeError as exc:
        raise OpenBBError(
            "Invalid IAPD firm search response: firm address details contain invalid JSON."
        ) from exc
    if not isinstance(decoded, dict):
        raise OpenBBError(
            "Invalid IAPD firm search response: firm address details must be an object."
        )
    return _string_dict(
        decoded,
        "Invalid IAPD firm search response: firm address details must be an object.",
    )


def _string_dict(value: object, error_message: str) -> dict[str, object]:
    """Validate an object and retain its string-keyed fields."""
    if not isinstance(value, dict):
        raise OpenBBError(error_message)
    return {key: item for key, item in value.items() if isinstance(key, str)}


def _clean_text(value: object) -> str | None:
    """Normalize optional text."""
    if value is None:
        return None
    if not isinstance(value, (str, int)):
        raise OpenBBError(
            "Invalid IAPD firm search response: expected a scalar text value."
        )
    cleaned = " ".join(str(value).split())
    return cleaned or None
