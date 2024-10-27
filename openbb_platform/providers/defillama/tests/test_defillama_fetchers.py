"""Unit tests for DeFiLlama provider modules."""

import pytest
from openbb_core.app.service.user_service import UserService
from openbb_defillama.models.coins_block_timestamp import (
    DeFiLlamaCoinsBlockTimestampFetcher,
)
from openbb_defillama.models.coins_change import DeFiLlamaCoinsChangeFetcher
from openbb_defillama.models.coins_chart import DeFiLlamaCoinsChartFetcher
from openbb_defillama.models.coins_current import DeFiLlamaCoinsCurrentFetcher
from openbb_defillama.models.coins_first import DeFiLlamaCoinsFirstFetcher
from openbb_defillama.models.coins_historical import DeFiLlamaCoinsHistoricalFetcher
from openbb_defillama.models.fees_overview import DeFiLlamaFeesOverviewFetcher
from openbb_defillama.models.fees_summary import DeFiLlamaFeesSummaryFetcher
from openbb_defillama.models.revenue_overview import DeFiLlamaRevenueOverviewFetcher
from openbb_defillama.models.revenue_summary import DeFiLlamaRevenueSummaryFetcher
from openbb_defillama.models.stablecoins_charts import DeFiLlamaStablecoinsChartsFetcher
from openbb_defillama.models.stablecoins_current import (
    DeFiLlamaStablecoinsCurrentFetcher,
)
from openbb_defillama.models.stablecoins_distribution import (
    DeFiLlamaStablecoinsDistributionFetcher,
)
from openbb_defillama.models.stablecoins_historical import (
    DeFiLlamaStablecoinsHistoricalFetcher,
)
from openbb_defillama.models.stablecoins_list import DeFiLlamaStablecoinsListFetcher
from openbb_defillama.models.tvl_chains import DeFiLlamaTvlChainsFetcher
from openbb_defillama.models.tvl_current import DeFiLlamaTvlCurrentFetcher
from openbb_defillama.models.tvl_historical import DeFiLlamaTvlHistoricalFetcher
from openbb_defillama.models.volumes_overview import DeFiLlamaVolumesOverviewFetcher
from openbb_defillama.models.volumes_summary import DeFiLlamaVolumesSummaryFetcher
from openbb_defillama.models.yields_historical import DeFiLlamaYieldsHistoricalFetcher
from openbb_defillama.models.yields_pools import DeFiLlamaYieldsPoolsFetcher

test_credentials = UserService().default_user_settings.credentials.model_dump(
    mode="json"
)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("token", "MOCK_TOKEN"),
        ],
    }


@pytest.mark.record_http
def test_defillama_coins_block_timestamp_fetcher(credentials=test_credentials):
    params = {
        "chain": "ethereum",
        "timestamp": 1704047400,
    }

    fetcher = DeFiLlamaCoinsBlockTimestampFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_defillama_coins_change_fetcher(credentials=test_credentials):
    params = {
        "token": "coingecko:ethereum",
        "timestamp": 1704047400,
        "look_forward": False,
        "period": "24h",
    }

    fetcher = DeFiLlamaCoinsChangeFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_defillama_coins_chart_fetcher(credentials=test_credentials):
    params = {
        "token": "coingecko:ethereum",
        "start_date": 1704047400,
    }

    fetcher = DeFiLlamaCoinsChartFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_defillama_coins_current_fetcher(credentials=test_credentials):
    params = {
        "token": "coingecko:ethereum",
    }

    fetcher = DeFiLlamaCoinsCurrentFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_defillama_coins_first_fetcher(credentials=test_credentials):
    params = {
        "token": "coingecko:ethereum",
    }

    fetcher = DeFiLlamaCoinsFirstFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_defillama_coins_historical_fetcher(credentials=test_credentials):
    params = {
        "token": "coingecko:ethereum",
        "timestamp": 1704047400,
    }

    fetcher = DeFiLlamaCoinsHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_defillama_fees_overview_fetcher(credentials=test_credentials):
    params = {}

    fetcher = DeFiLlamaFeesOverviewFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_defillama_fees_summary_fetcher(credentials=test_credentials):
    params = {
        "protocol": "litecoin",
    }

    fetcher = DeFiLlamaFeesSummaryFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_defillama_revenue_overview_fetcher(credentials=test_credentials):
    params = {}

    fetcher = DeFiLlamaRevenueOverviewFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_defillama_revenue_summary_fetcher(credentials=test_credentials):
    params = {
        "protocol": "litecoin",
    }

    fetcher = DeFiLlamaRevenueSummaryFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_defillama_stablecoins_charts_fetcher(credentials=test_credentials):
    params = {}

    fetcher = DeFiLlamaStablecoinsChartsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_defillama_stablecoins_current_fetcher(credentials=test_credentials):
    params = {}

    fetcher = DeFiLlamaStablecoinsCurrentFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_defillama_stablecoins_distribution_fetcher(credentials=test_credentials):
    params = {
        "stablecoin": "1",
    }

    fetcher = DeFiLlamaStablecoinsDistributionFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_defillama_stablecoins_historical_fetcher(credentials=test_credentials):
    params = {}

    fetcher = DeFiLlamaStablecoinsHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_defillama_stablecoins_list_fetcher(credentials=test_credentials):
    params = {}

    fetcher = DeFiLlamaStablecoinsListFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_defillama_tvl_chains_fetcher(credentials=test_credentials):
    params = {}

    fetcher = DeFiLlamaTvlChainsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_defillama_tvl_current_fetcher(credentials=test_credentials):
    params = {
        "symbol": "uniswap",
    }

    fetcher = DeFiLlamaTvlCurrentFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_defillama_tvl_historical_fetcher(credentials=test_credentials):
    params = {}

    fetcher = DeFiLlamaTvlHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_defillama_volumes_overview_fetcher(credentials=test_credentials):
    params = {}

    fetcher = DeFiLlamaVolumesOverviewFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_defillama_volumes_summary_fetcher(credentials=test_credentials):
    params = {
        "protocol": "uniswap",
    }

    fetcher = DeFiLlamaVolumesSummaryFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_defillama_yields_historical_fetcher(credentials=test_credentials):
    params = {
        "pool_id": "747c1d2a-c668-4682-b9f9-296708a3dd90",
    }

    fetcher = DeFiLlamaYieldsHistoricalFetcher()
    result = fetcher.test(params, credentials)
    assert result is None


@pytest.mark.record_http
def test_defillama_yields_pools_fetcher(credentials=test_credentials):
    params = {}

    fetcher = DeFiLlamaYieldsPoolsFetcher()
    result = fetcher.test(params, credentials)
    assert result is None
