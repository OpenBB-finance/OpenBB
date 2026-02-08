"""Utilities for standardizing country inputs across providers using ISO 3166 standards.

This module provides a Country type that inherits from str for type checker compatibility
while providing full access to ISO 3166 country data via a static dataset.

Providers can access alpha_2, alpha_3, name, and numeric properties as needed.

References:
    - ISO 3166-1: https://en.wikipedia.org/wiki/ISO_3166-1
"""

import json
from pathlib import Path
from typing import Any

from pydantic_core import core_schema


def _load_country_data() -> dict[str, dict[str, str]]:
    """Load country data from JSON and build lookup indices.

    Returns a dict with lookup keys (alpha_2, alpha_3, name variants) mapping to country data.
    """
    data_path = Path(__file__).parent / "country_data.json"
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)

    lookup: dict[str, dict[str, str]] = {}
    for country in data["countries"]:
        # Index by alpha_2 (case-insensitive)
        lookup[country["alpha_2"].upper()] = country
        lookup[country["alpha_2"].lower()] = country

        # Index by alpha_3 (case-insensitive)
        lookup[country["alpha_3"].upper()] = country
        lookup[country["alpha_3"].lower()] = country

        # Index by name (case-insensitive)
        name_lower = country["name"].lower()
        lookup[name_lower] = country
        lookup[country["name"]] = country

        # Index by snake_case name
        snake_name = name_lower.replace(" ", "_").replace(",", "").replace("'", "")
        lookup[snake_name] = country

    return lookup


# Load once at module import - no decompression needed, just simple JSON parse
_COUNTRY_LOOKUP = _load_country_data()


class Country(str):
    """Country string type with full ISO 3166 data access.

    Inherits from str (storing alpha_2 code) for type checker compatibility
    while providing access to alpha_2, alpha_3, name, and numeric properties.

    Accepts:
        - ISO 3166-1 alpha-2 codes (e.g., "US", "us")
        - ISO 3166-1 alpha-3 codes (e.g., "USA", "usa")
        - Full country names (e.g., "United States")
        - lower_snake_case names (e.g., "united_states")

    Examples
    --------
    >>> c = Country("united_states")
    >>> str(c)
    'US'
    >>> c.alpha_2
    'US'
    >>> c.alpha_3
    'USA'
    >>> c.name
    'United States'
    """

    _country_data: dict[str, str]

    def __new__(cls, value: Any) -> "Country":
        """Create a new Country instance.

        Parameters
        ----------
        value : Any
            Country input (alpha-2, alpha-3, name, or lower_snake_case).

        Returns
        -------
        Country
            A Country instance storing the alpha_2 code as its string value.

        Raises
        ------
        ValueError
            If the country cannot be resolved.
        """
        country_data = (
            value._country_data
            if isinstance(value, Country)
            else cls._lookup_country(value)
        )

        # Create str instance with the alpha_2 code
        instance = super().__new__(cls, country_data["alpha_2"])
        # Store the country data dict
        instance._country_data = country_data
        return instance

    @staticmethod
    def _lookup_country(value: Any) -> dict[str, str]:
        """Look up a country from various input formats.

        Parameters
        ----------
        value : Any
            Country input to look up.

        Returns
        -------
        dict[str, str]
            The country data dictionary with alpha_2, alpha_3, name, numeric.

        Raises
        ------
        ValueError
            If the country cannot be found.
        """
        val = str(value).strip()

        # Convert lower_snake_case to lookup key
        if "_" in val:
            val = val.replace("_", " ")

        # Try direct lookup
        lookup_key = val.lower()
        if lookup_key in _COUNTRY_LOOKUP:
            return _COUNTRY_LOOKUP[lookup_key]

        # Try original case
        if val in _COUNTRY_LOOKUP:
            return _COUNTRY_LOOKUP[val]

        raise ValueError(
            f"Invalid country: '{value}'. "
            "Accepts ISO 3166-1 alpha-2 codes (e.g., 'US'), "
            "alpha-3 codes (e.g., 'USA'), "
            "or country names (e.g., 'United States', 'united_states')."
        )

    @property
    def alpha_2(self) -> str:
        """ISO 3166-1 alpha-2 code (e.g., 'US')."""
        return self._country_data["alpha_2"]

    @property
    def alpha_3(self) -> str:
        """ISO 3166-1 alpha-3 code (e.g., 'USA')."""
        return self._country_data["alpha_3"]

    @property
    def name(self) -> str:
        """The country's official designation (e.g., 'United States')."""
        return self._country_data["name"]

    @property
    def numeric(self) -> str | None:
        """ISO 3166-1 numeric code (e.g., '840'), if available."""
        return self._country_data.get("numeric")

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: Any) -> Any:
        """Return the Pydantic core schema for validation."""
        return core_schema.no_info_after_validator_function(
            cls,
            core_schema.str_schema(),
        )


# Backwards-compatible alias
CountryParam = Country
