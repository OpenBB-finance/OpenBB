"""Integration tests for the usda Python interface (obb.usda)."""

from importlib.util import find_spec

import pytest
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb


def _clean(params: dict) -> dict:
    """Drop None values so omitted params fall back to their defaults."""
    return {k: v for k, v in params.items() if v is not None}


@pytest.mark.parametrize(
    "params",
    [
        {"provider": "usda"},
        {
            "provider": "usda",
            "commodity": "coffee",
            "attribute": "exports",
            "country": "brazil",
            "start_year": 2020,
            "end_year": 2025,
        },
    ],
)
@pytest.mark.skipif(
    find_spec("openbb_commodity") is not None,
    reason="commands live on the commodity extension",
)
@pytest.mark.integration
def test_usda_psd_data(params, obb):
    """PSD data tables and time series."""
    result = obb.usda.psd_data(**_clean(params))
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"provider": "usda", "commodity": "sugar", "year": 2025, "month": 5}],
)
@pytest.mark.skipif(
    find_spec("openbb_commodity") is not None,
    reason="commands live on the commodity extension",
)
@pytest.mark.integration
def test_usda_psd_report(params, obb):
    """PSD PDF report as base64 content."""
    result = obb.usda.psd_report(**_clean(params))
    assert isinstance(result, dict)
    assert result.get("content")


@pytest.mark.parametrize(
    "params",
    [{"provider": "usda", "year": 2024, "month": 12, "week": 2}],
)
@pytest.mark.skipif(
    find_spec("openbb_commodity") is not None,
    reason="commands live on the commodity extension",
)
@pytest.mark.integration
def test_usda_weather_bulletins(params, obb):
    """Weather bulletin links."""
    result = obb.usda.weather_bulletins(**_clean(params))
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize(
    "params",
    [
        {
            "provider": "usda",
            "urls": [
                "https://esmis.nal.usda.gov/sites/default/release-files/cj82k728n/9w033w568/x059f4232/wwcb0125.pdf"
            ],
        }
    ],
)
@pytest.mark.skipif(
    find_spec("openbb_commodity") is not None,
    reason="commands live on the commodity extension",
)
@pytest.mark.integration
def test_usda_weather_bulletins_download(params, obb):
    """Weather bulletin PDF download."""
    result = obb.usda.weather_bulletins_download(**_clean(params))
    assert isinstance(result, list)
    assert result[0].get("content")
