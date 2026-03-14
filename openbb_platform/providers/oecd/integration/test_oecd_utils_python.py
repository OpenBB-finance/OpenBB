"""OECD Utilities module integration tests."""

import pytest
from openbb_core.app.model.obbject import OBBject

# pylint: disable=redefined-outer-name


@pytest.fixture(scope="session")
def obb(pytestconfig):  # pylint: disable=inconsistent-return-statements
    """Fixture to setup obb."""

    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb  # pylint: disable=import-outside-toplevel

        return openbb.obb


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_oecd_utils_list_topic_choices(params, obb):
    """Test oecd_utils_list_topic_choices endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.oecd_utils.list_topic_choices(**params)
    assert result
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize(
    "params",
    [
        {
            "topic": None,
        },
        {
            "topic": "ECO",
        },
    ],
)
@pytest.mark.integration
def test_oecd_utils_list_subtopic_choices(params, obb):
    """Test oecd_utils_list_subtopic_choices endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.oecd_utils.list_subtopic_choices(**params)
    assert isinstance(result, list)


@pytest.mark.parametrize(
    "params",
    [
        {
            "topic": None,
            "subtopic": None,
        },
        {
            "topic": "ECO",
            "subtopic": None,
        },
    ],
)
@pytest.mark.integration
def test_oecd_utils_list_dataflows(params, obb):
    """Test oecd_utils_list_dataflows endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.oecd_utils.list_dataflows(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0  # type: ignore


@pytest.mark.parametrize("params", [{}])
@pytest.mark.integration
def test_oecd_utils_list_dataflow_choices(params, obb):
    """Test oecd_utils_list_dataflow_choices endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.oecd_utils.list_dataflow_choices(**params)
    assert result
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize(
    "params",
    [
        {
            "query": None,
        },
        {
            "query": "health",
        },
    ],
)
@pytest.mark.integration
def test_oecd_utils_list_topics(params, obb):
    """Test oecd_utils_list_topics endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.oecd_utils.list_topics(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0  # type: ignore


@pytest.mark.parametrize(
    "params",
    [
        {
            "dataflow_id": "DF_PRICES_ALL",
            "output_format": "json",
        },
        {
            "dataflow_id": "DF_PRICES_ALL",
            "output_format": "markdown",
        },
    ],
)
@pytest.mark.integration
def test_oecd_utils_get_dataflow_parameters(params, obb):
    """Test oecd_utils_get_dataflow_parameters endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.oecd_utils.get_dataflow_parameters(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.parametrize(
    "params",
    [
        {
            "query": None,
            "topic": None,
            "subtopic": None,
            "dataflow_id": None,
        },
        {
            "query": "GDP",
            "topic": None,
            "subtopic": None,
            "dataflow_id": None,
        },
        {
            "query": None,
            "topic": "HEA",
            "subtopic": None,
            "dataflow_id": None,
        },
        {
            "query": None,
            "topic": None,
            "subtopic": None,
            "dataflow_id": "DF_PRICES_ALL",
        },
    ],
)
@pytest.mark.integration
def test_oecd_utils_list_tables(params, obb):
    """Test oecd_utils_list_tables endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.oecd_utils.list_tables(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0  # type: ignore


@pytest.mark.parametrize(
    "params",
    [
        {
            "table_id": "DF_PRICES_ALL",
        },
        {
            "table_id": "DF_T725R_Q",
        },
    ],
)
@pytest.mark.integration
def test_oecd_utils_get_table_detail(params, obb):
    """Test oecd_utils_get_table_detail endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.oecd_utils.get_table_detail(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results


@pytest.mark.parametrize(
    "params",
    [
        {
            "topic": None,
        },
        {
            "topic": "ECO",
        },
    ],
)
@pytest.mark.integration
def test_oecd_utils_list_table_choices(params, obb):
    """Test oecd_utils_list_table_choices endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.oecd_utils.list_table_choices(**params)
    assert result
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize(
    "params",
    [
        {
            "symbol": "DF_PRICES_ALL::CPI",
            "country": None,
            "frequency": None,
            "transform": None,
            "dimension_values": None,
        },
        {
            "symbol": "DF_PRICES_ALL::CPI",
            "country": "true",
            "frequency": None,
            "transform": None,
            "dimension_values": None,
        },
        {
            "symbol": "DF_PRICES_ALL::CPI",
            "country": "USA",
            "frequency": "true",
            "transform": None,
            "dimension_values": None,
        },
    ],
)
@pytest.mark.integration
@pytest.mark.skip(reason="Not included in Python interface (include_in_schema=False)")
def test_oecd_utils_indicator_choices(params, obb):
    """Test oecd_utils_indicator_choices endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.oecd_utils.indicator_choices(**params)
    assert isinstance(result, list)


@pytest.mark.parametrize(
    "params",
    [
        {
            "topic": None,
            "subtopic": None,
            "table": None,
            "country": None,
            "frequency": None,
        },
    ],
)
@pytest.mark.integration
def test_oecd_utils_presentation_table_choices(params, obb):
    """Test oecd_utils_presentation_table_choices endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.oecd_utils.presentation_table_choices(**params)
    assert isinstance(result, list)


@pytest.mark.parametrize(
    "params",
    [
        {
            "table": "DF_QNA::T0101",
            "country": "USA",
            "dimension": "unit_measure",
            "frequency": None,
        },
    ],
)
@pytest.mark.integration
@pytest.mark.skip(reason="Not included in Python interface (include_in_schema=False)")
def test_oecd_utils_presentation_table_dim_choices(params, obb):
    """Test oecd_utils_presentation_table_dim_choices endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.oecd_utils.presentation_table_dim_choices(**params)
    assert isinstance(result, list)


@pytest.mark.parametrize(
    "params",
    [
        {
            "topic": None,
            "subtopic": None,
            "table": "DF_PRICES_ALL",
            "country": "USA",
            "counterpart": None,
            "frequency": "M",
            "unit_measure": None,
            "adjustment": None,
            "transformation": None,
            "dimension_values": None,
            "limit": 2,
            "start_date": None,
            "end_date": None,
        },
    ],
)
@pytest.mark.integration
def test_oecd_utils_presentation_table(params, obb):
    """Test oecd_utils_presentation_table endpoint."""
    params = {p: v for p, v in params.items() if v}
    result = obb.oecd_utils.presentation_table(**params)
    assert result
