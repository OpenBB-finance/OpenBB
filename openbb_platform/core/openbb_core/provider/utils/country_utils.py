"""Utilities for standardizing country inputs across providers using ISO 3166 standards.

This module provides a Country type that inherits from str for type checker compatibility
while providing full access to ISO 3166 country data via a static dataset.

Providers can access alpha_2, alpha_3, name, numeric, and groups properties as needed.

Supported membership groups:
    - G7: Group of Seven major advanced economies
    - G20: Group of Twenty major economies
    - EU: European Union member states
    - NATO: North Atlantic Treaty Organization members
    - OECD: Organisation for Economic Co-operation and Development members
    - OPEC: Organization of the Petroleum Exporting Countries
    - BRICS: Brazil, Russia, India, China, South Africa (+ 2024 expansion)

References:
    - ISO 3166-1: https://en.wikipedia.org/wiki/ISO_3166-1
    - G7: https://en.wikipedia.org/wiki/G7
    - G20: https://en.wikipedia.org/wiki/G20
    - EU: https://european-union.europa.eu/principles-countries-history/eu-countries_en
    - NATO: https://www.nato.int/en/about-us/organization/nato-member-countries
    - OECD: https://en.wikipedia.org/wiki/OECD
    - OPEC: https://en.wikipedia.org/wiki/OPEC
    - BRICS: https://en.wikipedia.org/wiki/BRICS
"""

import json
import unicodedata
from pathlib import Path
from typing import Any, TypedDict

from pydantic_core import core_schema


class CountryData(TypedDict, total=False):
    """Type definition for country data dictionary."""

    alpha_2: str
    alpha_3: str
    name: str
    numeric: str
    groups: list[str]


_COMMON_ALIASES: dict[str, list[str]] = {
    "TR": ["turkey"],
}


def _strip_accents(text: str) -> str:
    """Strip diacritical marks from text (e.g., Curaçao -> Curacao)."""
    nfd = unicodedata.normalize("NFD", text)
    return "".join(c for c in nfd if not unicodedata.combining(c))


def _load_country_data() -> dict[str, CountryData]:
    """Load country data from JSON and build lookup indices.

    Returns a dict with lookup keys (alpha_2, alpha_3, name variants) mapping to country data.
    """
    data_path = Path(__file__).parent / "country_data.json"
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)

    lookup: dict[str, CountryData] = {}
    for country in data["countries"]:
        lookup[country["alpha_2"].upper()] = country
        lookup[country["alpha_2"].lower()] = country

        lookup[country["alpha_3"].upper()] = country
        lookup[country["alpha_3"].lower()] = country

        name_lower = country["name"].lower()
        lookup[name_lower] = country
        lookup[country["name"]] = country

        ascii_lower = _strip_accents(name_lower)
        if ascii_lower != name_lower:
            lookup[ascii_lower] = country

        for alias in _COMMON_ALIASES.get(country["alpha_2"], []):
            lookup[alias] = country

        snake_name = name_lower.replace(" ", "_").replace(",", "").replace("'", "")
        lookup[snake_name] = country
        ascii_snake = _strip_accents(snake_name)
        if ascii_snake != snake_name:
            lookup[ascii_snake] = country

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
    >>> c.groups
    ['G7', 'G20', 'NATO', 'OECD']
    >>> c.is_member_of("G7")
    True
    """

    _country_data: CountryData

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
    def _lookup_country(value: Any) -> CountryData:
        """Look up a country from various input formats.

        Parameters
        ----------
        value : Any
            Country input to look up.

        Returns
        -------
        CountryData
            The country data dictionary with alpha_2, alpha_3, name, numeric, groups.

        Raises
        ------
        ValueError
            If the country cannot be found.
        """
        val = str(value).strip()

        if "_" in val:
            val = val.replace("_", " ")

        lookup_key = val.lower()
        if lookup_key in _COUNTRY_LOOKUP:
            return _COUNTRY_LOOKUP[lookup_key]

        if val in _COUNTRY_LOOKUP:
            return _COUNTRY_LOOKUP[val]

        ascii_key = _strip_accents(lookup_key)
        if ascii_key in _COUNTRY_LOOKUP:
            return _COUNTRY_LOOKUP[ascii_key]

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

    @property
    def groups(self) -> list[str]:
        """List of membership groups this country belongs to.

        Available groups: G7, G20, EU, NATO, OECD, OPEC, BRICS.

        Examples
        --------
        >>> c = Country("US")
        >>> c.groups
        ['G7', 'G20', 'NATO', 'OECD']
        """
        return self._country_data.get("groups", [])

    def is_member_of(self, group: str) -> bool:
        """Check if country is a member of a specific group.

        Parameters
        ----------
        group : str
            The group to check membership for (e.g., 'G7', 'EU', 'NATO').
            Case-insensitive.

        Returns
        -------
        bool
            True if the country is a member of the group.

        Examples
        --------
        >>> c = Country("Germany")
        >>> c.is_member_of("G7")
        True
        >>> c.is_member_of("OPEC")
        False
        """
        return group.upper() in [g.upper() for g in self.groups]

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: Any) -> Any:
        """Return the Pydantic core schema for validation."""
        return core_schema.no_info_after_validator_function(
            cls,
            core_schema.str_schema(),
        )


# Backwards-compatible alias
CountryParam = Country
