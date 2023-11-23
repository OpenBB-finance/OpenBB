"""Test the Provider."""

from openbb_core.provider.abstract.provider import Provider


def test_provider_initialization():
    """Test the basic initialization of the Provider class."""
    provider = Provider(name="TestProvider", description="A simple test provider.")

    assert provider.name == "TestProvider"
    assert provider.description == "A simple test provider."
    assert provider.website is None
    assert provider.credentials == []
    assert provider.fetcher_dict == {}


def test_provider_with_optional_parameters():
    """Test the initialization of the Provider class with optional parameters."""
    provider = Provider(
        name="TestProvider",
        description="A simple test provider.",
        website="https://testprovider.example.com",
        credentials=["api_key"],
        fetcher_dict={"fetcher1": None},
    )

    assert provider.name == "TestProvider"
    assert provider.description == "A simple test provider."
    assert provider.website == "https://testprovider.example.com"
    assert provider.credentials == ["testprovider_api_key"]
    assert provider.fetcher_dict == {"fetcher1": None}


def test_provider_credentials_formatting():
    """Test the formatting of required credentials."""
    credentials = ["key1", "key2"]
    provider = Provider(
        name="TestProvider",
        description="A simple test provider.",
        credentials=credentials,
    )

    expected_credentials = ["testprovider_key1", "testprovider_key2"]
    assert provider.credentials == expected_credentials
