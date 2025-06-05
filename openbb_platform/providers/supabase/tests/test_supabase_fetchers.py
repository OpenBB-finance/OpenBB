import pytest
from unittest.mock import patch, MagicMock
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.model.credentials import Credentials
from openbb_supabase.models.supabase_query import SupabaseQueryQueryParams, SupabaseQueryData # Corrected import for SupabaseQueryData
from openbb_supabase.supabase_fetchers import SupabaseFetcher

@pytest.fixture(scope="module")
def mock_credentials():
    return Credentials(supabase_url="https://test.supabase.co", supabase_key="test_key")

def test_supabase_fetcher_transform_query():
    params = SupabaseQueryQueryParams(table_name="users", select_query="id, name", limit=10)
    # transform_query for Supabase currently returns params as is
    transformed = SupabaseFetcher.transform_query(params)
    assert transformed.table_name == "users"
    assert transformed.select_query == "id, name"
    assert transformed.limit == 10

@pytest.mark.asyncio
@patch("openbb_supabase.supabase_fetchers.create_client")
async def test_supabase_fetcher_extract_data(mock_create_client, mock_credentials):
    # Mock Supabase client and its methods
    mock_supabase_client = MagicMock()
    mock_query_builder = MagicMock()
    mock_execute_response = MagicMock()

    # Configure the mock calls
    mock_create_client.return_value = mock_supabase_client
    mock_supabase_client.table.return_value = mock_query_builder
    mock_query_builder.select.return_value = mock_query_builder
    mock_query_builder.eq.return_value = mock_query_builder # For filter
    mock_query_builder.limit.return_value = mock_query_builder
    mock_query_builder.execute.return_value = mock_execute_response
    mock_execute_response.data = [{"id": 1, "name": "Test User"}]

    params = SupabaseQueryQueryParams(
        table_name="users",
        select_query="id, name",
        filters=[{"column": "id", "operator": "eq", "value": 1}],
        limit=1
    )

    extracted_data = SupabaseFetcher.extract_data(query_params=params, credentials=mock_credentials)

    mock_create_client.assert_called_once_with("https://test.supabase.co", "test_key")
    mock_supabase_client.table.assert_called_with("users")
    mock_query_builder.select.assert_called_with("id, name")
    mock_query_builder.eq.assert_called_with("id", 1)
    mock_query_builder.limit.assert_called_with(1)
    mock_query_builder.execute.assert_called_once()

    assert len(extracted_data["results"]) == 1
    assert extracted_data["results"][0]["name"] == "Test User"

@pytest.mark.asyncio
@patch("openbb_supabase.supabase_fetchers.create_client")
async def test_supabase_fetcher_extract_data_no_results(mock_create_client, mock_credentials):
    mock_supabase_client = MagicMock()
    mock_query_builder = MagicMock()
    mock_execute_response = MagicMock()

    mock_create_client.return_value = mock_supabase_client
    mock_supabase_client.table.return_value = mock_query_builder
    mock_query_builder.select.return_value = mock_query_builder
    mock_query_builder.execute.return_value = mock_execute_response
    mock_execute_response.data = None # Simulate no data returned

    params = SupabaseQueryQueryParams(table_name="empty_table", select_query="*")
    extracted_data = SupabaseFetcher.extract_data(query_params=params, credentials=mock_credentials)
    assert len(extracted_data["results"]) == 0

@pytest.mark.asyncio
@patch("openbb_supabase.supabase_fetchers.create_client")
async def test_supabase_fetcher_extract_data_api_error(mock_create_client, mock_credentials):
    mock_create_client.side_effect = Exception("API Connection Error")

    params = SupabaseQueryQueryParams(table_name="users", select_query="id, name")

    # Check if it handles the exception gracefully (as per current implementation)
    extracted_data = SupabaseFetcher.extract_data(query_params=params, credentials=mock_credentials)
    assert len(extracted_data["results"]) == 0


def test_supabase_fetcher_transform_data():
    raw_data = {"results": [{"col1": "valueA", "col2": 300}, {"col1": "valueB", "col2": 400}]}
    params = SupabaseQueryQueryParams(table_name="dummy") # Not used by current transform_data
    # Corrected: The method returns SupabaseQueryData, not OBBject directly
    data_model_instance = SupabaseFetcher.transform_data(query_params=params, data=raw_data)

    assert isinstance(data_model_instance, SupabaseQueryData)
    assert isinstance(data_model_instance.results, list)
    assert len(data_model_instance.results) == 2
    assert data_model_instance.results[0]["col1"] == "valueA"

# Basic integration test placeholder
@pytest.mark.integration
@pytest.mark.asyncio
@patch("openbb_supabase.supabase_fetchers.create_client") # Keep Supabase calls mocked for now
async def test_supabase_query_integration(mock_create_client, mock_credentials):
    mock_supabase_client = MagicMock()
    mock_query_builder = MagicMock()
    mock_execute_response = MagicMock()
    mock_create_client.return_value = mock_supabase_client
    mock_supabase_client.table.return_value = mock_query_builder
    mock_query_builder.select.return_value = mock_query_builder
    mock_query_builder.eq.return_value = mock_query_builder
    mock_query_builder.limit.return_value = mock_query_builder
    mock_query_builder.execute.return_value = mock_execute_response
    mock_execute_response.data = [{"id": 1, "name": "Integrated Test User"}]

    params = SupabaseQueryQueryParams(
        table_name="users",
        select_query="id, name",
        filters=[{"column": "id", "operator": "eq", "value": 1}],
        limit=1
    )

    # Simulate OBBject.from_query relevant parts
    raw_data = SupabaseFetcher.extract_data(query_params=params, credentials=mock_credentials)
    # The fetcher's transform_data returns an instance of SupabaseQueryData
    data_model_instance = SupabaseFetcher.transform_data(query_params=params, data=raw_data)

    # For testing provider property, wrap in OBBject manually
    obbject_results = OBBject(results=data_model_instance.results, provider="supabase")

    assert isinstance(obbject_results, OBBject)
    assert obbject_results.provider == "supabase"
    assert len(obbject_results.results) == 1
    assert obbject_results.results[0]["name"] == "Integrated Test User"
