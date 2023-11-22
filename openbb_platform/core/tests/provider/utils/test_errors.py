"""Test custom errors."""

import pytest
from openbb_core.provider.utils.errors import EmptyDataError, ProviderError


def function_that_raises_provider_error():
    """Raise a ProviderError."""
    raise ProviderError("An error occurred in the provider.")


def function_that_raises_empty_data_error():
    """Raise an EmptyDataError."""
    raise EmptyDataError()


def test_provider_error_is_raised():
    """Test if the ProviderError is raised."""
    with pytest.raises(ProviderError) as exc_info:
        function_that_raises_provider_error()
    assert str(exc_info.value) == "An error occurred in the provider."


def test_empty_data_error_is_raised():
    """Test if the EmptyDataError is raised."""
    with pytest.raises(EmptyDataError) as exc_info:
        function_that_raises_empty_data_error()
    assert (
        str(exc_info.value) == "No results found. Try adjusting the query parameters."
    )


def test_empty_data_error_custom_message():
    """Test if the EmptyDataError is raised with a custom message."""
    custom_message = "Custom message for no data."
    with pytest.raises(EmptyDataError) as exc_info:
        raise EmptyDataError(custom_message)
    assert str(exc_info.value) == custom_message
