"""Test SEC extension."""

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
        ({"symbol": "TSLA", "provider": "sec", "use_cache": True}),
        ({"symbol": "SQQQ", "provider": "sec", "use_cache": True}),
    ],
)
@pytest.mark.integration
def test_sec_cik_map(params, obb):
    """Test the SEC CIK map endpoint."""
    result = obb.sec.cik_map(**params)
    assert result
    assert isinstance(result, OBBject)
    assert hasattr(result.results, "cik")
    assert isinstance(result.results.cik, str)


@pytest.mark.parametrize(
    "params",
    [
        ({"query": "berkshire hathaway", "provider": "sec", "use_cache": True}),
    ],
)
@pytest.mark.integration
def test_sec_institutions_search(params, obb):
    """Test the SEC institutions search endpoint."""
    result = obb.sec.institutions_search(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"provider": "sec"}),
        (
            {
                "provider": "sec",
                "taxonomy": "us-gaap",
                "year": 2024,
                "component": "soi",
            }
        ),
    ],
)
@pytest.mark.integration
def test_sec_schema_files(params, obb):
    """Test the SEC schema files endpoint."""
    result = obb.sec.schema_files(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"query": "0000909832", "provider": "sec", "use_cache": True}),
        ({"query": "0001067983", "provider": "sec", "use_cache": True}),
    ],
)
@pytest.mark.integration
def test_sec_symbol_map(params, obb):
    """Test the SEC symbol map endpoint."""
    result = obb.sec.symbol_map(**params)
    assert result
    assert isinstance(result, OBBject)
    assert hasattr(result.results, "symbol")
    assert isinstance(result.results.symbol, str)


@pytest.mark.parametrize(
    "params",
    [{"provider": "sec"}],
)
@pytest.mark.integration
def test_sec_rss_litigation(params, obb):
    """Test the SEC RSS litigation endpoint."""
    result = obb.sec.rss_litigation(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [{"query": "oil", "use_cache": False, "provider": "sec"}],
)
@pytest.mark.integration
def test_sec_sic_search(params, obb):
    """Test the SEC SIC search endpoint."""
    result = obb.sec.sic_search(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
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
def test_sec_filing_headers(params, obb):
    """Test the SEC Filing Headers endpoint."""
    from openbb_sec.models.sec_filing import SecFilingData

    result = obb.sec.filing_headers(**params)
    assert result
    assert isinstance(result, OBBject)
    assert isinstance(result.results, SecFilingData)
    assert hasattr(result.results, "cover_page")


@pytest.mark.parametrize(
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
def test_sec_htm_file(params, obb):
    """Test the SEC HTM File endpoint."""
    from openbb_sec.models.htm_file import SecHtmFileData

    result = obb.sec.htm_file(**params)
    assert result
    assert isinstance(result, OBBject)
    assert isinstance(result.results, SecHtmFileData)
    assert hasattr(result.results, "content")


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "calendar_year": 2023,
                "provider": "sec",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_sec_disclosures(params, obb):
    """Test the SEC disclosures endpoint."""
    result = obb.sec.disclosures(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "calendar_year": 2023,
                "provider": "sec",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_sec_risk_factors(params, obb):
    """Test the SEC risk factors endpoint."""
    result = obb.sec.risk_factors(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "calendar_year": 2023,
                "provider": "sec",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_sec_company_overview(params, obb):
    """Test the SEC company overview endpoint."""
    result = obb.sec.company_overview(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results.content


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "calendar_year": 2023,
                "statement_type": "balance",
                "provider": "sec",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_sec_financial_statements(params, obb):
    """Test the SEC as-filed financial statements endpoint."""
    result = obb.sec.financial_statements(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "calendar_year": 2023,
                "provider": "sec",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_sec_segment_revenue(params, obb):
    """Test the SEC segment and geographic revenue endpoint."""
    result = obb.sec.segment_revenue(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "symbol": "AAPL",
                "calendar_year": 2023,
                "provider": "sec",
                "use_cache": True,
            }
        ),
    ],
)
@pytest.mark.integration
def test_sec_legal_proceedings(params, obb):
    """Test the SEC legal proceedings endpoint."""
    result = obb.sec.legal_proceedings(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"query": "climate change", "form_type": "8-K", "provider": "sec"}),
    ],
)
@pytest.mark.integration
def test_sec_full_text_search(params, obb):
    """Test the SEC full-text search endpoint."""
    result = obb.sec.full_text_search(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "XLK", "provider": "sec"}),
    ],
)
@pytest.mark.integration
def test_sec_nport_fund_metrics(params, obb):
    """Test the SEC NPORT fund metrics endpoint."""
    result = obb.sec.nport_fund_metrics(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "CAT", "calendar_year": 2024, "provider": "sec"}),
    ],
)
@pytest.mark.integration
def test_sec_beneficial_ownership(params, obb):
    """Test the SEC beneficial ownership endpoint."""
    result = obb.sec.beneficial_ownership(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results.content


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "CAT", "calendar_year": 2024, "provider": "sec"}),
    ],
)
@pytest.mark.integration
def test_sec_management_profiles(params, obb):
    """Test the SEC management profiles endpoint."""
    result = obb.sec.management_profiles(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results.content


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "CAT", "calendar_year": 2024, "provider": "sec"}),
    ],
)
@pytest.mark.integration
def test_sec_executive_compensation(params, obb):
    """Test the SEC executive compensation endpoint."""
    result = obb.sec.executive_compensation(**params)
    assert result
    assert isinstance(result, OBBject)
    assert result.results.content


@pytest.mark.parametrize(
    "params",
    [
        ({"symbol": "CAT", "calendar_year": 2024, "provider": "sec"}),
    ],
)
@pytest.mark.integration
def test_sec_pay_versus_performance(params, obb):
    """Test the SEC pay versus performance endpoint."""
    result = obb.sec.pay_versus_performance(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
