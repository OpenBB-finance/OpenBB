# OpenBB Platform

[![Downloads](https://static.pepy.tech/badge/openbb)](https://pepy.tech/project/openbb)
[![LatestRelease](https://badge.fury.io/py/openbb.svg)](https://github.com/OpenBB-finance/OpenBB)

| OpenBB is committed to build the future of investment research by focusing on an open source infrastructure accessible to everyone, everywhere. |
| :---------------------------------------------------------------------------------------------------------------------------------------------: |
|              ![OpenBBLogo](https://user-images.githubusercontent.com/25267873/218899768-1f0964b8-326c-4f35-af6f-ea0946ac970b.png)               |
|                                                 Check our website at [openbb.co](https://www.openbb.co)                                         |

## Overview

The OpenBB Platform provides a convenient way to access raw financial data from multiple data providers. The package comes with a ready to use REST API - this allows developers from any language to easily create applications on top of OpenBB Platform.

Please find the complete documentation at [docs.openbb.co](https://docs.openbb.co/platform).

## Installation

### PyPI

The command below provides access to the core functionalities behind the OpenBB Platform, and a selection of sources.

```bash
pip install openbb
```

This will install the core, router modules, and the following data providers:

| Extension Name | Description | Installation Command | Minimum Subscription Type Required |
|----------------|-------------|----------------------|------------------------------------|
| openbb-benzinga | [Benzinga](https://www.benzinga.com/apis/en-ca/) data connector | pip install openbb-benzinga | Paid |
| openbb-bls | [Bureau of Labor Statistics](https://www.bls.gov/developers/home.htm) data connector | pip install openbb-bls | Free |
| openbb-congress-gov | [US Congress API](https://api.congress.gov/sign-up/) data connector | pip install openbb-congress-gov | Free |
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

### Extras

These packages are not installed when `pip install openbb` is run.  They are available for installation separately or by running `pip install openbb[all]`.

| Extension Name | Description | Installation Command | Minimum Subscription Type Required |
|----------------|-------------|----------------------|------------------------------------|
| openbb-mcp-server | Run the OpenBB Platform as a [MCP server](https://pypi.org/project/openbb-mcp-server/) | pip install openbb-mcp-server | None |
| openbb-charting | Integrated [Plotly charting library](https://pypi.org/project/openbb-charting/) and dedicated window rendering. | pip install openbb-charting | None |
| openbb-alpha-vantage | [Alpha Vantage](https://www.alphavantage.co/) data connector | pip install openbb-alpha-vantage | Free |
| openbb-biztoc | [Biztoc](https://api.biztoc.com/#biztoc-default) News data connector | pip install openbb-biztoc | Free |
| openbb-cboe | [Cboe](https://www.cboe.com/delayed_quotes/) data connector | pip install openbb-cboe | None |
| openbb-deribit | [Deribit](https://docs.deribit.com/) data connector | pip install openbb-deribit | None | - |
| openbb-ecb | [ECB](https://data.ecb.europa.eu/) data connector | pip install openbb-ecb | None |
| openbb-famafrench | [Ken French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) connector | pip install openbb-famafrench | None | - |
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


```bash
pip install openbb-equity openbb-yfinance
```

## Python

```python
>>> from openbb import obb
>>> output = obb.equity.price.historical("AAPL")
>>> df = output.to_dataframe()
>>> df.tail()
```

| date       |    open |   high |    low |   close |
|:-----------|--------:|-------:|-------:|--------:|
| 2025-09-30 | 254.86  | 255.92 | 253.11 |  254.63 |
| 2025-10-01 | 255.04  | 258.79 | 254.93 |  255.45 |
| 2025-10-02 | 256.58  | 258.18 | 254.15 |  257.13 |
| 2025-10-03 | 254.67  | 259.24 | 253.95 |  258.02 |
| 2025-10-06 | 257.945 | 259.07 | 255.05 |  256.69 |


## API keys

To fully leverage the OpenBB Platform you need to get some API keys to connect with data providers (listed above).

Here's how to set them:

### Local file

Specify the keys directly in the `~/.openbb_platform/user_settings.json` file.

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

### Runtime

Credentials can be set for the current session only, using the Python interface.

```python
>>> from openbb import obb
>>> obb.user.credentials.fred_api_key = "REPLACE_ME"
>>> obb.user.credentials.polygon_api_key = "REPLACE_ME"
```

Go to the [documentation](https://docs.openbb.co/platform/settings/user_settings/api_keys) for more details.

## REST API

The OpenBB Platform comes with a ready-to-use REST API built with FastAPI. Start the application using this command:

```bash
uvicorn openbb_core.api.rest_api:app --host 0.0.0.0 --port 8000 --reload
```

API documentation is found under "/docs", from the root of the server address, and is viewable in any browser supporting HTTP over localhost, such as Chrome.

See the [documentation](https://docs.openbb.co/platform/settings/system_settings#api-settings) for runtime settings and configurations.

## Local Development

To develop with the source code, you need to have the following:

- Git
- Python 3.10 - 3.13.
- Virtual Environment with `poetry` installed.
  - Activate your virtual environment and run, `pip install poetry`.
- A local copy of the [GitHub repository](https://github.com/OpenBB-finance/OpenBB.git)

Install the repository for local development by using the installation script.

  1. Activate your virtual environment.
  2. Navigate into the `openbb_platform` folder.
  3. Run `python dev_install.py -e` to install all packages in editable mode.

See the [documentation](https://docs.openbb.co/platform/developer_guide/architecture_overview) for an overview of the architecture and how to get started building your own extensions.
