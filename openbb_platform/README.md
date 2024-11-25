# OpenBB Platform

[![Downloads](https://static.pepy.tech/badge/openbb)](https://pepy.tech/project/openbb)
[![LatestRelease](https://badge.fury.io/py/openbb.svg)](https://github.com/OpenBB-finance/OpenBB)

| OpenBB is committed to build the future of investment research by focusing on an open source infrastructure accessible to everyone, everywhere. |
| :---------------------------------------------------------------------------------------------------------------------------------------------: |
|              ![OpenBBLogo](https://user-images.githubusercontent.com/25267873/218899768-1f0964b8-326c-4f35-af6f-ea0946ac970b.png)               |
|                                                 Check our website at [openbb.co](www.openbb.co)                                                 |

## Overview

The OpenBB Platform provides a convenient way to access raw financial data from multiple data providers. The package comes with a ready to use REST API - this allows developers from any language to easily create applications on top of OpenBB Platform.

Please find the complete documentation at [docs.openbb.co](https://docs.openbb.co/platform).

## Installation

The command below provides access to the core functionalities behind the OpenBB Platform.

```bash
pip install openbb
```

This will install the following data providers:

These packages are what will be installed when `pip install openbb` is run

| Extension Name | Description | Installation Command | Minimum Subscription Type Required |
|----------------|-------------|----------------------|------------------------------------|
| openbb-benzinga | [Benzinga](https://www.benzinga.com/apis/en-ca/) data connector | pip install openbb-benzinga | Paid |
| openbb-bls | [Bureau of Labor Statistics](https://www.bls.gov/developers/home.htm) data connector | pip install openbb-bls | Free |
| openbb-cftc | [Commodity Futures Trading Commission](https://publicreporting.cftc.gov/stories/s/r4w3-av2u) data connector | pip install openbb-cftc | Free |
| openbb-econdb | [EconDB](https://econdb.com) data connector | pip install openbb-econdb | None |
| openbb-imf | [IMF](https://data.imf.org) data connector | pip install openbb-imf | None |
| openbb-fmp | [FMP](https://site.financialmodelingprep.com/developer/) data connector | pip install openbb-fmp | Free |
| openbb-fred | [FRED](https://fred.stlouisfed.org/) data connector | pip install openbb-fred | Free |
| openbb-intrinio | [Intrinio](https://intrinio.com/pricing) data connector | pip install openbb-intrinio | Paid |
| openbb-oecd | [OECD](https://data.oecd.org/) data connector | pip install openbb-oecd | Free |
| openbb-polygon | [Polygon](https://polygon.io/) data connector | pip install openbb-polygon | Free |
| openbb-sec | [SEC](https://www.sec.gov/edgar/sec-api-documentation) data connector | pip install openbb-sec | None |
| openbb-tiingo | [Tiingo](https://www.tiingo.com/about/pricing) data connector | pip install openbb-tiingo | Free |
| openbb-tradingeconomics | [TradingEconomics](https://tradingeconomics.com/api) data connector | pip install openbb-tradingeconomics | Paid |
| openbb-yfinance | [Yahoo Finance](https://finance.yahoo.com/) data connector | pip install openbb-yfinance | None |

### Community Providers

These packages are not installed when `pip install openbb` is run.  They are available for installation separately or by running `pip install openbb[all]`

| Extension Name | Description | Installation Command | Minimum Subscription Type Required |
|----------------|-------------|----------------------|------------------------------------|
| openbb-alpha-vantage | [Alpha Vantage](https://www.alphavantage.co/) data connector | pip install openbb-alpha-vantage | Free |
| openbb-biztoc | [Biztoc](https://api.biztoc.com/#biztoc-default) News data connector | pip install openbb-biztoc | Free |
| openbb-cboe | [Cboe](https://www.cboe.com/delayed_quotes/) data connector | pip install openbb-cboe | None |
| openbb-ecb | [ECB](https://data.ecb.europa.eu/) data connector | pip install openbb-ecb | None |
| openbb-federal-reserve | [Federal Reserve](https://www.federalreserve.gov/) data connector | pip install openbb-federal-reserve | None |
| openbb-finra | [FINRA](https://www.finra.org/finra-data) data connector | pip install openbb-finra | None / Free |
| openbb-finviz | [Finviz](https://finviz.com) data connector | pip install openbb-finviz | None |
| openbb-government-us | [US Government](https://data.gov) data connector | pip install openbb-us-government | None |
| openbb-nasdaq | [Nasdaq Data Link](https://data.nasdaq.com/) connector | pip install openbb-nasdaq | None / Free |
| openbb-seeking-alpha | [Seeking Alpha](https://seekingalpha.com/) data connector | pip install openbb-seeking-alpha | None |
| openbb-stockgrid | [Stockgrid](https://stockgrid.io) data connector | pip install openbb-stockgrid | None |
| openbb-tmx | [TMX](https://money.tmx.com) data connector | pip install openbb-tmx | None |
| openbb-tradier | [Tradier](https://tradier.com) data connector | pip install openbb-tradier | None |
| openbb-wsj | [Wall Street Journal](https://www.wsj.com/) data connector | pip install openbb-wsj | None |
To install extensions that expand the core functionalities specify the extension name or use `all` to install all.

```bash
# Install a single extension, e.g. openbb-charting and yahoo finance
pip install openbb[charting]
pip install openbb-yfinance
```

Alternatively, you can install all extensions at once.

```bash
pip install openbb[all]
```

> Note: These instruction are specific to v4. For installation instructions and documentation for v3 go to our [website](https://docs.openbb.co/sdk).

## Python

```python
>>> from openbb import obb
>>> output = obb.equity.price.historical("AAPL")
>>> df = output.to_dataframe()
>>> df.head()
              open    high     low  ...  change_percent             label  change_over_time
date                                ...
2022-09-19  149.31  154.56  149.10  ...         3.46000  September 19, 22          0.034600
2022-09-20  153.40  158.08  153.08  ...         2.28000  September 20, 22          0.022800
2022-09-21  157.34  158.74  153.60  ...        -2.30000  September 21, 22         -0.023000
2022-09-22  152.38  154.47  150.91  ...         0.23625  September 22, 22          0.002363
2022-09-23  151.19  151.47  148.56  ...        -0.50268  September 23, 22         -0.005027

[5 rows x 12 columns]
```

## API keys

To fully leverage the OpenBB Platform you need to get some API keys to connect with data providers. Here are the 3 options on where to set them:

1. OpenBB Hub
2. Runtime
3. Local file

### 1. OpenBB Hub

Set your keys at [OpenBB Hub](https://my.openbb.co/app/platform/credentials) and get your personal access token from <https://my.openbb.co/app/platform/pat> to connect with your account.

```python
>>> from openbb import obb
>>> openbb.account.login(pat="OPENBB_PAT")

>>> # Persist changes in OpenBB Hub
>>> obb.account.save()
```

### 2. Runtime

```python
>>> from openbb import obb
>>> obb.user.credentials.fmp_api_key = "REPLACE_ME"
>>> obb.user.credentials.polygon_api_key = "REPLACE_ME"

>>> # Persist changes in ~/.openbb_platform/user_settings.json
>>> obb.account.save()
```

### 3. Local file

You can specify the keys directly in the `~/.openbb_platform/user_settings.json` file.

Populate this file with the following template and replace the values with your keys:

```json
{
  "credentials": {
    "fmp_api_key": "REPLACE_ME",
    "polygon_api_key": "REPLACE_ME",
    "benzinga_api_key": "REPLACE_ME",
    "fred_api_key": "REPLACE_ME"
  }
}
```

## REST API

The OpenBB Platform comes with a ready to use REST API built with FastAPI. Start the application using this command:

```bash
uvicorn openbb_core.api.rest_api:app --host 0.0.0.0 --port 8000 --reload
```

API documentation is found under "/docs", from the root of the server address, and is viewable in any browser supporting HTTP over localhost, such as Chrome.

Check `openbb-core` [README](https://pypi.org/project/openbb-core/) for additional info.

## Install for development

To develop the OpenBB Platform you need to have the following:

- Git
- Python 3.9 or higher
- Virtual Environment with `poetry` installed
  - To install these packages activate your virtual environment and run `pip install poetry toml`

How to install the platform in editable mode?

  1. Activate your virtual environment
  1. Navigate into the `openbb_platform` folder
  1. Run `python dev_install.py` to install the packages in editable mode
