"""Test e-Stat fetchers.

ATTRIBUTION: This service uses API functions from e-Stat,
however its contents are not guaranteed by government.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from openbb_estat.models.statistical_data import (
    EstatStatisticalDataFetcher,
)
from openbb_estat.utils.helpers import (
    format_estat_date,
    handle_estat_error,
    validate_stats_params,
)


def test_estat_statistical_data_fetcher():
    """Test EstatStatisticalDataFetcher transform_query."""
    params = {
        "symbol": "0003433219",
        "stats_code": "00200521",
        "area_code": "00000",
    }

    fetcher = EstatStatisticalDataFetcher()
    query = fetcher.transform_query(params)

    assert query.symbol == "0003433219"
    assert query.stats_code == "00200521"
    assert query.area_code == "00000"
    assert query.search_kind == "1"  # Default value
    assert query.data_format == "JSON"  # Default value


@pytest.mark.asyncio
async def test_estat_statistical_data_fetcher_aextract_data():
    """Test EstatStatisticalDataFetcher aextract_data with mocked response."""

    mock_response = {
        "GET_STATS_DATA": {
            "RESULT": {
                "STATUS": 0,
                "ERROR_MSG": "The process has been successfully completed.",
            },
            "STATISTICAL_DATA": {
                "DATA_INF": {
                    "VALUE": [
                        {
                            "@tab": "2020_01",
                            "@cat01": "0",
                            "@area": "00000",
                            "@time": "2020000000",
                            "@unit": "people",
                            "$": "126226568"
                        },
                        {
                            "@tab": "2020_01",
                            "@cat01": "1",
                            "@area": "01000",
                            "@time": "2020000000",
                            "@unit": "people",
                            "$": "5228885"
                        }
                    ]
                }
            }
        }
    }

    params = {"symbol": "0003433219"}
    fetcher = EstatStatisticalDataFetcher()
    query = fetcher.transform_query(params)

    with patch("aiohttp.ClientSession.get") as mock_get:
        # Mock the response object
        mock_response_obj = AsyncMock()
        mock_response_obj.status = 200
        mock_response_obj.json.return_value = mock_response

        # Create a mock context manager for the get() call
        mock_get.return_value.__aenter__ = AsyncMock(return_value=mock_response_obj)
        mock_get.return_value.__aexit__ = AsyncMock(return_value=None)

        data = await fetcher.aextract_data(query, {"api_key": "test_key"})

        assert len(data) == 2
        assert data[0]["$"] == "126226568"
        assert data[1]["$"] == "5228885"


def test_estat_statistical_data_fetcher_transform_data():
    """Test EstatStatisticalDataFetcher transform_data."""

    raw_data = [
        {
            "@tab": "2020_01",
            "@cat01": "Total",
            "@area": "Japan",
            "@time": "2020000000",
            "@unit": "people",
            "$": "126226568"
        },
        {
            "@tab": "2020_01",
            "@cat01": "Male",
            "@area": "Tokyo",
            "@time": "2020000000",
            "@unit": "people",
            "$": "6500000"
        }
    ]

    params = {"symbol": "0003433219"}
    fetcher = EstatStatisticalDataFetcher()
    query = fetcher.transform_query(params)

    result = fetcher.transform_data(query, raw_data)

    assert len(result) == 2
    assert result[0].value == 126226568.0
    assert result[0].date.year == 2020
    assert result[0].unit == "people"
    assert result[1].value == 6500000.0


@pytest.mark.asyncio
async def test_estat_error_handling():
    """Test error handling for e-Stat API errors."""

    mock_error_response = {
        "GET_STATS_DATA": {
            "RESULT": {
                "STATUS": 300,
                "ERROR_MSG": "Statistical data not found.",
            }
        }
    }

    params = {"symbol": "invalid_id"}
    fetcher = EstatStatisticalDataFetcher()
    query = fetcher.transform_query(params)

    with patch("aiohttp.ClientSession.get") as mock_get:
        # Mock the response object
        mock_response_obj = AsyncMock()
        mock_response_obj.status = 200
        mock_response_obj.json.return_value = mock_error_response

        # Create a mock context manager for the get() call
        mock_get.return_value.__aenter__ = AsyncMock(return_value=mock_response_obj)
        mock_get.return_value.__aexit__ = AsyncMock(return_value=None)

        with pytest.raises(Exception) as exc_info:
            await fetcher.aextract_data(query, {"api_key": "test_key"})

        assert "Statistical data not found" in str(exc_info.value)


# Test helper functions
def test_handle_estat_error():
    """Test error handling helper function."""
    # Test known error codes
    assert "Invalid Application ID" in handle_estat_error(100, "Invalid API key")
    assert "Invalid parameter format" in handle_estat_error(200, "Invalid params")
    assert "Statistical data not found" in handle_estat_error(300, "No data")
    assert "Server error" in handle_estat_error(400, "Server issue")

    # Test specific error codes
    assert "Application ID not registered" in handle_estat_error(101, "Auth issue")
    assert "Missing required parameter" in handle_estat_error(201, "Param issue")
    assert "No data available" in handle_estat_error(301, "Data issue")

    # Test unknown error code
    assert "API error (999)" in handle_estat_error(999, "Unknown")


def test_validate_stats_params():
    """Test parameter validation helper."""
    params = {
        "appId": "test",
        "searchKind": "3",  # Invalid, should be corrected
        "metaGetFlg": "X",  # Invalid, should be corrected
        "someParam": None,  # Should be removed
    }

    cleaned = validate_stats_params(params)

    assert cleaned["searchKind"] == "1"  # Corrected
    assert cleaned["metaGetFlg"] == "Y"  # Corrected
    assert "someParam" not in cleaned  # Removed


def test_format_estat_date():
    """Test date formatting helper."""
    # Test various date formats
    assert format_estat_date("2020000000") == "2020-01-01"  # Special format
    assert format_estat_date("2020") == "2020-01-01"  # Year only
    assert format_estat_date("202012") == "2020-12-01"  # Year and month
    assert format_estat_date("") is None  # Empty
    assert format_estat_date("invalid") is None  # Invalid


def test_query_params_validation():
    """Test query parameter validation and defaults."""
    params = {
        "symbol": "0003433219",
        "search_kind": "2",
        "data_format": "XML",
    }

    fetcher = EstatStatisticalDataFetcher()
    query = fetcher.transform_query(params)

    assert query.search_kind == "2"
    assert query.data_format == "XML"
    assert query.explanation_get_flg == "Y"  # Default value


@pytest.mark.asyncio
async def test_missing_api_key_uses_default():
    """Test that missing API key uses default key."""
    params = {"symbol": "0003433219"}
    fetcher = EstatStatisticalDataFetcher()
    query = fetcher.transform_query(params)

    # Mock response to check default key is used
    with patch("aiohttp.ClientSession.get") as mock_get:
        # Mock the response object
        mock_response_obj = AsyncMock()
        mock_response_obj.status = 200
        mock_response_obj.json.return_value = {
            "GET_STATS_DATA": {
                "RESULT": {"STATUS": 0},
                "STATISTICAL_DATA": {"DATA_INF": {"VALUE": []}}
            }
        }

        # Create a mock context manager for the get() call
        mock_get.return_value.__aenter__ = AsyncMock(return_value=mock_response_obj)
        mock_get.return_value.__aexit__ = AsyncMock(return_value=None)

        # Should not raise error, uses default key
        data = await fetcher.aextract_data(query, None)
        assert data == []


@pytest.mark.asyncio
async def test_api_response_with_no_data():
    """Test handling when API returns no statistical data."""
    mock_response = {
        "GET_STATS_DATA": {
            "RESULT": {
                "STATUS": 0,
                "ERROR_MSG": "Success",
            }
            # Missing STATISTICAL_DATA
        }
    }

    params = {"symbol": "test_id"}
    fetcher = EstatStatisticalDataFetcher()
    query = fetcher.transform_query(params)

    with patch("aiohttp.ClientSession.get") as mock_get:
        # Mock the response object
        mock_response_obj = AsyncMock()
        mock_response_obj.status = 200
        mock_response_obj.json.return_value = mock_response

        # Create a mock context manager for the get() call
        mock_get.return_value.__aenter__ = AsyncMock(return_value=mock_response_obj)
        mock_get.return_value.__aexit__ = AsyncMock(return_value=None)

        with pytest.raises(Exception) as exc_info:
            await fetcher.aextract_data(query, {"api_key": "test_key"})

        assert "No statistical data found" in str(exc_info.value)


def test_transform_data_with_edge_cases():
    """Test data transformation with edge cases."""
    raw_data = [
        # Normal data
        {
            "@tab": "2020_01",
            "@cat01": "Total",
            "@area": "Japan",
            "@time": "2020000000",
            "@unit": "people",
            "$": "126226568"
        },
        # Missing value - will be skipped
        {
            "@tab": "2020_02",
            "@time": "2020000000",
            # Missing "$" field
        },
        # Invalid value - will be skipped
        {
            "@tab": "2020_03",
            "@time": "2020000000",
            "$": "invalid_number"
        },
        # Missing date but valid value - will be included with None date
        {
            "@tab": "2020_04",
            "$": "1000000"
            # Missing "@time" field
        },
    ]

    params = {"symbol": "test"}
    fetcher = EstatStatisticalDataFetcher()
    query = fetcher.transform_query(params)

    result = fetcher.transform_data(query, raw_data)

    # Should have 1 valid record (only the 1st with valid data and date)
    # Records with missing values, invalid values, or missing dates are skipped
    # because the SeriesData model requires both date and value to be valid
    assert len(result) == 1
    assert result[0].value == 126226568.0
    assert result[0].date.year == 2020
