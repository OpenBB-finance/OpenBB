"""Tests for the Fama-French router commands."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from openbb_famafrench import famafrench_router as router

MODEL_COMMANDS = [
    router.factors,
    router.us_portfolio_returns,
    router.regional_portfolio_returns,
    router.country_portfolio_returns,
    router.international_index_returns,
    router.breakpoints,
]


@pytest.mark.parametrize("command", MODEL_COMMANDS)
def test_model_backed_commands(command):
    """Each model-backed command delegates to OBBject.from_query(OpenBBQuery(...))."""
    sentinel = object()

    with (
        patch.object(router, "OBBject") as mock_obbject,
        patch.object(router, "OpenBBQuery") as mock_query,
    ):
        mock_obbject.from_query = AsyncMock(return_value=sentinel)

        result = asyncio.run(
            command(
                cc=None,
                provider_choices=None,
                standard_params=None,
                extra_params=None,
            )
        )

    assert result is sentinel
    assert mock_query.called
    mock_obbject.from_query.assert_awaited_once()


def test_factor_choices_region_only():
    """factor_choices returns factor choices for a region."""
    result = asyncio.run(router.factor_choices(region="europe"))

    assert isinstance(result, list)
    assert result
    assert all("label" in d and "value" in d for d in result)


def test_factor_choices_region_and_factor():
    """factor_choices returns interval choices for a region and factor."""
    result = asyncio.run(router.factor_choices(region="europe", factor="3_Factors"))

    assert isinstance(result, list)
    assert result


def test_factor_choices_no_args():
    """factor_choices returns all regions when no arguments are supplied."""
    result = asyncio.run(router.factor_choices())

    assert isinstance(result, list)
    assert result


def test_factor_choices_portfolio():
    """factor_choices returns portfolio choices when is_portfolio is True."""
    result = asyncio.run(router.factor_choices(region="america", is_portfolio=True))

    assert isinstance(result, list)
    assert result


def test_factor_choices_is_portfolio_false_value():
    """factor_choices coerces a non-True is_portfolio value to False."""
    result = asyncio.run(router.factor_choices(is_portfolio=False))

    assert isinstance(result, list)
    assert result


def test_factor_choices_helper_invoked():
    """factor_choices forwards arguments to get_factor_choices."""
    with patch(
        "openbb_famafrench.utils.helpers.get_factor_choices",
        new=AsyncMock(return_value=[{"label": "x", "value": "x"}]),
    ) as mock_helper:
        result = asyncio.run(router.factor_choices(region="japan"))

    assert result == [{"label": "x", "value": "x"}]
    mock_helper.assert_awaited_once_with(
        region="japan", factor=None, is_portfolio=False, portfolio=None
    )


def test_famafrench_apps_serves_bundled_template():
    """famafrench_apps returns the parsed contents of the bundled apps.json."""
    result = asyncio.run(router.famafrench_apps())

    assert result
    assert isinstance(result, (dict, list))
