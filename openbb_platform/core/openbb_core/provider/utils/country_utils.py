"""Utilities for standardizing country inputs across providers using ISO 3166 standards.

This module provides a Country type that inherits from str for type checker compatibility
while providing full access to ISO 3166 country data via pycountry.

Providers can access alpha_2, alpha_3, name, and numeric properties as needed.

References:
    - ISO 3166-1: https://en.wikipedia.org/wiki/ISO_3166-1
    - pycountry: https://github.com/pycountry/pycountry
"""

from typing import Any

import pycountry


class Country(str):
    """Country string type with full ISO 3166 model access.

    Inherits from str (storing alpha_2 code) for type checker compatibility
    while providing access to the full pycountry object for alpha_2, alpha_3,
    name, and numeric properties.

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

    _country: Any  # pycountry country object

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
        if isinstance(value, Country):
            country_obj = value._country
        else:
            country_obj = cls._lookup_country(value)

        # Create str instance with the alpha_2 code
        instance = super().__new__(cls, country_obj.alpha_2)
        # Store the pycountry object
        instance._country = country_obj
        return instance

    @staticmethod
    def _lookup_country(value: Any) -> Any:
        """Look up a country from various input formats.

        Parameters
        ----------
        value : Any
            Country input to look up.

        Returns
        -------
        pycountry.db.Country
            The pycountry country object.

        Raises
        ------
        ValueError
            If the country cannot be found.
        """
        val = str(value).strip()

        # Convert lower_snake_case to space-separated (e.g., "united_states" -> "united states")
        if "_" in val:
            val = val.replace("_", " ")

        try:
            return pycountry.countries.lookup(val)
        except LookupError as e:
            raise ValueError(
                f"Invalid country: '{value}'. "
                "Accepts ISO 3166-1 alpha-2 codes (e.g., 'US'), "
                "alpha-3 codes (e.g., 'USA'), "
                "or country names (e.g., 'United States', 'united_states')."
            ) from e

    @property
    def alpha_2(self) -> str:
        """ISO 3166-1 alpha-2 code (e.g., 'US')."""
        return self._country.alpha_2

    @property
    def alpha_3(self) -> str:
        """ISO 3166-1 alpha-3 code (e.g., 'USA')."""
        return self._country.alpha_3

    @property
    def name(self) -> str:
        """Full country name (e.g., 'United States')."""
        return self._country.name

    @property
    def numeric(self) -> str | None:
        """ISO 3166-1 numeric code (e.g., '840'), if available."""
        return getattr(self._country, "numeric", None)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> Any:
        """Return the Pydantic core schema for validation."""
        from pydantic_core import core_schema

        return core_schema.no_info_after_validator_function(
            cls,
            core_schema.str_schema(),
        )


# Backwards-compatible alias
CountryParam = Country
