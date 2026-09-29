"""Shared helpers for the SEC Investment Adviser Public Disclosure API."""

from __future__ import annotations

from datetime import date, datetime
from json import JSONDecodeError, loads
from urllib.parse import urlencode

from openbb_core.app.model.abstract.error import OpenBBError

from openbb_sec.utils.definitions import HEADERS

IAPD_SEARCH_URL = "https://api.adviserinfo.sec.gov/search"
IAPD_CACHE_SECONDS = 24 * 60 * 60
IAPD_RESULT_LIMIT = 100


async def request_iapd(
    path: str,
    params: dict[str, str | int],
    use_cache: bool,
) -> object:
    """Request JSON from a public IAPD search endpoint."""
    from openbb_sec.utils.cache import cached_request

    query = urlencode(params)
    url = f"{IAPD_SEARCH_URL}/{path}"
    if query:
        url = f"{url}?{query}"
    return await cached_request(
        url,
        headers=HEADERS,
        use_cache=use_cache,
        expire=IAPD_CACHE_SECONDS,
    )


def iapd_hits(
    payload: object, context: str
) -> list[tuple[dict[str, object], dict[str, object]]]:
    """Validate an IAPD response and return source and hit objects."""
    payload = string_dict(
        payload,
        f"Invalid IAPD {context} response: expected a JSON object.",
    )
    error_code = clean_text(payload.get("errorCode"))
    if error_code is not None:
        error_message = clean_text(payload.get("errorMessage")) or "Unknown error"
        raise OpenBBError(
            f"IAPD {context} failed with error {error_code}: {error_message}"
        )

    hits_container = string_dict(
        payload.get("hits"),
        f"Invalid IAPD {context} response: missing the hits object.",
    )
    hits = hits_container.get("hits")
    if not isinstance(hits, list):
        raise OpenBBError(
            f"Invalid IAPD {context} response: expected hits.hits to be a list."
        )

    records: list[tuple[dict[str, object], dict[str, object]]] = []
    for hit in hits:
        hit_record = string_dict(
            hit,
            f"Invalid IAPD {context} response: each hit must be an object.",
        )
        source = string_dict(
            hit_record.get("_source"),
            f"Invalid IAPD {context} response: each hit must contain a source object.",
        )
        records.append((source, hit_record))
    return records


def iapd_sources(payload: object, context: str) -> list[dict[str, object]]:
    """Validate an IAPD response and return its source objects."""
    return [source for source, _ in iapd_hits(payload, context)]


def string_dict(value: object, error_message: str) -> dict[str, object]:
    """Validate an object and retain its string-keyed fields."""
    if not isinstance(value, dict):
        raise OpenBBError(error_message)
    return {key: item for key, item in value.items() if isinstance(key, str)}


def required_text(value: object, field: str, context: str = "search") -> str:
    """Return required IAPD text or raise a response error."""
    cleaned = clean_text(value)
    if cleaned is None:
        raise OpenBBError(
            f"Invalid IAPD {context} response: adviser data is missing {field}."
        )
    return cleaned


def clean_text(value: object) -> str | None:
    """Normalize optional scalar text."""
    if value is None:
        return None
    if not isinstance(value, (str, int)) or isinstance(value, bool):
        raise OpenBBError("Invalid IAPD response: expected a scalar text value.")
    cleaned = " ".join(str(value).split())
    return cleaned or None


def clean_int(value: object) -> int | None:
    """Normalize an optional integer."""
    if value is None or value == "":
        return None
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise OpenBBError("Invalid IAPD response: expected an integer value.")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise OpenBBError("Invalid IAPD response: expected an integer value.") from exc


def clean_date(value: object, *formats: str) -> date | None:
    """Normalize an optional date using the accepted source formats."""
    cleaned = clean_text(value)
    if cleaned is None:
        return None
    for date_format in formats or ("%Y-%m-%d",):
        try:
            return datetime.strptime(cleaned, date_format).date()  # noqa: DTZ007
        except ValueError:
            continue
    raise OpenBBError("Invalid IAPD response: expected a valid date value.")


def embedded_object(value: object, field: str) -> dict[str, object]:
    """Decode a JSON object embedded in an IAPD string field."""
    if value is None or value == "":
        return {}
    if isinstance(value, dict):
        return string_dict(
            value,
            f"Invalid IAPD response: {field} must be an object.",
        )
    if not isinstance(value, str):
        raise OpenBBError(f"Invalid IAPD response: {field} must be an object.")
    try:
        decoded = loads(value)
    except JSONDecodeError as exc:
        raise OpenBBError(f"Invalid IAPD response: invalid JSON in {field}.") from exc
    return string_dict(
        decoded,
        f"Invalid IAPD response: {field} must be an object.",
    )
