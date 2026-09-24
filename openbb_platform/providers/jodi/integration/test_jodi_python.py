"""Test the JODI extension through the Python interface."""

import pytest
from openbb_core.app.model.obbject import OBBject


@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""
    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb

    pytest.skip("Integration tests are not enabled.")


def run(obb, path, params):
    """Run one endpoint and make the common assertions."""
    params = {p: v for p, v in params.items() if v is not None}
    func = obb.jodi
    for part in path.split("."):
        func = getattr(func, part)
    result = func(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    assert result.extra["results_metadata"]["source"]


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": None,
                "product": None,
                "unit": None,
                "start_date": None,
                "end_date": None,
                "provider": "jodi",
                "use_cache": True,
            }
        ),
        (
            {
                "country": "india",
                "product": "gasoline",
                "unit": "ktons",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_oil_balance(params, obb):
    """Test the oil balance endpoint."""
    run(obb, "oil.balance", params)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": None,
                "product": None,
                "unit": None,
                "start_date": None,
                "end_date": None,
                "provider": "jodi",
                "use_cache": True,
            }
        ),
        (
            {
                "country": "saudi_arabia,iraq,united_states",
                "product": "crude_oil",
                "unit": "kbd",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_oil_production(params, obb):
    """Test the oil production endpoint."""
    run(obb, "oil.production", params)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": "united_states,china,india",
                "product": "gasoline",
                "unit": "kbd",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_oil_demand(params, obb):
    """Test the oil demand endpoint."""
    run(obb, "oil.demand", params)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": "japan",
                "unit": "kbd",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_oil_demand_by_product(params, obb):
    """Test the oil demand by product endpoint."""
    run(obb, "oil.demand_by_product", params)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": "china,india,south_korea",
                "product": "crude_oil",
                "unit": "kbd",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_oil_imports(params, obb):
    """Test the oil imports endpoint."""
    run(obb, "oil.imports", params)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": "saudi_arabia,united_arab_emirates",
                "product": "crude_oil",
                "unit": "kbd",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_oil_exports(params, obb):
    """Test the oil exports endpoint."""
    run(obb, "oil.exports", params)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": "united_states,japan",
                "product": "crude_oil",
                "unit": "kbbl",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_oil_stocks(params, obb):
    """Test the oil stocks endpoint."""
    run(obb, "oil.stocks", params)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": None,
                "unit": None,
                "start_date": None,
                "end_date": None,
                "provider": "jodi",
                "use_cache": True,
            }
        ),
        (
            {
                "country": "norway",
                "unit": "tj",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_gas_balance(params, obb):
    """Test the gas balance endpoint."""
    run(obb, "gas.balance", params)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": "united_states,qatar,norway",
                "unit": "m3",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_gas_production(params, obb):
    """Test the gas production endpoint."""
    run(obb, "gas.production", params)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": "germany,france,italy",
                "measure": "observed",
                "unit": "m3",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_gas_demand(params, obb):
    """Test the gas demand endpoint."""
    run(obb, "gas.demand", params)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": "japan,china,south_korea",
                "flow": "lng",
                "unit": "m3",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_gas_imports(params, obb):
    """Test the gas imports endpoint."""
    run(obb, "gas.imports", params)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": "united_states,qatar,australia",
                "flow": "lng",
                "unit": "m3",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_gas_exports(params, obb):
    """Test the gas exports endpoint."""
    run(obb, "gas.exports", params)


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "country": "germany,france,netherlands",
                "unit": "m3",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "provider": "jodi",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_jodi_gas_stocks(params, obb):
    """Test the gas stocks endpoint."""
    run(obb, "gas.stocks", params)
