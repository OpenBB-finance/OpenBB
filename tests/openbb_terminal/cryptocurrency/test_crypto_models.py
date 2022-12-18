# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.cryptocurrency import crypto_models


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
        [
            "doge",
            "CoinGecko",
            "name",
        ],
        [
            "bitcoin",
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
        [
            "btc",
            "Binance",
            "id",
        ],
        [
            "polka",
            "Binance",
            "id",
        ],
        [
            "doge",
            "Binance",
            "id",
        ],
        [
            "btc",
            "Coinbase",
            "id",
        ],
        [
            "polka",
            "Coinbase",
            "id",
        ],
        [
            "doge",
            "Coinbase",
            "id",
        ],
    ],
)
def test_find(query, source, key, recorder):

    result_df = getattr(crypto_models, "find")(query=query, source=source, key=key)

    assert not result_df.empty
    recorder.capture(result_df)
