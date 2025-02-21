"""Test Regulators extension."""

import pytest
from extensions.tests.conftest import parametrize
from openbb_core.app.model.obbject import OBBject


# pylint: disable=inconsistent-return-statements
@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""

    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb  # pylint: disable=import-outside-toplevel

        return openbb.obb


# pylint: disable=redefined-outer-name


@parametrize(
    "params",
    [
        ({"symbol": "TSLA", "provider": "sec", "use_cache": None}),
        ({"symbol": "SQQQ", "provider": "sec", "use_cache": None}),
    ],
)
@pytest.mark.integration
def test_regulators_sec_cik_map(params, obb):
    """Test the SEC CIK map endpoint."""
    result = obb.regulators.sec.cik_map(**params)
    assert result
    assert isinstance(result, OBBject)
    assert hasattr(result.results, "cik")
    assert isinstance(result.results.cik, str)


@parametrize(
    "params",
    [
        ({"query": "berkshire hathaway", "provider": "sec", "use_cache": None}),
    ],
)
@pytest.mark.integration
def test_regulators_sec_institutions_search(params, obb):
    """Test the SEC institutions search endpoint."""
    result = obb.regulators.sec.institutions_search(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "query": "2022",
                "provider": "sec",
                "url": None,
                "use_cache": None,
            }
        ),
        (
            {
                "query": "",
                "provider": "sec",
                "url": "https://xbrl.fasb.org/us-gaap/2014/entire/",
                "use_cache": None,
            }
        ),
    ],
)
@pytest.mark.integration
def test_regulators_sec_schema_files(params, obb):
    """Test the SEC schema files endpoint."""
    result = obb.regulators.sec.schema_files(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results.files) > 0


@parametrize(
    "params",
    [
        ({"query": "0000909832", "provider": "sec", "use_cache": None}),
        ({"query": "0001067983", "provider": "sec", "use_cache": None}),
    ],
)
@pytest.mark.integration
def test_regulators_sec_symbol_map(params, obb):
    """Test the SEC symbol map endpoint."""
    result = obb.regulators.sec.symbol_map(**params)
    assert result
    assert isinstance(result, OBBject)
    assert hasattr(result.results, "symbol")
    assert isinstance(result.results.symbol, str)


@parametrize(
    "params",
    [({"provider": "sec"})],
)
@pytest.mark.integration
def test_regulators_sec_rss_litigation(params, obb):
    """Test the SEC RSS litigation endpoint."""
    result = obb.regulators.sec.rss_litigation(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [({"query": "oil", "use_cache": False, "provider": "sec"})],
)
@pytest.mark.integration
def test_regulators_sec_sic_search(params, obb):
    """Test the SEC SIC search endpoint."""
    result = obb.regulators.sec.sic_search(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        ({"query": "grain", "provider": "cftc"}),
    ],
)
@pytest.mark.integration
def test_regulators_cftc_cot_search(params, obb):
    """Test the CFTC COT search endpoint."""
    result = obb.regulators.cftc.cot_search(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "id": "045601",
                "report_type": "legacy",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "futures_only": False,
                "provider": "cftc",
            }
        ),
    ],
)
@pytest.mark.integration
def test_regulators_cftc_cot(params, obb):
    """Test the CFTC COT endpoint."""
    result = obb.regulators.cftc.cot(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@parametrize(
    "params",
    [
        (
            {
                "url": "https://www.sec.gov/Archives/edgar/data/21344/000155278124000634/",
                "provider": "sec",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_regulators_sec_filing_headers(params, obb):
    """Test the SEC Filing Headers endpoint."""
    from openbb_sec.models.sec_filing import SecFilingData

    result = obb.regulators.sec.filing_headers(**params)
    assert result
    assert isinstance(result, OBBject)
    assert isinstance(result.results, SecFilingData)
    assert hasattr(result.results, "cover_page")


@parametrize(
    "params",
    [
        (
            {
                "url": "https://www.sec.gov/Archives/edgar/data/1990353/000110465925015513/tm256977d7_ex99-1.htm",
                "provider": "sec",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_regulators_sec_htm_file(params, obb):
    """Test the SEC HTM File endpoint."""
    from openbb_sec.models.htm_file import SecHtmFileData

    result = obb.regulators.sec.htm_file(**params)
    assert result
    assert isinstance(result, OBBject)
    assert isinstance(result.results, SecHtmFileData)
    assert hasattr(result.results, "content")
