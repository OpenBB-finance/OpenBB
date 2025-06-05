import pytest
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.model.credentials import Credentials
from openbb_helixdb.models.helix_query import HelixDBQueryQueryParams
from openbb_helixdb.helix_fetchers import HelixDBFetcher

@pytest.fixture(scope="module")
def mock_credentials():
    return Credentials(helixdb_api_key="test_key", helixdb_database_url="test_url")

def test_helixdb_fetcher_transform_query():
    params = HelixDBQueryQueryParams(query="SELECT * FROM test", parameters={"id": 1})
    transformed = HelixDBFetcher.transform_query(params)
    assert transformed["query"] == "SELECT * FROM test"
    assert transformed["parameters"]["id"] == 1

@pytest.mark.asyncio
async def test_helixdb_fetcher_extract_data(mock_credentials):
    # Test the mock implementation
    params_user_1 = HelixDBQueryQueryParams(query="SELECT * FROM users WHERE id = 1")

    # Since extract_data is static, we call it on the class
    # In a real scenario, this might be part of an instance or called differently
    # For now, directly calling the static method as defined
    extracted_data_user_1 = HelixDBFetcher.extract_data(query=params_user_1, credentials=mock_credentials)
    assert len(extracted_data_user_1["results"]) == 1
    assert extracted_data_user_1["results"][0]["name"] == "Test User"

    params_other = HelixDBQueryQueryParams(query="SELECT * FROM products")
    extracted_data_other = HelixDBFetcher.extract_data(query=params_other, credentials=mock_credentials)
    assert len(extracted_data_other["results"]) == 0


def test_helixdb_fetcher_transform_data():
    raw_data = {"results": [{"col1": "value1", "col2": 100}, {"col1": "value2", "col2": 200}]}
    # Query parameter is not used in the current transform_data, so passing a dummy one
    params = HelixDBQueryQueryParams(query="SELECT * FROM dummy")
    obbject_data = HelixDBFetcher.transform_data(query=params, data=raw_data)

    assert isinstance(obbject_data.results, list)
    assert len(obbject_data.results) == 2
    assert obbject_data.results[0]["col1"] == "value1"

# Basic integration test placeholder - this would typically be in a separate file
# and would involve the command runner if testing through the OpenBB interface.
# For now, this directly uses the fetcher.
@pytest.mark.integration
@pytest.mark.asyncio
async def test_helixdb_query_integration(mock_credentials):
    params = HelixDBQueryQueryParams(query="SELECT * FROM users WHERE id = 1")
    # This simulates a part of what OBBject.from_query would do
    # 1. Transform query (implicitly done if extract_data took transformed query)
    # 2. Extract data
    raw_data = HelixDBFetcher.extract_data(query=params, credentials=mock_credentials)
    # 3. Transform data
    # Corrected: OBBject.from_query is not directly used here,
    # rather we test the fetcher's transform_data method which returns the Data model.
    # The OBBject wrapping happens at a higher level.
    data_model_instance = HelixDBFetcher.transform_data(query=params, data=raw_data)

    # The fetcher's transform_data returns an instance of HelixDBQueryData, not OBBject directly.
    # The OBBject is constructed by the core system using this Data instance.
    # So, we assert properties of data_model_instance.
    # To simulate OBBject, we'd wrap it manually if needed for test scope.
    # For this test, asserting the Data model's content is sufficient.

    # If we were to wrap it in an OBBject for testing provider property:
    obbject_results = OBBject(results=data_model_instance.results, provider="helixdb")

    assert isinstance(obbject_results.results, list) # Check results on OBBject
    assert obbject_results.provider == "helixdb"
    assert len(obbject_results.results) == 1
    assert obbject_results.results[0]["name"] == "Test User"

# It's good practice to also have a test for the provider definition itself,
# but that might be more of a core platform test.
# For now, focusing on the fetcher.
