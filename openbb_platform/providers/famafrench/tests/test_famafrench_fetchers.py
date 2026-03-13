"""Fama-French fetchers tests."""

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_famafrench.models.breakpoints import FamaFrenchBreakpointFetcher
from openbb_famafrench.models.country_portfolio_returns import (
    FamaFrenchCountryPortfolioReturnsFetcher,
)
from openbb_famafrench.models.factors import FamaFrenchFactorsFetcher
from openbb_famafrench.models.international_index_returns import (
    FamaFrenchInternationalIndexReturnsFetcher,
)
from openbb_famafrench.models.regional_portfolio_returns import (
    FamaFrenchRegionalPortfolioReturnsFetcher,
)
from openbb_famafrench.models.us_portfolio_returns import (
    FamaFrenchUSPortfolioReturnsFetcher,
)

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration."""
    return {
        "filter_headers": [
            ("User-Agent", None),
        ],
    }


@pytest.mark.record_http
def test_famafrench_factors(credentials=test_credentials):
    """Test Fama-French factors fetcher."""
    params = {"region": "america", "factor": "3_factors", "interval": "annual"}

    fetcher = FamaFrenchFactorsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_us_portfolio_returns(credentials=test_credentials):
    """Test US portfolio returns fetcher."""
    params = {
        "portfolio": "5_industry_portfolios",
        "measure": "value",
        "frequency": "monthly",
    }

    fetcher = FamaFrenchUSPortfolioReturnsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_regional_portfolio_returns(credentials=test_credentials):
    """Test regional portfolio returns fetcher."""
    params = {
        "region": "europe",
    }

    fetcher = FamaFrenchRegionalPortfolioReturnsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_country_portfolio_returns(credentials=test_credentials):
    """Test country portfolio returns fetcher."""
    params = {
        "country": "japan",
    }

    fetcher = FamaFrenchCountryPortfolioReturnsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_international_index_returns(credentials=test_credentials):
    """Test international index returns fetcher."""
    params = {
        "index": "europe_ex_uk",
        "frequency": "annual",
    }

    fetcher = FamaFrenchInternationalIndexReturnsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_fama_french_breakpoints(credentials=test_credentials):
    """Test Fama-French breakpoints fetcher."""
    params = {
        "breakpoint_type": "op",
    }

    fetcher = FamaFrenchBreakpointFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
