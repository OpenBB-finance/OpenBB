"""IMF Utilities module integration tests."""

import pytest
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""

    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb


@pytest.mark.parametrize(
    "params",
    [
        {
            "output_format": "json",
        }
    ],
)
@pytest.mark.integration
def test_imf_list_dataflows(params, obb):
    """Test imf_list_dataflows endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.imf.list_dataflows(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        {
            "dataflow_id": "CPI",
            "output_format": "json",
        },
    ],
)
@pytest.mark.integration
def test_imf_get_dataflow_dimensions(params, obb):
    """Test imf_get_dataflow_dimensions endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.imf.get_dataflow_dimensions(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results
    assert isinstance(result.results, dict)


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_portwatch_list_port_id_choices(params, obb):
    """Test imf_portwatch_list_port_id_choices endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf.portwatch.list_port_id_choices(**params)
    assert result
    assert isinstance(result, list)


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_list_tables(params, obb):
    """Test imf_list_tables endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf.list_tables(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_list_table_choices(params, obb):
    """Test imf_list_table_choices endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf.list_table_choices(**params)
    assert result
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_list_dataflow_choices(params, obb):
    """Test imf_list_dataflow_choices endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf.list_dataflow_choices(**params)
    assert result
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize(
    "params",
    [
        {
            "dataflow_group": None,
            "table": None,
            "country": None,
            "frequency": None,
        },
        {
            "dataflow_group": "cpi",
            "table": None,
            "country": None,
            "frequency": None,
        },
    ],
)
@pytest.mark.integration
def test_imf_presentation_table_choices(params, obb):
    """Test imf_presentation_table_choices endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf.presentation_table_choices(**params)
    assert result
    assert isinstance(result, list)


@pytest.mark.parametrize(
    "params",
    [
        {
            "dataflow_group": "cpi",
            "table": "cpi",
            "country": "JPN",
            "frequency": "A",
            "dimension_values": None,
            "limit": 1,
            "raw": True,
        }
    ],
)
@pytest.mark.integration
def test_imf_presentation_table(params, obb):
    """Test imf_presentation_table endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf.presentation_table(**params)
    assert result
    assert isinstance(result, list)
    assert len(result) > 1


@pytest.mark.parametrize(
    "params",
    [
        {
            "symbol": "CPI::CPI__T",
            "country": None,
            "frequency": None,
            "transform": None,
            "dimension_values": None,
        },
        {
            "symbol": "CPI::CPI__T",
            "country": "JPN",
            "frequency": None,
            "transform": None,
            "dimension_values": None,
        },
    ],
)
@pytest.mark.integration
@pytest.mark.skip(reason="Not included in Python interface")
def test_imf_indicator_choices(params, obb):
    """Test imf_indicator_choices endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf.indicator_choices(**params)
    assert result
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_list_bop_country_choices(params, obb):
    """Test imf_list_bop_country_choices endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf.list_bop_country_choices(**params)
    assert result
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_list_cpi_country_choices(params, obb):
    """Test imf_list_cpi_country_choices endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf.list_cpi_country_choices(**params)
    assert result
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_portwatch_list_country_choices(params, obb):
    """Test imf_portwatch_list_country_choices endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf.portwatch.list_country_choices(**params)
    assert result
    assert isinstance(result, list)


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_portwatch_list_tradenow_region_choices(params, obb):
    """Test imf_portwatch_list_tradenow_region_choices endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf.portwatch.list_tradenow_region_choices(**params)
    assert result
    assert isinstance(result, list)


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_portwatch_list_container_port_choices(params, obb):
    """Test imf_portwatch_list_container_port_choices endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf.portwatch.list_container_port_choices(**params)
    assert result
    assert isinstance(result, list)
    assert result[0]["value"] == "TOP10"


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_portwatch_list_disruption_event_choices(params, obb):
    """Test imf_portwatch_list_disruption_event_choices endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf.portwatch.list_disruption_event_choices(**params)
    assert result
    assert isinstance(result, list)
    assert result[0]["value"] == "LATEST"


@pytest.mark.parametrize(
    "params",
    [{"country_code": "USA", "metric": "portcalls"}],
)
@pytest.mark.integration
def test_imf_portwatch_country_activity(params, obb):
    """Test imf_portwatch_country_activity endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf.portwatch.country_activity(**params, provider="imf")
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"code": "USA", "metric": "trade_value"}],
)
@pytest.mark.integration
def test_imf_portwatch_monthly_trade(params, obb):
    """Test imf_portwatch_monthly_trade endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf.portwatch.monthly_trade(**params, provider="imf")
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"metric": "portcalls"}],
)
@pytest.mark.integration
def test_imf_portwatch_container_metrics(params, obb):
    """Test imf_portwatch_container_metrics endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf.portwatch.container_metrics(**params, provider="imf")
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_portwatch_disruption_events(params, obb):
    """Test imf_portwatch_disruption_events endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf.portwatch.disruption_events(**params, provider="imf")
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_portwatch_disruptions_map(params, obb):
    """Test imf_portwatch_disruptions_map endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf.portwatch.disruptions_map(**params, provider="imf")
    assert result
    assert isinstance(result, OBBject)


@pytest.mark.parametrize(
    "params",
    [{"event_id": "LATEST"}],
)
@pytest.mark.integration
def test_imf_portwatch_disruption_sankey(params, obb):
    """Test imf_portwatch_disruption_sankey endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf.portwatch.disruption_sankey(**params, provider="imf")
    assert result
    assert isinstance(result, OBBject)
