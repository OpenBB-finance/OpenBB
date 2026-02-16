"""Utilities for standardizing exchange inputs across providers using ISO 10383 MIC codes.

This module provides an Exchange type that inherits from str for type checker compatibility
while providing full access to ISO 10383 Market Identifier Code (MIC) data via a static dataset.

Providers can access mic, acronym, and name properties as needed.

References:
    - ISO 10383: https://www.iso20022.org/market-identifier-codes
    - MIC Registry (CSV): https://www.iso20022.org/sites/default/files/ISO10383_MIC/ISO10383_MIC.csv
    - Wikipedia: https://en.wikipedia.org/wiki/Market_Identifier_Code
"""

import json
from pathlib import Path
from typing import Any, TypedDict

from pydantic_core import core_schema


class ExchangeData(TypedDict, total=False):
    """Type definition for exchange data dictionary."""

    mic: str
    acronym: str
    name: str


def _load_exchange_data() -> dict[str, ExchangeData]:
    """Load exchange data from JSON and build lookup indices.

    Returns a dict with lookup keys (mic, acronym, name variants) mapping to exchange data.
    """
    data_path = Path(__file__).parent / "exchange_data.json"
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)

    lookup: dict[str, ExchangeData] = {}
    for exchange in data["exchanges"]:
        # Index by MIC (case-insensitive)
        lookup[exchange["mic"].upper()] = exchange
        lookup[exchange["mic"].lower()] = exchange

        # Index by acronym (case-insensitive, first-write-wins to preserve
        # operating MIC priority over segment MICs sharing the same acronym)
        acronym = exchange["acronym"]
        acronym_upper = acronym.upper()
        acronym_lower = acronym.lower()
        if acronym_upper not in lookup:
            lookup[acronym_upper] = exchange
        if acronym_lower not in lookup:
            lookup[acronym_lower] = exchange

        # Index by name (case-insensitive)
        name_lower = exchange["name"].lower()
        if name_lower not in lookup:
            lookup[name_lower] = exchange
        if exchange["name"] not in lookup:
            lookup[exchange["name"]] = exchange

        # Index by snake_case name
        snake_name = (
            name_lower.replace(" ", "_")
            .replace("-", "_")
            .replace(",", "")
            .replace("'", "")
        )
        if snake_name not in lookup:
            lookup[snake_name] = exchange

    return lookup


# Load once at module import
_EXCHANGE_LOOKUP = _load_exchange_data()


class Exchange(str):
    """Exchange string type with full ISO 10383 MIC data access.

    Inherits from str (storing MIC code) for type checker compatibility
    while providing access to mic, acronym, and name properties.

    Accepts:
        - ISO 10383 MIC codes (e.g., "XNAS", "XNYS")
        - Exchange acronyms (e.g., "NASDAQ", "NYSE")
        - Full exchange names (e.g., "New York Stock Exchange")
        - lower_snake_case names (e.g., "new_york_stock_exchange")

    Examples
    --------
    >>> e = Exchange("nasdaq")
    >>> str(e)
    'XNAS'
    >>> e.mic
    'XNAS'
    >>> e.acronym
    'NASDAQ'
    >>> e.name
    'NASDAQ - ALL MARKETS'
    """

    _exchange_data: ExchangeData

    def __new__(cls, value: Any) -> "Exchange":
        """Create a new Exchange instance.

        Parameters
        ----------
        value : Any
            Exchange input (MIC, acronym, name, or lower_snake_case).

        Returns
        -------
        Exchange
            An Exchange instance storing the MIC code as its string value.

        Raises
        ------
        ValueError
            If the exchange cannot be resolved.
        """
        exchange_data = (
            value._exchange_data
            if isinstance(value, Exchange)
            else cls._lookup_exchange(value)
        )

        # Create str instance with the MIC code
        instance = super().__new__(cls, exchange_data["mic"])
        # Store the exchange data dict
        instance._exchange_data = exchange_data
        return instance

    @staticmethod
    def _lookup_exchange(value: Any) -> ExchangeData:
        """Look up an exchange from various input formats.

        Parameters
        ----------
        value : Any
            Exchange input to look up.

        Returns
        -------
        ExchangeData
            The exchange data dictionary with mic, acronym, name.

        Raises
        ------
        ValueError
            If the exchange cannot be found.
        """
        val = str(value).strip()

        # Convert lower_snake_case to lookup key
        if "_" in val:
            val = val.replace("_", " ")

        # Try direct lookup
        lookup_key = val.lower()
        if lookup_key in _EXCHANGE_LOOKUP:
            return _EXCHANGE_LOOKUP[lookup_key]

        # Try uppercase (common for MICs)
        if val.upper() in _EXCHANGE_LOOKUP:
            return _EXCHANGE_LOOKUP[val.upper()]

        # Try original case
        if val in _EXCHANGE_LOOKUP:
            return _EXCHANGE_LOOKUP[val]

        raise ValueError(
            f"Invalid exchange: '{value}'. "
            "Accepts ISO 10383 MIC codes (e.g., 'XNAS', 'XNYS'), "
            "acronyms (e.g., 'NASDAQ', 'NYSE'), "
            "or exchange names (e.g., 'New York Stock Exchange')."
        )

    @property
    def mic(self) -> str:
        """ISO 10383 Market Identifier Code (e.g., 'XNAS')."""
        return self._exchange_data["mic"]

    @property
    def acronym(self) -> str:
        """Exchange acronym/short name (e.g., 'NASDAQ')."""
        return self._exchange_data["acronym"]

    @property
    def name(self) -> str:
        """Full exchange name (e.g., 'NASDAQ - ALL MARKETS')."""
        return self._exchange_data["name"]

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: Any) -> Any:
        """Return the Pydantic core schema for validation."""
        return core_schema.no_info_after_validator_function(
            cls,
            core_schema.str_schema(),
        )


# Backwards-compatible alias
ExchangeParam = Exchange
