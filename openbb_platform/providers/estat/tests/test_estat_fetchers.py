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

from openbb_estat.models.search import EstatSearchFetcher
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


# e-Stat Search Tests


def test_estat_search_fetcher_transform_query():
    """Test EstatSearchFetcher transform_query."""
    params = {"query": "population", "limit": 50}

    fetcher = EstatSearchFetcher()
    query = fetcher.transform_query(params)

    assert query.query == "population"
    assert query.limit == 50


def test_estat_search_fetcher_transform_query_defaults():
    """Test EstatSearchFetcher transform_query with defaults."""
    params = {}

    fetcher = EstatSearchFetcher()
    query = fetcher.transform_query(params)

    assert query.query is None
    assert query.limit == 100  # Default value


@pytest.mark.asyncio
async def test_estat_search_fetcher_aextract_data():
    """Test EstatSearchFetcher aextract_data with mocked response."""

    mock_response = {
        "GET_STATS_LIST": {
            "RESULT": {
                "STATUS": 0,
                "ERROR_MSG": "Success",
            },
            "DATALIST_INF": {
                "LIST_INF": [
                    {
                        "STAT_NAME": {
                            "@id": "0003433219",
                            "$": "Population Census 2020",
                        },
                        "STATISTICS_NAME": {
                            "@code": "00200521",
                            "$": "Population Census",
                        },
                        "GOV_ORG": {"$": "Statistics Bureau"},
                        "SURVEY_DATE": "2020-10-01",
                        "OPEN_DATE": "2021-06-25",
                        "SMALL_AREA": "0",
                    },
                    {
                        "STAT_NAME": {
                            "@id": "0003410379",
                            "$": "Consumer Price Index",
                        },
                        "STATISTICS_NAME": {
                            "@code": "00200573",
                            "$": "Consumer Price Index",
                        },
                        "GOV_ORG": {"$": "Statistics Bureau"},
                        "SURVEY_DATE": "2023-12-01",
                        "OPEN_DATE": "2024-01-19",
                        "SMALL_AREA": "0",
                    },
                ]
            },
        }
    }

    params = {"query": "population"}
    fetcher = EstatSearchFetcher()
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
        assert data[0]["STAT_NAME"]["@id"] == "0003433219"
        assert data[1]["STAT_NAME"]["@id"] == "0003410379"


def test_estat_search_fetcher_transform_data():
    """Test EstatSearchFetcher transform_data."""

    raw_data = [
        {
            "STAT_NAME": {
                "@id": "0003433219",
                "$": "Population Census 2020",
            },
            "STATISTICS_NAME": {
                "@code": "00200521",
                "$": "Population Census",
            },
            "GOV_ORG": {"$": "Statistics Bureau"},
            "SURVEY_DATE": "2020-10-01",
            "OPEN_DATE": "2021-06-25",
            "SMALL_AREA": "0",
        }
    ]

    params = {"query": "population"}
    fetcher = EstatSearchFetcher()
    query = fetcher.transform_query(params)

    result = fetcher.transform_data(query, raw_data)

    # Check AnnotatedResult structure
    assert hasattr(result, "result")
    assert hasattr(result, "metadata")

    # Check data
    assert len(result.result) == 1
    assert result.result[0].dataset_id == "0003433219"
    assert result.result[0].title == "Population Census 2020"
    assert result.result[0].stats_code == "00200521"
    assert result.result[0].statistics_name == "Population Census"
    assert result.result[0].gov_org == "Statistics Bureau"

    # Check metadata
    assert "attribution" in result.metadata
    assert "e-Stat" in result.metadata["attribution"]
    assert result.metadata["source"] == "https://www.e-stat.go.jp/"
    assert result.metadata["api_version"] == "3.0"


@pytest.mark.asyncio
async def test_estat_search_error_handling():
    """Test error handling for e-Stat search API errors."""

    mock_error_response = {
        "GET_STATS_LIST": {
            "RESULT": {
                "STATUS": 100,
                "ERROR_MSG": "Invalid Application ID",
            }
        }
    }

    params = {"query": "test"}
    fetcher = EstatSearchFetcher()
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
            await fetcher.aextract_data(query, {"api_key": "invalid_key"})

        assert "Invalid Application ID" in str(exc_info.value)


