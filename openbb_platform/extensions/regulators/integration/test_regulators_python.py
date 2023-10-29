"""Test Regulators extension."""
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
        ({"symbol": "TSLA", "provider": "sec"}),
        ({"symbol": "SQQQ", "provider": "sec"}),
    ],
)
@pytest.mark.integration
def test_regulators_sec_cik_map(params, obb):
    result = obb.regulators.sec.cik_map(**params)
    assert result
    assert isinstance(result, OBBject)
    assert hasattr(result.results, "cik")
    assert isinstance(result.results.cik, str)


@pytest.mark.parametrize(
    "params",
    [
        ({"query": "berkshire hathaway", "provider": "sec"}),
    ],
)
@pytest.mark.integration
def test_regulators_sec_institutions_search(params, obb):
    result = obb.regulators.sec.institutions_search(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "limit": 3,
                "type": "8-K",
                "cik": None,
                "provider": "sec",
                "use_cache": False,
            }
        ),
        (
            {
                "cik": "0001067983",
                "limit": 3,
                "type": "10-Q",
                "symbol": None,
                "provider": "sec",
                "use_cache": False,
            }
        ),
    ],
)
@pytest.mark.integration
def test_regulators_sec_filings(params, obb):
    result = obb.regulators.sec.filings(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"query": "2022", "provider": "sec", "url": None}),
        (
            {
                "query": "",
                "provider": "sec",
                "url": "https://xbrl.fasb.org/us-gaap/2014/entire/",
            }
        ),
    ],
)
@pytest.mark.integration
def test_regulators_sec_schema_files(params, obb):
    result = obb.regulators.sec.schema_files(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results.files) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"query": "0000909832", "provider": "sec"}),
        ({"query": "0001067983", "provider": "sec"}),
    ],
)
@pytest.mark.integration
def test_regulators_sec_symbol_map(params, obb):
    result = obb.regulators.sec.symbol_map(**params)
    assert result
    assert isinstance(result, OBBject)
    assert hasattr(result.results, "symbol")
    assert isinstance(result.results.symbol, str)


@pytest.mark.parametrize(
    "params",
    [({"provider": "sec"})],
)
@pytest.mark.integration
def test_regulators_sec_rss_litigation(params, obb):
    result = obb.regulators.sec.rss_litigation(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [({"query": "oil", "use_cache": False, "provider": "sec"})],
)
@pytest.mark.integration
def test_regulators_sec_sic_search(params, obb):
    result = obb.regulators.sec.sic_search(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
