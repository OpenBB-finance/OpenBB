{%- set types = cookiecutter.extension_types.split(',') | map('trim') | list -%}
{%- set has_provider = 'provider' in types or 'all' in types -%}
"""Tests for the {{ cookiecutter.router_name }} router."""

import asyncio
{%- if has_provider %}
from unittest.mock import AsyncMock, patch
{%- endif %}

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from {{ cookiecutter.package_name }}.routers import {{ cookiecutter.router_name }} as module


class TestGetExample:
    """``get_example`` returns the symbol details from the response."""

    def test_rejects_non_object_response(self, monkeypatch):
        async def fake_request(url):
            return [{"details": {}}]

        monkeypatch.setattr(module, "amake_request", fake_request)
        with pytest.raises(OpenBBError):
            asyncio.run(module.get_example(symbol="AAPL"))

    def test_results(self, monkeypatch):
        requested: list[str] = []

        async def fake_request(url):
            requested.append(url)
            return {"details": {"symbol": "AAPL"}}

        monkeypatch.setattr(module, "amake_request", fake_request)
        result = asyncio.run(module.get_example(symbol="AAPL"))
        assert result.results == {"symbol": "AAPL"}
        assert requested == [f"{module.SYMBOL_INFO_URL}?symbol=AAPL"]


class TestPostExample:
    """``post_example`` measures the quote."""

    def test_results(self):
        result = asyncio.run(
            module.post_example(module.QuoteQueryParams(bid=1.0, ask=3.0, flag=True))
        )
        assert result.results == {"mid": 2.0, "spread": 2.0, "flag": True}
{%- if has_provider %}


class TestModelCommands:
    """Model commands delegate to ``OBBject.from_query``."""

    @pytest.mark.parametrize("command", [module.model_example, module.candles])
    def test_delegates_to_query(self, command):
        sentinel = object()
        with (
            patch.object(module, "OBBject") as obbject,
            patch.object(module, "Query") as query,
        ):
            obbject.from_query = AsyncMock(return_value=sentinel)
            result = asyncio.run(
                command(
                    cc=None,
                    provider_choices=None,
                    standard_params=None,
                    extra_params=None,
                )
            )
        assert result is sentinel
        query.assert_called_once()
{%- endif %}
