# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.cryptocurrency import crypto_views


@pytest.mark.vcr
@pytest.mark.parametrize(
    "query, source, key",
    [
        [
            "btc",
            "CoinGecko",
            "id",
        ],
        [
            "bt",
            "CoinGecko",
            "symbol",
        ],
        # [ TOO SLOW
        #     "doge",
        #     "CoinGecko",
        #     "name",
        # ],
        [
            "btc",
            "CoinPaprika",
            "id",
        ],
        [
            "bt",
            "CoinPaprika",
            "symbol",
        ],
        [
            "doge",
            "CoinPaprika",
            "name",
        ],
        # [ TOO SLOW
        #     "btc",
        #     "Binance",
        #     "id",
        # ],
        [
            "bt",
            "Binance",
            "id",
        ],
        [
            "doge",
            "Binance",
            "id",
        ],
        # [ TOO SLOW
        #     "btc",
        #     "Coinbase",
        #     "id",
        # ],
        [
            "bt",
            "Coinbase",
            "symbol",
        ],
        [
            "doge",
            "Coinbase",
            "name",
        ],
    ],
)
@pytest.mark.record_stdout
def test_find(query, source, key):
    crypto_views.find(query=query, source=source, key=key)
