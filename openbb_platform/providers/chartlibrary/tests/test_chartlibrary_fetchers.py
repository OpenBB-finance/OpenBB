"""Tests for the ChartLibrary fetchers."""

from asyncio import run
from datetime import date

import pytest
from openbb_chartlibrary.models.pattern_similarity import (
    CHARTLIBRARY_SEARCH_URL,
    ChartLibraryPatternSimilarityFetcher,
)
from openbb_core.provider.utils.errors import EmptyDataError, UnauthorizedError
from pydantic import ValidationError


class MockResponse:
    """Minimal aiohttp response double."""

    # pylint: disable=too-few-public-methods

    def __init__(self, status: int, payload: dict) -> None:
        """Initialize the response double."""
        self.status = status
        self._payload = payload

    async def json(self) -> dict:
        """Return the JSON payload."""
        return self._payload


def test_chartlibrary_pattern_similarity_fetcher(monkeypatch) -> None:
    """Test the ChartLibrary pattern similarity fetcher."""

    async def mock_extract_data(query, credentials, **kwargs) -> list[dict]:
        _ = (query, credentials, kwargs)
        return [
            {
                "symbol": "MSFT",
                "date": "2024-01-12",
                "distance": 0.12,
                "similarity_rank": 1,
                "return_1d": 0.01,
                "return_3d": -0.02,
                "return_5d": 0.03,
                "return_10d": 0.04,
            }
        ]

    monkeypatch.setattr(
        ChartLibraryPatternSimilarityFetcher,
        "extract_data",
        mock_extract_data,
    )

    params = {
        "symbol": "NVDA",
        "date": date(2025, 1, 15),
        "timeframe": "rth",
        "limit": 10,
    }

    result = ChartLibraryPatternSimilarityFetcher().test(
        params,
        {"chartlibrary_api_key": "MOCK_API_KEY"},
    )

    assert result is None


def test_chartlibrary_pattern_similarity_normalizes_response_fields() -> None:
    """Test ChartLibrary field aliases are normalized into the standard model."""
    query = ChartLibraryPatternSimilarityFetcher.transform_query(
        {
            "symbol": "nvda",
            "date": date(2025, 1, 15),
            "timeframe": "rth",
        }
    )

    results = ChartLibraryPatternSimilarityFetcher.transform_data(
        query,
        [
            {
                "ticker": "msft",
                "match_date": "2024-01-12T15:30:00Z",
                "similarity": 0.12,
                "match_score": 88.0,
                "return_1d": 0.01,
                "return_3d": -0.02,
                "return_5d": 0.03,
                "return_10d": 0.04,
            }
        ],
    )

    assert len(results) == 1
    assert results[0].symbol == "MSFT"
    assert results[0].rank == 1
    assert results[0].distance == 0.12
    assert results[0].similarity_score == 88.0
    assert results[0].timeframe == "rth"
    assert results[0].forward_return_3d == -0.02


def test_chartlibrary_pattern_similarity_rejects_invalid_query_values() -> None:
    """Test provider-specific API constraints are validated locally."""
    with pytest.raises(ValidationError):
        ChartLibraryPatternSimilarityFetcher.transform_query(
            {"symbol": "NVDA", "date": date(2025, 1, 15), "timeframe": "5m"}
        )

    with pytest.raises(ValidationError):
        ChartLibraryPatternSimilarityFetcher.transform_query(
            {"symbol": "NVDA", "date": date(2025, 1, 15), "limit": 51}
        )


def test_chartlibrary_pattern_similarity_extracts_results(monkeypatch) -> None:
    """Test request construction and extraction from a search response."""
    captured: dict[str, object] = {}

    async def mock_amake_request(url: str, **kwargs) -> dict[str, list[dict]]:
        captured["url"] = url
        captured["method"] = kwargs.get("method")
        captured["headers"] = kwargs.get("headers")
        captured["json"] = kwargs.get("json")
        return {"results": [{"symbol": "MSFT", "date": "2024-01-12"}]}

    monkeypatch.setattr(
        "openbb_core.provider.utils.helpers.amake_request",
        mock_amake_request,
    )

    query = ChartLibraryPatternSimilarityFetcher.transform_query(
        {
            "symbol": "nvda",
            "date": date(2025, 1, 15),
            "timeframe": "rth",
            "limit": 10,
        }
    )
    results = run(
        ChartLibraryPatternSimilarityFetcher.aextract_data(
            query,
            {"chartlibrary_api_key": "MOCK_API_KEY"},
        )
    )

    assert results == [{"symbol": "MSFT", "date": "2024-01-12"}]
    assert captured["url"] == CHARTLIBRARY_SEARCH_URL
    assert captured["method"] == "POST"
    assert captured["json"] == {
        "query": "NVDA 2025-01-15",
        "timeframe": "rth",
        "top_n": 10,
    }
    assert captured["headers"] == {
        "Authorization": "Bearer MOCK_API_KEY",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def test_chartlibrary_pattern_similarity_extracts_matches_response(monkeypatch) -> None:
    """Test legacy matches responses are still accepted."""

    async def mock_amake_request(_url: str, **_kwargs) -> dict[str, list[dict]]:
        return {"matches": [{"symbol": "MSFT", "date": "2024-01-12"}]}

    monkeypatch.setattr(
        "openbb_core.provider.utils.helpers.amake_request",
        mock_amake_request,
    )

    query = ChartLibraryPatternSimilarityFetcher.transform_query(
        {"symbol": "NVDA", "date": date(2025, 1, 15)}
    )
    results = run(
        ChartLibraryPatternSimilarityFetcher.aextract_data(
            query,
            {"chartlibrary_api_key": "MOCK_API_KEY"},
        )
    )

    assert results == [{"symbol": "MSFT", "date": "2024-01-12"}]


def test_chartlibrary_pattern_similarity_empty_response_raises(monkeypatch) -> None:
    """Test empty responses raise EmptyDataError."""

    async def mock_amake_request(_url: str, **_kwargs) -> dict[str, list]:
        return {"matches": []}

    monkeypatch.setattr(
        "openbb_core.provider.utils.helpers.amake_request",
        mock_amake_request,
    )

    query = ChartLibraryPatternSimilarityFetcher.transform_query(
        {"symbol": "NVDA", "date": date(2025, 1, 15)}
    )

    with pytest.raises(EmptyDataError):
        run(
            ChartLibraryPatternSimilarityFetcher.aextract_data(
                query,
                {"chartlibrary_api_key": "MOCK_API_KEY"},
            )
        )


def test_chartlibrary_pattern_similarity_unauthorized_response_raises(
    monkeypatch,
) -> None:
    """Test ChartLibrary authorization errors are surfaced."""

    async def mock_amake_request(_url: str, **kwargs) -> None:
        callback = kwargs["response_callback"]
        await callback(MockResponse(401, {"message": "bad api key"}), None)

    monkeypatch.setattr(
        "openbb_core.provider.utils.helpers.amake_request",
        mock_amake_request,
    )

    query = ChartLibraryPatternSimilarityFetcher.transform_query(
        {"symbol": "NVDA", "date": date(2025, 1, 15)}
    )

    with pytest.raises(UnauthorizedError):
        run(
            ChartLibraryPatternSimilarityFetcher.aextract_data(
                query,
                {"chartlibrary_api_key": "MOCK_API_KEY"},
            )
        )
