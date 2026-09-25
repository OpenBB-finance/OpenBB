"""Test custom errors."""

import pytest

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError


def function_that_raises_provider_error():
    """Raise a OpenBBError."""
    raise OpenBBError("An error occurred in the provider.")


def function_that_raises_empty_data_error():
    """Raise an EmptyDataError."""
    raise EmptyDataError()


def test_provider_error_is_raised():
    """Test if the OpenBBError is raised."""
    with pytest.raises(OpenBBError) as exc_info:
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


def test_unauthorized_error_default_placeholder():
    """Default message keeps the placeholder when no provider is given."""
    from openbb_core.provider.utils.errors import UnauthorizedError

    e = UnauthorizedError()
    assert "<provider name>" in str(e)


def test_unauthorized_error_provider_substituted_string():
    """Provider name replaces the placeholder when message is a str."""
    from openbb_core.provider.utils.errors import UnauthorizedError

    e = UnauthorizedError(
        message="Unauthorized <provider name> API request.", provider_name="fmp"
    )
    assert "fmp" in str(e)
    assert "<provider name>" not in str(e)


def test_unauthorized_error_provider_substituted_tuple():
    """Provider name replaces the placeholder when default tuple message is used."""
    from openbb_core.provider.utils.errors import UnauthorizedError

    e = UnauthorizedError(provider_name="polygon")
    assert "polygon" in str(e)
