---
title: Set API Keys
sidebar_position: 1
---

API keys can be managed directly from the SDK environment. If there is already a Terminal installation configured with API keys, they will be recognized by the SDK. Their status can be verified with the line of code below.

```python
from openbb_terminal.sdk import openbb
openbb.keys.mykeys(show = True)
```

Removing `show = True` from the syntax will hide the values for the keys, as shown in the screenshot below.

| API                       | Key     |
|:--------------------------|:--------|
| BINANCE_KEY               | ******* |
| BINANCE_SECRET            | ******* |
| BITQUERY_KEY              | ******* |
| CMC_KEY                   | ******* |
| COINBASE_KEY              | ******* |
| COINBASE_PASS_PHRASE      | ******* |
| COINBASE_SECRET           | ******* |
| COINGLASS_KEY             | ******* |
| CRYPTO_PANIC_KEY          | ******* |
| EODHD_KEY                 | ******* |
| ETHPLORER_KEY             | ******* |

Individual keys are entered like this example:

```python
obb.keys.fred(
    key = 'replace_me',
    persist = True,
)
```

The required fields for each source will vary, print the docstring for each to know the required inputs.

```python
help(openbb.keys.reddit)
```


```py
    Help on Operation in module openbb_terminal.core.library.operation:

    <openbb_terminal.core.library.operation.Operation object>
    Set Reddit key

    Parameters
    ----------
    client_id: str
        Client ID
    client_secret: str
        Client secret
    password: str
        User assword
    username: str
        User username
    useragent: str
        User useragent
    persist: bool
        If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
```


<details>
  <summary>API Reference (expand to see list of API key references)</summary>

| Key Name   | Description                              | URL                                                                                |
| :--------- | :--------------------------------------- | :--------------------------------------------------------------------------------- |
| av         | AlphaVantage                             | https://www.alphavantage.co/support/#api-key                                       |
| fmp        | Financial Modelling Prep                 | https://site.financialmodelingprep.com/developer/docs/                             |
| quandl     | Quandl                                   | https://www.quandl.com                                                             |
| polygon    | Polygon                                  | https://polygon.io                                                                 |
| fred       | Federal Reserve Economic Database (FRED) | https://fred.stlouisfed.org                                                        |
| news       | News API                                 | https://newsapi.org/                                                               |
| tradier    | Tradier                                  | https://developer.tradier.com                                                      |
| cmc        | CoinMarketCap                            | https://coinmarketcap.com/                                                         |
| finnhub    | Finnhub                                  | https://finnhub.io/                                                                |
| iex        | IEX Cloud                                | https://iexcloud.io/                                                               |
| reddit     | Reddit                                   | https://www.reddit.com/wiki/api                                                    |
| twitter    | Twitter                                  | https://developer.twitter.com                                                      |
| rh         | Robinhood                                | https://robinhood.com/us/en/                                                       |
| degiro     | DeGiro                                   | https://www.degiro.com/                                                            |
| oanda      | Oanda                                    | https://developer.oanda.com                                                        |
| binance    | Binance                                  | https://binance.com                                                                |
| bitquery   | Bitquery                                 | https://bitquery.io/                                                               |
| si         | Sentiment Investor                       | https://sentimentinvestor.com                                                      |
| cb         | Coinbase                                 | https://help.coinbase.com/en/exchange/managing-my-account/how-to-create-an-api-key |
| walert     | Whale Alert                              | https://docs.whale-alert.io/                                                       |
| glassnode  | Glassnode                                | https://docs.glassnode.com/basic-api/api-key#how-to-get-an-api-key/                |
| coinglass  | Coinglass                                | https://coinglass.github.io/API-Reference/#api-key                                 |
| ethplorer  | Ethplorer                                | https://github.com/EverexIO/Ethplorer/wiki/Ethplorer-API                           |
| smartstake | Smartstake                               | https://www.smartstake.io                                                          |
| github     | GitHub                                   | https://docs.github.com/en/rest/guides/getting-started-with-the-rest-api           |
| messari    | Messari                                  | https://messari.io/api/docs                                                        |
| cpanic     | Crypto Panic                             | https://cryptopanic.com/developers/api/                                            |
| eodhd      | EODHD                                    | https://eodhistoricaldata.com/                                                     |
| santiment  | Santiment                                | https://app.santiment.net/                                                         |
| shroom     | ShroomDK                                 | https://sdk.flipsidecrypto.xyz/shroomdk                                            |
| tokenterminal    | Token Terminal                     | https://tokenterminal.com/                                                         |
</details>

### Importing Keys as a Variable

In cases where API credentials must be passed to another process, use the following import statement:

```python
from openbb_terminal import config_terminal as cfg
```

Values can then be passed to a request URL as a variable, `f"{cfg.API_KEY_QUANDL}"`

The code block below will authorize Quandl to request data from Nasdaq Data Link. The series in the example is for the historical price of gold.

```python
import quandl
from openbb_terminal import config_terminal as cfg

gold = quandl.get("LBMA/GOLD", collapse="monthly", transform="", index_col=0, order="desc", parse_dates=True, authtoken=f"{cfg.API_KEY_QUANDL}")
```

| Date                |   USD (AM) |   USD (PM) |   GBP (AM) |   GBP (PM) |   EURO (AM) |   EURO (PM) |
|:--------------------|-----------:|-----------:|-----------:|-----------:|------------:|------------:|
| 2022-11-30 00:00:00 |    1757.35 |    1768.9  |    1491.46 |    1506.57 |     1704.98 |     1714.06 |
| 2022-10-31 00:00:00 |    1638.85 |    1639    |    1419.74 |    1425.27 |     1649.5  |     1656.87 |
| 2022-09-30 00:00:00 |    1672.75 |    1671.75 |    1495.94 |    1502.4  |     1703.7  |     1710.53 |
| 2022-08-31 00:00:00 |    1712.4  |    1715.9  |    1472.15 |    1478.08 |     1713.6  |     1715.21 |
| 2022-07-31 00:00:00 |    1758.9  |    1753.4  |    1447.4  |    1451.64 |     1724.07 |     1725.7  |

### Creating a Backup Copy

To make a backup file containing all stored keys, use the code block below.

```python
df_keys = openbb.keys.mykeys(show = True)
df_keys.to_csv('backup.csv')
```
