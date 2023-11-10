"""Python interface integration tests for the equity extension."""

import pytest
from openbb_core.app.model.obbject import OBBject

# pylint: disable=too-many-lines,redefined-outer-name
# pylint: disable=import-outside-toplevel,inconsistent-return-statements


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
        ({"date": "2023-01-25", "provider": "intrinio", "symbol": "AAPL"}),
        ({"provider": "cboe", "symbol": "AAPL"}),
    ],
)
@pytest.mark.integration
def test_derivatives_options_chains(params, obb):
    result = obb.derivatives.options.chains(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "AAPL"}),
        ({"source": "delayed", "provider": "intrinio", "symbol": "AAPL"}),
        ({"symbol": None, "source": "delayed", "provider": "intrinio"}),
        ({"symbol": "PLTR", "source": "delayed", "provider": "intrinio"}),
    ],
)
@pytest.mark.integration
def test_derivatives_options_unusual(params, obb):
    result = obb.derivatives.options.unusual(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
