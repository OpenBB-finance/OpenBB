"""Unit tests for Banxico provider fetchers."""

from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from pydantic import ValidationError

from openbb_banxico.models.currency_historical import (
    BanxicoCurrencyHistoricalFetcher,
)


def test_currency_historical_normalizes_supported_symbol():
    """The provider accepts OpenBB's hyphenated currency-pair format."""
    fetcher = BanxicoCurrencyHistoricalFetcher()

    query = fetcher.transform_query(
        {
            "symbol": "usd-mxn",
            "start_date": "2024-01-02",
            "end_date": "2024-01-05",
        }
    )

    assert query.symbol == "USDMXN"
    assert query.start_date == date(2024, 1, 2)
    assert query.end_date == date(2024, 1, 5)


def test_currency_historical_rejects_unsupported_symbol():
    """The initial provider version is intentionally limited to USD/MXN."""
    fetcher = BanxicoCurrencyHistoricalFetcher()

    with pytest.raises(ValidationError, match="only the USDMXN"):
        fetcher.transform_query({"symbol": "EURMXN"})


def test_currency_historical_transforms_banxico_observations():
    """Spanish API keys are mapped to OpenBB's standard price schema."""
    fetcher = BanxicoCurrencyHistoricalFetcher()
    query = fetcher.transform_query(
        {
            "symbol": "USDMXN",
            "start_date": "2024-01-02",
            "end_date": "2024-01-05",
        }
    )

    result = fetcher.transform_data(
        query,
        [
            {"fecha": "02/01/2024", "dato": "17.0297"},
            {"fecha": "03/01/2024", "dato": "17.0492"},
            {"fecha": "04/01/2024", "dato": "17.0458"},
            {"fecha": "05/01/2024", "dato": "16.8987"},
        ],
    )

    assert [(item.date, item.close) for item in result] == [
        (date(2024, 1, 2), 17.0297),
        (date(2024, 1, 3), 17.0492),
        (date(2024, 1, 4), 17.0458),
        (date(2024, 1, 5), 16.8987),
    ]


def test_currency_historical_requires_an_api_token():
    """A missing credential fails before the provider makes a network request."""
    fetcher = BanxicoCurrencyHistoricalFetcher()
    query = fetcher.transform_query({"symbol": "USDMXN"})

    with pytest.raises(OpenBBError, match="banxico_api_key"):
        fetcher.extract_data(query, credentials={})