@pytest.mark.asyncio
async def test_estat_search_empty_query():
    """Test search with no query returns all datasets."""

    mock_response = {
        "GET_STATS_LIST": {
            "RESULT": {"STATUS": 0, "ERROR_MSG": "Success"},
            "DATALIST_INF": {
                "LIST_INF": [
                    {
                        "STAT_NAME": {"@id": "0003433219", "$": "Test Dataset"},
                        "STATISTICS_NAME": {"@code": "00200521", "$": "Test"},
                        "GOV_ORG": {"$": "Test Bureau"},
                    }
                ]
            },
        }
    }

    params = {}  # No query
    fetcher = EstatSearchFetcher()
    query = fetcher.transform_query(params)

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response_obj = AsyncMock()
        mock_response_obj.status = 200
        mock_response_obj.json.return_value = mock_response

        mock_get.return_value.__aenter__ = AsyncMock(return_value=mock_response_obj)
        mock_get.return_value.__aexit__ = AsyncMock(return_value=None)

        data = await fetcher.aextract_data(query, {"api_key": "test_key"})

        assert len(data) == 1


def test_estat_search_metadata_attribution():
    """Test that metadata includes attribution notice."""

    raw_data = [
        {
            "STAT_NAME": {"@id": "123", "$": "Test"},
            "STATISTICS_NAME": {"@code": "001", "$": "Test"},
            "GOV_ORG": {"$": "Test"},
        }
    ]

    params = {}
    fetcher = EstatSearchFetcher()
    query = fetcher.transform_query(params)

    result = fetcher.transform_data(query, raw_data)

    assert "attribution" in result.metadata
    assert "e-Stat" in result.metadata["attribution"]
    assert "not guaranteed by government" in result.metadata["attribution"]


@pytest.mark.asyncio
async def test_estat_search_single_result():
    """Test handling when API returns single result (not a list)."""

    mock_response = {
        "GET_STATS_LIST": {
            "RESULT": {"STATUS": 0, "ERROR_MSG": "Success"},
            "DATALIST_INF": {
                "LIST_INF": {  # Single dict, not list
                    "STAT_NAME": {"@id": "0003433219", "$": "Test Dataset"},
                    "STATISTICS_NAME": {"@code": "00200521", "$": "Test"},
                    "GOV_ORG": {"$": "Test Bureau"},
                }
            },
        }
    }

    params = {}
    fetcher = EstatSearchFetcher()
    query = fetcher.transform_query(params)

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_response_obj = AsyncMock()
        mock_response_obj.status = 200
        mock_response_obj.json.return_value = mock_response

        mock_get.return_value.__aenter__ = AsyncMock(return_value=mock_response_obj)
        mock_get.return_value.__aexit__ = AsyncMock(return_value=None)

        data = await fetcher.aextract_data(query, {"api_key": "test_key"})

        # Should convert single dict to list
        assert isinstance(data, list)
        assert len(data) == 1


def test_estat_search_limit_validation():
    """Test that limit parameter is validated correctly."""
    # Test upper bound - should now work with higher limit
    params = {"limit": 10000}  # Within new max
    fetcher = EstatSearchFetcher()
    query = fetcher.transform_query(params)
    assert query.limit == 10000

    # Test valid limit
    params = {"limit": 500}
    query = fetcher.transform_query(params)
    assert query.limit == 500


def test_estat_search_pagination():
    """Test pagination parameter (start_position)."""
    params = {"query": "population", "limit": 50, "start_position": 51}

    fetcher = EstatSearchFetcher()
    query = fetcher.transform_query(params)

    assert query.start_position == 51
    assert query.limit == 50


def test_estat_search_pagination_metadata():
    """Test that pagination metadata is included in response."""

    raw_data = [
        {
            "_pagination": {
                "next_key": "101",
                "number": "500",
                "result_inf": {},
            },
            "STAT_NAME": {"@id": "0003433219", "$": "Population Census 2020"},
            "STATISTICS_NAME": {"@code": "00200521", "$": "Population Census"},
            "GOV_ORG": {"$": "Statistics Bureau"},
        }
    ]

    params = {"query": "population"}
    fetcher = EstatSearchFetcher()
    query = fetcher.transform_query(params)

    result = fetcher.transform_data(query, raw_data)

    # Check pagination metadata
    assert "next_start_position" in result.metadata
    assert result.metadata["next_start_position"] == "101"
    assert result.metadata["has_more"] is True
    assert result.metadata["total_available"] == "500"
    # Ensure first dataset is still parsed correctly
    assert len(result.result) == 1
    assert result.result[0].dataset_id == "0003433219"
