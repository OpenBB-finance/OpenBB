"""Test Commodity extension."""

import pytest
from openbb_core.app.model.obbject import OBBject

# pylint: disable=redefined-outer-name


@pytest.fixture(scope="session")
def obb(pytestconfig):  # pylint: disable=inconsistent-return-statements
    """Fixture to setup obb."""
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb  # pylint: disable=import-outside-toplevel

        return openbb.obb


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "commodity": "all",
                "start_date": None,
                "end_date": None,
                "frequency": None,
                "transform": None,
                "aggregation_method": None,
                "provider": "fred",
            }
        ),
    ],
)
@pytest.mark.integration
def test_commodity_price_spot(params, obb):
    """Test the commodity spot prices endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.commodity.price.spot(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "category": "balance_sheet",
                "table": "stocks",
                "start_date": None,
                "end_date": None,
                "provider": "eia",
                "use_cache": True,
            }
        ),
        (
            {
                "category": "weekly_estimates",
                "table": "crude_production",
                "start_date": "2020-01-01",
                "end_date": "2023-12-31",
                "provider": "eia",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_commodity_petroleum_status_report(params, obb):
    """Test Commodity Petroleum Status Report endpoint."""
    result = obb.commodity.petroleum_status_report(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "table": "01",
                "symbol": None,
                "start_date": "2024-09-01",
                "end_date": "2024-10-01",
                "provider": "eia",
                "frequency": "month",
            }
        ),
    ],
)
@pytest.mark.integration
def test_commodity_short_term_energy_outlook(params, obb):
    """Test Commodity Short Term Energy Outlook endpoint."""
    result = obb.commodity.short_term_energy_outlook(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "commodity": "sugar",
                "year": 2025,
                "month": 5,
                "provider": "government_us",
            }
        ),
    ],
)
@pytest.mark.integration
def test_commodity_psd_report(params, obb):
    """Test Commodity PSD Report endpoint."""
    result = obb.commodity.psd_report(**params)
    assert result
    assert isinstance(result, dict)
    assert result["data_format"]["data_type"] == "pdf"


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "year": 2025,
                "month": 5,
                "week": 2,
                "provider": "government_us",
            }
        ),
    ],
)
@pytest.mark.integration
def test_commodity_weather_bulletins(params, obb):
    """Test Commodity Weather Bulletins endpoint."""
    result = obb.commodity.weather_bulletins(**params)
    assert result
    assert isinstance(result, list)
    assert len(result) > 0
    for bulletin in result:
        assert bulletin["label"]
        assert bulletin["value"]


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "urls": [
                    "https://esmis.nal.usda.gov/sites/default/release-files/cj82k728n/vx023b997/z890tr81b/wwcb1825.pdf",
                    "https://esmis.nal.usda.gov/sites/default/release-files/cj82k728n/w6635s43r/x059dz29h/wwcb1924.pdf",
                ],
                "provider": "government_us",
            }
        ),
    ],
)
@pytest.mark.integration
def test_commodity_weather_bulletins_download(params, obb):
    """Test Commodity Weather Bulletins Download endpoint."""
    result = obb.commodity.weather_bulletins_download(**params)
    assert result
    assert isinstance(result, list)
    assert len(result) > 0
    for bulletin in result:
        assert isinstance(bulletin, dict)
        assert bulletin["content"]
        assert bulletin["data_format"]["data_type"] == "pdf"


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "provider": "government_us",
            }
        ),
        (
            {
                "provider": "government_us",
                "report_id": "coffee_summary",
                "commodity": None,
                "country": None,
                "attribute": None,
                "start_year": None,
                "end_year": None,
                "aggregate_regions": False,
            }
        ),
        (
            {
                "report_id": "world_crop_production_summary",  # ignored if commodity is set
                "commodity": "corn",
                "country": "united_states,argentina",
                "attribute": "exports",
                "start_year": 2025,
                "end_year": 2025,
                "provider": "government_us",
                "aggregate_regions": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_commodity_psd_data(params, obb):
    """Test Commodity PSD Data endpoint."""
    params = {p: v for p, v in params.items() if v is not None}

    result = obb.commodity.psd_data(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
