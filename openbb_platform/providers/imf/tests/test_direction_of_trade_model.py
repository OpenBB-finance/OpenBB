"""Unit tests for the IMF Direction Of Trade model and fetcher."""

# ruff: noqa: I001

from datetime import date
from typing import Any
from unittest.mock import patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_imf.models.direction_of_trade import (
    ImfDirectionOfTradeData,
    ImfDirectionOfTradeFetcher,
    ImfDirectionOfTradeQueryParams,
)


class TestImfDirectionOfTradeQueryParams:
    """Tests for ``ImfDirectionOfTradeQueryParams._validate_country_fields``."""

    def test_empty_country_raises(self):
        """Empty input raises ``ValueError`` (covers line 57)."""
        with pytest.raises(ValueError, match="Required parameter for IMF provider"):
            ImfDirectionOfTradeQueryParams(country="", counterpart="world")

    def test_all_keyword_returns_wildcard(self):
        """The ``all`` keyword resolves to a ``*`` wildcard (covers line 60)."""
        q = ImfDirectionOfTradeQueryParams(country="all", counterpart="world")
        assert q.country == "*"

    def test_all_with_other_countries_raises(self):
        """An ``all`` token mixed with other tokens raises (covers lines 74-77)."""
        with pytest.raises(
            ValueError, match="'all' cannot be used with other country codes"
        ):
            ImfDirectionOfTradeQueryParams(country="USA,all", counterpart="world")

    def test_all_in_list_returns_wildcard(self):
        """A single-element ``[all]`` list returns ``*`` (covers line 78)."""
        q = ImfDirectionOfTradeQueryParams(country=["all"], counterpart="world")
        assert q.country == "*"

    def test_resolves_multi_country_string(self):
        """Multiple country codes resolve via ``resolve_country_input``."""
        q = ImfDirectionOfTradeQueryParams(country="USA,JPN", counterpart="world")
        assert q.country == "USA,JPN"


class TestImfDirectionOfTradeFetcher:
    """Tests for ``ImfDirectionOfTradeFetcher``."""

    def test_transform_query(self):
        """``transform_query`` builds the query model."""
        q = ImfDirectionOfTradeFetcher.transform_query(
            {"country": "USA", "counterpart": "world"}
        )
        assert isinstance(q, ImfDirectionOfTradeQueryParams)

    @pytest.mark.asyncio
    async def test_aextract_data_passes_limit_through_kwargs(self):
        """``limit`` is forwarded as ``lastNObservations`` (covers line 147)."""
        q = ImfDirectionOfTradeFetcher.transform_query(
            {
                "country": "USA",
                "counterpart": "world",
                "frequency": "annual",
                "direction": "exports",
                "limit": 3,
                "start_date": date(2023, 1, 1),
                "end_date": date(2024, 1, 1),
            }
        )
        recorded: dict[str, Any] = {}

        def fake_imts_query(**kwargs: Any) -> dict[str, Any]:
            recorded.update(kwargs)
            return {"data": [], "metadata": {}}

        with patch(
            "openbb_imf.utils.dot_helpers.imts_query", side_effect=fake_imts_query
        ):
            await ImfDirectionOfTradeFetcher.aextract_data(q, None)
        assert recorded["lastNObservations"] == 3
        assert recorded["start_date"] == "2023-01-01"
        assert recorded["end_date"] == "2024-01-01"
        assert recorded["freq"] == "A"

    @pytest.mark.asyncio
    async def test_aextract_data_wraps_value_error(self):
        """A ``ValueError`` from ``imts_query`` is wrapped in ``OpenBBError`` (covers lines 163-164)."""
        q = ImfDirectionOfTradeFetcher.transform_query(
            {"country": "USA", "counterpart": "world"}
        )
        with patch(
            "openbb_imf.utils.dot_helpers.imts_query",
            side_effect=ValueError("boom"),
        ):
            with pytest.raises(OpenBBError):
                await ImfDirectionOfTradeFetcher.aextract_data(q, None)

    def test_transform_data_empty_raises(self):
        """An empty data payload raises ``EmptyDataError`` (covers line 177)."""
        q = ImfDirectionOfTradeFetcher.transform_query(
            {"country": "USA", "counterpart": "world"}
        )
        with pytest.raises(EmptyDataError):
            ImfDirectionOfTradeFetcher.transform_data(q, {"data": [], "metadata": {}})

    def test_transform_data_aliases_to_model(self):
        """Rows pass through the alias map to ``ImfDirectionOfTradeData``."""
        q = ImfDirectionOfTradeFetcher.transform_query(
            {"country": "USA", "counterpart": "world"}
        )
        record = {
            "TIME_PERIOD": "2024-01-01",
            "COUNTRY": "United States",
            "country_code": "USA",
            "COUNTERPART_COUNTRY": "World",
            "counterpart_country_code": "G001",
            "OBS_VALUE": 123.0,
            "series_id": "IMF_STA_IMTS_X",
            "FREQUENCY": "A",
        }
        out = ImfDirectionOfTradeFetcher.transform_data(
            q, {"data": [record], "metadata": {"foo": 1}}
        )
        assert isinstance(out.result[0], ImfDirectionOfTradeData)
        assert out.result[0].symbol == "IMTS::X"
        assert out.metadata == {"foo": 1}
