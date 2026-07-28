"""Test the Fetcher."""

from typing import Any

import pytest

from openbb_core.provider.abstract.fetcher import Data, Fetcher, QueryParams

# Step 1: Create a dummy subclass of Fetcher


class MockData(Data):
    """Mock data class."""


class MockQueryParams(QueryParams):
    """Mock query params class."""


class MockFetcher(Fetcher[MockQueryParams, list[MockData]]):
    """Mock fetcher class."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> MockQueryParams:
        """Transform the params to the provider-specific query."""
        return MockQueryParams()

    @staticmethod
    def extract_data(query: MockQueryParams, credentials: dict[str, str] | None) -> Any:
        """Extract the data from the provider."""
        return [{"mock_key": "mock_value"}]  # Mocking a data response

    @staticmethod
    def transform_data(query: MockQueryParams, data: Any, **kwargs) -> list[MockData]:
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
    assert MockFetcher.return_type == list[MockData]


def test_fetcher_data_type():
    """Test the data_type classproperty."""
    assert MockFetcher.data_type == MockData


@pytest.mark.requires_pandas
def test_fetcher_test():
    """Test ``Fetcher.test`` runs the full pipeline (requires pandas for DataFrame assertions)."""
    pytest.importorskip("pandas")
    tested = MockFetcher.test(params={})
    assert tested is None


def test_fetcher_aextract_data_overrides_extract():
    """Test subclass implements aextract_data -> assigned to extract_data."""

    class AsyncFetcher(Fetcher[MockQueryParams, list[MockData]]):
        @staticmethod
        def transform_query(params):
            return MockQueryParams()

        @staticmethod
        async def aextract_data(query, credentials):
            return [{"mock_key": "x"}]

        @staticmethod
        def transform_data(query, data, **kwargs):
            return [MockData(**i) for i in data]

    assert AsyncFetcher.extract_data == AsyncFetcher.aextract_data


def test_fetcher_subclass_missing_extract_raises():
    """Test NotImplementedError when neither extract method implemented."""
    with pytest.raises(NotImplementedError, match="must implement"):

        class _Bad(Fetcher[MockQueryParams, list[MockData]]):
            @staticmethod
            def transform_query(params):
                return MockQueryParams()

            @staticmethod
            def transform_data(query, data, **kwargs):
                return []


def test_fetcher_return_type_annotated_result():
    """Test AnnotatedResult origin path. Since pydantic Generic doesn't expose
    typing origin, this branch is structurally unreachable; verify the property
    still returns the parameterized type without crashing."""
    from openbb_core.provider.abstract.annotated_result import AnnotatedResult

    class AnnotatedFetcher(Fetcher[MockQueryParams, AnnotatedResult[list[MockData]]]):
        @staticmethod
        def transform_query(params):
            return MockQueryParams()

        @staticmethod
        def extract_data(query, credentials):
            return [{"mock_key": "x"}]

        @staticmethod
        def transform_data(query, data, **kwargs):
            return AnnotatedResult(result=[MockData(**i) for i in data])

    rt = AnnotatedFetcher.return_type
    assert rt is not None


def test_fetcher_return_type_annotated_result_branch(monkeypatch):
    sentinel = object()

    class _Fetcher(Fetcher[MockQueryParams, list[MockData]]):
        __orig_bases__ = [(None, sentinel)]  # type: ignore[assignment]

        @staticmethod
        def transform_query(params):
            return MockQueryParams()

        @staticmethod
        def extract_data(query, credentials):
            return []

        @staticmethod
        def transform_data(query, data, **kwargs):
            return []

    monkeypatch.setattr(
        "openbb_core.provider.abstract.fetcher.get_origin",
        lambda value: (
            __import__(
                "openbb_core.provider.abstract.fetcher", fromlist=["AnnotatedResult"]
            ).AnnotatedResult
            if value is sentinel
            else None
        ),
    )
    monkeypatch.setattr(
        "openbb_core.provider.abstract.fetcher.get_args",
        lambda value: (list[MockData],) if value is sentinel else (),
    )

    assert _Fetcher.return_type == list[MockData]


@pytest.mark.requires_pandas
def test_fetcher_test_dataframe_data():
    """Test DataFrame data branch in test()."""
    pytest.importorskip("pandas")
    from pandas import DataFrame

    class DfFetcher(Fetcher[MockQueryParams, list[MockData]]):
        @staticmethod
        def transform_query(params):
            return MockQueryParams()

        @staticmethod
        def extract_data(query, credentials):
            return DataFrame([{"mock_key": "x"}])

        @staticmethod
        def transform_data(query, data, **kwargs):
            return [MockData(**row) for row in data.to_dict(orient="records")]

    assert DfFetcher.test(params={}) is None


@pytest.mark.requires_pandas
def test_fetcher_test_scalar_return():
    """Test non-list return type branch in test()."""
    pytest.importorskip("pandas")

    class ScalarFetcher(Fetcher[MockQueryParams, MockData]):
        @staticmethod
        def transform_query(params):
            return MockQueryParams()

        @staticmethod
        def extract_data(query, credentials):
            return {"mock_key": "x"}

        @staticmethod
        def transform_data(query, data, **kwargs):
            return MockData(**data)

    assert ScalarFetcher.test(params={}) is None
