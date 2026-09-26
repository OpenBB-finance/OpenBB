"""Test the JODI fetchers against cassettes synthesized from trimmed fixtures.

Every test executes the full pipeline against a cold cache: the download
replays offline from an in-memory cassette, then ingests and queries.
"""

from datetime import date

import pytest
from openbb_core.app.service.user_service import UserService

from openbb_jodi.models.gas_balance import JodiGasBalanceFetcher
from openbb_jodi.models.gas_demand import JodiGasDemandFetcher
from openbb_jodi.models.gas_exports import JodiGasExportsFetcher
from openbb_jodi.models.gas_imports import JodiGasImportsFetcher
from openbb_jodi.models.gas_production import JodiGasProductionFetcher
from openbb_jodi.models.gas_stocks import JodiGasStocksFetcher
from openbb_jodi.models.oil_balance import JodiOilBalanceFetcher
from openbb_jodi.models.oil_demand import JodiOilDemandFetcher
from openbb_jodi.models.oil_demand_by_product import JodiOilDemandByProductFetcher
from openbb_jodi.models.oil_exports import JodiOilExportsFetcher
from openbb_jodi.models.oil_imports import JodiOilImportsFetcher
from openbb_jodi.models.oil_production import JodiOilProductionFetcher
from openbb_jodi.models.oil_stocks import JodiOilStocksFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)

DATES = {"start_date": date(2024, 1, 1), "end_date": date(2024, 3, 31)}


@pytest.mark.usefixtures("jodi_cassette")
def test_jodi_oil_balance_fetcher(credentials=test_credentials):
    """Test the JODI oil balance fetcher."""
    params = {
        "country": "united_states",
        "product": "crude_oil",
        "unit": "kbbl",
        **DATES,
    }
    fetcher = JodiOilBalanceFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.usefixtures("jodi_cassette")
def test_jodi_oil_production_fetcher(credentials=test_credentials):
    """Test the JODI oil production fetcher."""
    params = {"country": "united_states,saudi_arabia", "unit": "kbd", **DATES}
    fetcher = JodiOilProductionFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.usefixtures("jodi_cassette")
def test_jodi_oil_demand_fetcher(credentials=test_credentials):
    """Test the JODI oil demand fetcher."""
    params = {"country": "united_states", "product": "gasoline", **DATES}
    fetcher = JodiOilDemandFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.usefixtures("jodi_cassette")
def test_jodi_oil_demand_by_product_fetcher(credentials=test_credentials):
    """Test the JODI oil demand by product fetcher."""
    params = {"country": "united_states", "unit": "kbd", **DATES}
    fetcher = JodiOilDemandByProductFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.usefixtures("jodi_cassette")
def test_jodi_oil_imports_fetcher(credentials=test_credentials):
    """Test the JODI oil imports fetcher."""
    params = {"country": "united_states", "product": "crude_oil", **DATES}
    fetcher = JodiOilImportsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.usefixtures("jodi_cassette")
def test_jodi_oil_exports_fetcher(credentials=test_credentials):
    """Test the JODI oil exports fetcher."""
    params = {"country": "saudi_arabia,united_states", "product": "crude_oil", **DATES}
    fetcher = JodiOilExportsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.usefixtures("jodi_cassette")
def test_jodi_oil_stocks_fetcher(credentials=test_credentials):
    """Test the JODI oil stocks fetcher."""
    params = {"country": "united_states", "unit": "kbbl", **DATES}
    fetcher = JodiOilStocksFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.usefixtures("jodi_cassette")
def test_jodi_gas_balance_fetcher(credentials=test_credentials):
    """Test the JODI gas balance fetcher."""
    params = {"country": "united_states", "unit": "m3", **DATES}
    fetcher = JodiGasBalanceFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.usefixtures("jodi_cassette")
def test_jodi_gas_production_fetcher(credentials=test_credentials):
    """Test the JODI gas production fetcher."""
    params = {"country": "united_states,norway", "unit": "m3", **DATES}
    fetcher = JodiGasProductionFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.usefixtures("jodi_cassette")
def test_jodi_gas_demand_fetcher(credentials=test_credentials):
    """Test the JODI gas demand fetcher."""
    params = {"country": "united_states", "measure": "observed", **DATES}
    fetcher = JodiGasDemandFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.usefixtures("jodi_cassette")
def test_jodi_gas_imports_fetcher(credentials=test_credentials):
    """Test the JODI gas imports fetcher."""
    params = {"country": "united_states", "flow": "pipeline", **DATES}
    fetcher = JodiGasImportsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.usefixtures("jodi_cassette")
def test_jodi_gas_exports_fetcher(credentials=test_credentials):
    """Test the JODI gas exports fetcher."""
    params = {"country": "qatar", "flow": "lng", **DATES}
    fetcher = JodiGasExportsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.usefixtures("jodi_cassette")
def test_jodi_gas_stocks_fetcher(credentials=test_credentials):
    """Test the JODI gas stocks fetcher."""
    params = {"country": "united_states", "unit": "m3", **DATES}
    fetcher = JodiGasStocksFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
