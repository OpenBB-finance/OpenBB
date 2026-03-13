# OpenBB TMX Provider

This extension integrates the [TMX](https://www.tmx.com) data provider into the OpenBB Platform.

## Installation

To install the extension:

```bash
pip install openbb-tmx
```

Documentation available [here](https://docs.openbb.co/platform/developer_guide/contributing).

## Additional information

`openbb-tmx` is an unofficial, community, data provider extension for the OpenBB Platform.

Install with `pip install openbb-tmx`, or from the local directory, `pip install -e .`

## Command Coverage

- .derivatives.options.chains
  - Historical EOD chains data available from 2009.
- .equity.calendar.earnings
- .equity.estimates.consensus
- .equity.discovery.gainers
  - Includes a 'category' parameter for the type of 'best performer'.
- .equity.fundamental.dividends
- .equity.fundamental.filings
- .equity.ownership.insider_trading
  - Does not use the Standard Model because the data returned are total shares traded  over the previous 3,6,and 12 months.
- .equity.price.quote
- .equity.price.historical
  - Daily, weekly, monthly, and intraday - with valid intervals being any X number of minutes.
  - Weekly and monthly intervals are for the period beginning.
  - Historical intraday data begins April 14, 2022.
  - Split-adjusted, split and dividend adjusted, as well as unadjusted prices are available only for daily intervals. Other intervals are split-adjusted.
- .equity.search
- .equity.profile
- .etf.search
- .etf.info
- .etf.sectors
- .etf.countries
- .etf.holdings
  - Top 10 holdings only.
- .fixedincome.corporate.bond_prices
- .fixedincome.government.treasury_prices
- .index.constituents
  - Full constituents with weights and notional values.
- .index.snapshots
  - Regions of: ["ca", "us"]
- .index.available
  - Includes URLs to methedology and factsheet documents.
- .index.sectors
- .news.company

## Symbology

No exchange suffix is required to handle Canadian listings.  The extension accepts `.TO` and `.TSX` as well as no suffix.  Additionally, a composite ticker symbol can be entered. For example, `AAPL` trades as a Canadian Depositary Receipt, under the symbol `AAPL:AQN`, on the NEO Exchange. The US listing is also found as `AAPL:US`.  Some US and select European data is available from some functions, like `quote` and `historical`.

Indices all begin with `^`.

## Caching

This extension uses `aiohttp-client-cache` with a SQL backend to cache symbol directories, ETF, and index data. It can be bypassed with the parameter, `use_cache=False`. ETF and index data is gathered from a single JSON file which is updated daily by the exchange. The HTTP request is cached for one day.
