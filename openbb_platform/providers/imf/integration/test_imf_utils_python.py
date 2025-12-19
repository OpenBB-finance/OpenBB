"""IMF Utilities module integration tests."""

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
        {
            "output_format": "json",
        }
    ],
)
@pytest.mark.integration
def test_imf_utils_list_dataflows(params, obb):
    """Test imf_utils_list_dataflows endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.imf_utils.list_dataflows(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0  # type: ignore


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
def test_imf_utils_get_dataflow_dimensions(params, obb):
    """Test imf_utils_get_dataflow_dimensions endpoint."""
    params = {p: v for p, v in params.items() if v}

    result = obb.imf_utils.get_dataflow_dimensions(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results
    assert isinstance(result.results, dict)


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_utils_list_port_id_choices(params, obb):
    """Test imf_utils_list_port_id_choices endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf_utils.list_port_id_choices(**params)
    assert result
    assert isinstance(result, list)


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_utils_list_tables(params, obb):
    """Test imf_utils_list_tables endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf_utils.list_tables(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0  # type: ignore


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_utils_list_table_choices(params, obb):
    """Test imf_utils_list_table_choices endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf_utils.list_table_choices(**params)
    assert result
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_imf_utils_list_dataflow_choices(params, obb):
    """Test imf_utils_list_dataflow_choices endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf_utils.list_dataflow_choices(**params)
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
def test_imf_utils_presentation_table_choices(params, obb):
    """Test imf_utils_presentation_table_choices endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf_utils.presentation_table_choices(**params)
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
def test_imf_utils_presentation_table(params, obb):
    """Test imf_utils_presentation_table endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf_utils.presentation_table(**params)
    assert result
    assert isinstance(result, list)
    assert len(result) > 1  # type: ignore


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
def test_imf_utils_indicator_choices(params, obb):
    """Test imf_utils_indicator_choices endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.imf_utils.indicator_choices(**params)
    assert result
    assert isinstance(result, list)
    assert len(result) > 0
