{%- set provider_class = cookiecutter.provider_name.replace('_', ' ').title().replace(' ', '') -%}
"""Tests for the {{ cookiecutter.provider_name }} provider."""

import asyncio

from {{ cookiecutter.package_name }}.providers.{{ cookiecutter.provider_name }} import (
    {{ cookiecutter.provider_name }}_provider,
)
from {{ cookiecutter.package_name }}.providers.{{ cookiecutter.provider_name }}.models.equity_historical import (
    {{ provider_class }}EquityHistoricalFetcher,
)
from {{ cookiecutter.package_name }}.providers.{{ cookiecutter.provider_name }}.models.example import (
    ExampleFetcher,
)


class TestProvider:
    """The provider registers every fetcher."""

    def test_fetcher_dict(self):
        assert {{ cookiecutter.provider_name }}_provider.fetcher_dict == {
            "EquityHistorical": {{ provider_class }}EquityHistoricalFetcher,
            "Example": ExampleFetcher,
        }


class TestExampleFetcher:
    """The example fetcher maps the raw columns onto the data model."""

    def test_fetcher(self):
        ExampleFetcher.test({"symbol": "AAPL"})

    def test_rows(self):
        rows = asyncio.run(ExampleFetcher.fetch_data({"symbol": "AAPL"}))
        assert [row.model_dump() for row in rows] == [
            {
                "symbol": "AAPL",
                "date": "2023-08-23",
                "open": 2.0,
                "high": 5.0,
                "low": 1.0,
                "close": 4.0,
                "volume": 5.0,
            },
            {
                "symbol": "AAPL",
                "date": "2023-08-24",
                "open": 4.0,
                "high": 7.0,
                "low": 3.0,
                "close": 6.0,
                "volume": 10.0,
            },
        ]


class TestEquityHistoricalFetcher:
    """The standard-model fetcher fills the custom field."""

    def test_fetcher(self):
        {{ provider_class }}EquityHistoricalFetcher.test({"symbol": "AAPL"})

    def test_custom_field(self):
        rows = asyncio.run(
            {{ provider_class }}EquityHistoricalFetcher.fetch_data(
                {"symbol": "AAPL", "custom_param": "x"}
            )
        )
        assert [row.custom_field for row in rows] == [
            "x",
            "Data validator replaced None.",
        ]
