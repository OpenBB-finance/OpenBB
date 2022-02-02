# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.due_diligence import coinpaprika_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("start", "mock_start"),
            ("end", "mock_end"),
        ]
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, kwargs",
    [
        ("get_coin", dict()),
        ("get_coin_twitter_timeline", dict()),
        ("get_coin_events_by_id", dict()),
        ("get_coin_exchanges_by_id", dict()),
        ("get_coin_markets_by_id", dict()),
        ("get_ohlc_historical", dict()),
        ("get_tickers_info_for_coin", dict()),
        ("validate_coin", dict(coin="btc-bitcoin", coins_dct={"btc-bitcoin": "BTC"})),
        ("basic_coin_info", dict()),
    ],
)
def test_call_func(func, kwargs, recorder):
    result = getattr(coinpaprika_model, func)(**kwargs)

    if isinstance(result, tuple):
        recorder.capture_list(result)
    else:
        recorder.capture(result)
