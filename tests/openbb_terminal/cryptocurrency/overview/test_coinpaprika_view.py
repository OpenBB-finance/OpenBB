import pytest
from pandas import DataFrame

from openbb_terminal.cryptocurrency.overview import coinpaprika_view


@pytest.mark.record_verify_screen
def test_display_global_market(mocker):
    mocker.patch(
        "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_global_info",
        return_value=DataFrame(
            {
                "active_cryptocurrencies": [10800],
                "upcoming_icos": [0],
                "ongoing_icos": [49],
                "ended_icos": [3380],
                "markets": [713],
                "market_cap_change_percentage_24h_usd": [3.0877],
                "btc_market_cap_in_pct": [44.594],
                "eth_market_cap_in_pct": [19.027],
                "Value": [100000000.0],
            }
        ),
    )

    coinpaprika_view.display_global_market()


@pytest.mark.record_verify_screen
def test_display_all_coins_market_info(mocker):
    mocker.patch(
        "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_coins_market_info",
        return_value=DataFrame(
            {
                "id": ["btc-bitcoin"],
                "name": ["Bitcoin"],
                "symbol": ["BTC"],
                "rank": [1],
                "circulating_supply": [18700000.0],
                "total_supply": [18700000.0],
                "max_supply": [21000000.0],
                "beta_value": [0.0],
                "last_updated": ["2021-01-10T00:00:00Z"],
                "price": [30000.0],
            }
        ),
    )

    coinpaprika_view.display_all_coins_market_info(symbol="BTC")


@pytest.mark.record_verify_screen
def test_display_all_coins_info(mocker):
    mocker.patch(
        "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_coins_info",
        return_value=DataFrame(
            {
                "id": ["btc-bitcoin"],
                "name": ["Bitcoin"],
                "symbol": ["BTC"],
                "rank": [1],
                "circulating_supply": [18700000.0],
                "total_supply": [18700000.0],
                "max_supply": [21000000.0],
                "beta_value": [0.0],
                "last_updated": ["2021-01-10T00:00:00Z"],
                "price": [30000.0],
            }
        ),
    )

    coinpaprika_view.display_all_coins_info(symbol="BTC")


@pytest.mark.record_verify_screen
def test_display_all_exchanges(mocker):
    mocker.patch(
        "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_list_of_exchanges",
        return_value=DataFrame(
            {
                "id": ["binance"],
                "name": ["Binance"],
                "year_established": [2017],
                "country": ["Hong Kong"],
                "description": [
                    "Binance is a cryptocurrency exchange that provides a platform for\
                     trading various cryptocurrencies.\
                     It is one of the fastest growing and most popular cryptocurrency\
                     exchanges in the world. \
                     All trading pairs can be found on the centralized exchange. \
                     Binance is based in Hong Kong and was founded in 2017 by\
                     Changpeng Zhao and Yi He."
                ],
                "url": ["https://www.binance.com/"],
                "has_trading_incentive": [False],
                "fiat_currencies": ["USD"],
                "trust_score": [9],
                "trust_score_rank": [1],
                "trade_volume_24h_btc": [0.0],
                "trade_volume_24h_btc_normalized": [0.0],
            }
        ),
    )

    coinpaprika_view.display_all_exchanges(symbol="BTC")


@pytest.mark.record_verify_screen
def test_display_exchange_markets(mocker):
    mocker.patch(
        "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_exchanges_market",
        return_value=DataFrame(
            {
                "id": ["btc-bitcoin"],
                "name": ["Bitcoin"],
                "market_url": ["https://coinpaprika.com/market/"],
                "symbol": ["BTC"],
                "rank": [1],
                "circulating_supply": [18700000.0],
                "total_supply": [18700000.0],
                "max_supply": [21000000.0],
                "beta_value": [0.0],
                "last_updated": ["2021-01-10T00:00:00Z"],
                "price": [30000.0],
            }
        ),
    )

    coinpaprika_view.display_exchange_markets()


@pytest.mark.record_verify_screen
def test_display_all_platforms(mocker):
    mocker.patch(
        "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_all_contract_platforms",
        return_value=DataFrame(
            {
                "id": ["binance"],
                "name": ["Binance"],
                "year_established": [2017],
                "country": ["Hong Kong"],
                "description": [
                    "Binance is a cryptocurrency exchange that provides a platform for\
                     trading various cryptocurrencies.\
                     It is one of the fastest growing and most popular cryptocurrency\
                     exchanges in the world. \
                     All trading pairs can be found on the centralized exchange. \
                     Binance is based in Hong Kong and was founded in 2017 by\
                     Changpeng Zhao and Yi He."
                ],
                "url": ["https://www.binance.com/"],
                "has_trading_incentive": [False],
                "fiat_currencies": ["USD"],
                "trust_score": [9],
                "trust_score_rank": [1],
                "trade_volume_24h_btc": [0.0],
                "trade_volume_24h_btc_normalized": [0.0],
            }
        ),
    )

    coinpaprika_view.display_all_platforms()


@pytest.mark.record_verify_screen
def test_display_contracts(mocker):
    mocker.patch(
        "openbb_terminal.cryptocurrency.overview.coinpaprika_model.get_contract_platform",
        return_value=DataFrame(
            {
                "id": ["btc-bitcoin"],
                "name": ["Bitcoin"],
                "market_url": ["https://coinpaprika.com/market/"],
                "symbol": ["BTC"],
                "rank": [1],
                "circulating_supply": [18700000.0],
                "total_supply": [18700000.0],
                "max_supply": [21000000.0],
                "beta_value": [0.0],
                "last_updated": ["2021-01-10T00:00:00Z"],
                "price": [30000.0],
            }
        ),
    )

    coinpaprika_view.display_contracts(symbol="BTC")
