---
title: Data Extensions
sidebar_position: 1
description: Learn about the OpenBB Platform and its extension framework that allows
  seamless integration of modules like 'openbb-yfinance'. Discover how installations
  and removals automatically update the router when the Python interpreter is refreshed.
  This page lists the data provider extensions available.
keywords:
- OpenBB Platform
- extension framework
- yFinance
- install openbb-yfinance
- Python interpreter
- PyPI
- openbb-qa
- data
- vendors
- providers
- install
- free
- subscription
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Data - Extensions | OpenBB Platform Docs" />

Data extensions will expand the breadth and coverage of the data available in the OpenBB Platform.  Each source (provider) is its own independent extension, even if there is only one endpoint accessible.  This allows every data source to be inserted or removed, at any time, without distrubing the operation of the Core components.

Functions will appear in the Python Interface and Fast API only if a supported provider, for that specific endpoint, is installed.  Additional Python libraries will be installed, where required, by the extension.

## Provider Coverage

The total installed coverage can be determined through the Python interface, as a dictionary.

```python
from openbb import obb
obb.coverage.providers
```

## Installation

All data extensions are installed with similar syntax.  Published data extensions will have names beginning with `openbb`.  For example, yFinance.

```console
pip install openbb-yfinance
```

Additions and removals update the router automatically to reflect the changes when the Python interpreter is refreshed.  Below is a list of data provider extensions.

Uninstall any extension with `pip uninstall`.

```console
pip uninstall openbb-yfinance
```

## Available Data Extensions

| Extension Name | Description | Installation Command | Core/Community | Minimum Subscription Type Required |
|:-----------------|:-----------:|:-------------------:|:-----------------:|--------------------------------------:|
| openbb-alpha-vantage | [Alpha Vantage](https://www.alphavantage.co/) data connector. | pip install openbb-alpha-vantage | Community | Free |
| openbb-benzinga | [Benzinga](https://www.benzinga.com/apis/en-ca/) data connector. | pip install openbb-benzinga | Core | Paid |
| openbb-biztoc | [Biztoc](https://api.biztoc.com/#biztoc-default) News data connector. | pip install openbb-biztoc | Community | Free |
| openbb-cboe | [Cboe](https://www.cboe.com/delayed_quotes/) data connector. | pip install openbb-cboe | Community | None |
| openbb-ecb | [ECB](https://data.ecb.europa.eu/) data connector. | pip install openbb-ecb | Community | None |
| openbb-finra | [FINRA](https://www.finra.org/finra-data) data connector. | pip install openbb-finra | Community | None / Free |
| openbb-fmp | [FMP](https://site.financialmodelingprep.com/developer/) data connector. | pip install openbb-fmp | Core | Free |
| openbb-fred | [FRED](https://fred.stlouisfed.org/) data connector. | pip install openbb-fred | Core | Free |
| openbb-government-us | [US Government](https://data.gov) data connector. | pip install openbb-us-government | Core | None |
| openbb-intrinio | [Intrinio](https://intrinio.com/pricing) data connector. | pip install openbb-intrinio | Core | Paid |
| openbb-nasdaq | [Nasdaq Data Link](https://data.nasdaq.com/) connector. | pip install openbb-nasdaq | Community | None / Free |
| openbb-oecd | [OECD](https://data.oecd.org/) data connector. | pip install openbb-oecd | Core | Free |
| openbb-polygon | [Polygon](https://polygon.io/) data connector. | pip install openbb-polygon | Core | Free |
| openbb-sec | [SEC](https://www.sec.gov/edgar/sec-api-documentation) data connector. | pip install openbb-sec | Core | None |
| openbb-seeking-alpha | [Seeking Alpha](https://seekingalpha.com/) data connector. | pip install openbb-seeking-alpha | Community | None |
| openbb-stockgrid | [Stockgrid](https://stockgrid.io) data connector. | pip install openbb-stockgrid | Community | None |
| openbb-tiingo | [Tiingo](https://www.tiingo.com/about/pricing) data connector. | pip install openbb-tiingo | Core | Free |
| openbb-tradingeconomics | [TradingEconomics](https://tradingeconomics.com/api) data connector. | pip install openbb-tradingeconomics | Core | Paid |
| openbb-ultima | [Ultima Insights](https://ultimainsights.ai/openbb) data connector. | pip install openbb-ultima | Community | Paid |
| openbb-wsj | [Wall Street Journal](https://www.wsj.com/) data connector. | pip install openbb-wsj | Community | None |
| openbb-yfinance | [Yahoo Finance](https://finance.yahoo.com/) data connector. | pip install openbb-yfinance | Community | None |

Have you published a data provider extension and want it featured on this list?  Tell us about it!  Open a pull request on [GitHub](https://github.com/OpenBB-finance/OpenBBTerminal/) to submit an extension for inclusion.  Code contributions, for new and existing, data providers are always welcome.

Search [PyPI](https://pypi.org/search/?q=openbb-) to find more extensions.
