from pandas import DataFrame

from openbb_terminal.cryptocurrency.overview import cryptopanic_view


# mock the get_news function
def test_display_news(mocker):
    mocker.patch(
        "openbb_terminal.cryptocurrency.overview.cryptopanic_model.get_news",
        return_value=DataFrame.from_dict(
            {
                "id": "5ff9b5b5b3c3b0001c7b0b1a",
                "title": "Bitcoin Price Analysis: BTC/USD bulls eye $40,000",
                "link": "https://www.fxstreet.com/cryptocurrencies/news/\
                    bitcoin-price-analysis-btc-usd-bulls-eye-40000-202101100000",
                "domain": "fxstreet.com",
                "created_at": "2021-01-10T00:00:00Z",
                "source": {
                    "id": "cryptopanic",
                    "name": "CryptoPanic",
                    "domain": "cryptopanic.com",
                    "logo": "https://cryptopanic.com/static/img/logo.png",
                },
            },
            orient="index",
        ).T,
    )
    cryptopanic_view.display_news(limit=2)
