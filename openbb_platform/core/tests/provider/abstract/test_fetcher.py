"""Test the Fetcher."""

from typing import Any, Dict, List, Optional

import pytest
from openbb_core.provider.abstract.fetcher import Data, Fetcher, QueryParams

# Step 1: Create a dummy subclass of Fetcher


class MockData(Data):
    """Mock data class."""


class MockQueryParams(QueryParams):
    """Mock query params class."""


class MockFetcher(Fetcher[MockQueryParams, List[MockData]]):
    """Mock fetcher class."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> MockQueryParams:
        """Transform the params to the provider-specific query."""
        return MockQueryParams()

    @staticmethod
    def extract_data(
        query: MockQueryParams, credentials: Optional[Dict[str, str]]
    ) -> Any:
        """Extract the data from the provider."""
        return [{"mock_key": "mock_value"}]  # Mocking a data response

    @staticmethod
    def transform_data(query: MockQueryParams, data: Any, **kwargs) -> List[MockData]:
        """Transform the provider-specific data."""
        return [MockData(**item) for item in data]


@pytest.mark.asyncio
async def test_fetcher_methods():
    """Test the Fetcher abstract methods using a mock Fetcher subclass."""
    params = {"param1": "value1"}
    mock_fetcher = MockFetcher()

    fetched_data = await mock_fetcher.fetch_data(params=params)
    assert isinstance(fetched_data, list)
    assert isinstance(fetched_data[0], MockData)
    assert fetched_data[0].model_dump() == {"mock_key": "mock_value"}


def test_fetcher_query_params_type():
    """Test the query_params_type classproperty."""
    assert MockFetcher.query_params_type == MockQueryParams


def test_fetcher_return_type():
    """Test the return_type classproperty."""
    assert MockFetcher.return_type == List[MockData]


def test_fetcher_data_type():
    """Test the data_type classproperty."""
    assert MockFetcher.data_type == MockData


def test_fetcher_test():
    """Test the test method."""
    tested = MockFetcher.test(params={})
    assert tested is None
