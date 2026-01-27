"""Utilities for standardizing country inputs across providers using ISO 3166 standards.

This module provides country type handling using pydantic-extra-types for ISO compliance.
Providers can customize serialization via field_serializer to match their API requirements.

References:
    - ISO 3166-1: https://en.wikipedia.org/wiki/ISO_3166-1
    - pydantic-extra-types: https://docs.pydantic.dev/latest/api/pydantic_extra_types_country/
"""

from typing import Annotated, Any

from pydantic import BeforeValidator, PlainSerializer
from pydantic_extra_types.country import CountryAlpha2, CountryShortName

def _normalize_country_input(value: Any) -> str:
    """
    Normalize country input to a format pydantic-extra-types can handle.

    Accepts:
    - ISO 3166-1 alpha-2 codes (e.g., "US", "us")
    - Full country names (e.g., "United States")
    - lower_snake_case names (e.g., "united_states")

    Parameters
    ----------
    value : Any
        The input country value.

    Returns
    -------
    str
        Normalized country string for pydantic validation.
    """
    if value is None:
        return value

    val = str(value).strip()

    # If it's a 2-letter code, uppercase it for CountryAlpha2
    if len(val) == 2:
        return val.upper()

    # Convert lower_snake_case to Title Case (e.g., "united_states" -> "United States")
    if "_" in val:
        val = val.replace("_", " ").title()

    # Try to match as a country name
    return val.title() if val.islower() else val


def _resolve_country_to_alpha2(value: Any) -> CountryAlpha2:
    """
    Resolve various country input formats to CountryAlpha2.

    Parameters
    ----------
    value : Any
        Country input (code, name, or lower_snake_case).

    Returns
    -------
    CountryAlpha2
        Validated ISO 3166-1 alpha-2 country object.

    Raises
    ------
    ValueError
        If the country cannot be resolved.
    """
    if value is None:
        return value

    if isinstance(value, CountryAlpha2):
        return value

    normalized = _normalize_country_input(value)

    # Try as alpha-2 code first
    if len(normalized) == 2:
        try:
            return CountryAlpha2._validate(normalized, None)
        except ValueError:
            pass

    # Try as country name
    try:
        country_name = CountryShortName._validate(normalized, None)
        return CountryAlpha2._validate(country_name.alpha2, None)
    except ValueError as e:
        raise ValueError(
            f"Invalid country: '{value}'. "
            "Accepts ISO 3166-1 alpha-2 codes (e.g., 'US') "
            "or country names (e.g., 'United States', 'united_states')."
        ) from e


# Type alias for country fields that accept flexible input
# Serializes to lowercase alpha-2 code by default
CountryParam = Annotated[
    CountryAlpha2,
    BeforeValidator(_resolve_country_to_alpha2),
    PlainSerializer(lambda x: str(x).lower() if x else None, return_type=str),
]
