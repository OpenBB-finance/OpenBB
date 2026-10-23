# OpenBB Nasdaq Provider

This extension integrates the [Nasdaq](https://www.nasdaq.com) data into the OpenBB Platform.

Every dataset is read from the public Nasdaq website API. **No API key or account is required.**

> This extension is not affiliated with, endorsed by, or authorized by Nasdaq, Inc.

## Installation

Install from PyPI:

```bash
pip install openbb-nasdaq
```

Or from the source tree:

```bash
uv pip install -e openbb_platform/providers/nasdaq
```

Then rebuild the Python interface:

```python
import openbb

openbb.build()
```

## Coverage

Nasdaq publishes far more than US equities. This extension covers the US market
activity API, the Nasdaq Nordic and Baltic markets, and the Morningstar
fundamentals Nasdaq co-brands for Nordic listings.

### US markets

| Command | Description |
| ------- | ----------- |
| `equity.search` | The Nasdaq-traded symbol directory. |
| `equity.screener` | Screen US listings by exchange, sector, region, market cap, and country. |
| `equity.quote` | Delayed quotes with the sector, market cap, and dividend summary. |
| `equity.profile` | Company profile, sector, industry, and business description. |
| `equity.historical` | Daily OHLCV history. |
| `equity.filings` | SEC filings, with links to the filed PDFs. |
| `equity.fundamental.balance` · `income` · `cash` · `ratios` | Statements and ratios, annual or quarterly. |
| `equity.fundamental.dividends` · `historical_eps` | Dividend history and earnings surprises. |
| `equity.ownership.insider_trading` · `institutional` · `short_interest` | Ownership and short interest. |
| `equity.estimates.price_target` · `consensus` | Analyst actions and the consensus overview. |
| `equity.calendar.earnings` · `dividend` · `splits` · `ipo` | Corporate calendars. |
| `economy.calendar` | The economic events calendar. |
| `markets.status` | Session status with the next open and close times. |
| `markets.movers` | Most active, advancers, decliners, and Nasdaq-100, by session. |
| `markets.quotes` | One request for a mixed-asset watchlist. |
| `markets.upcoming` | Event counts and a preview of the next session. |
| `index.search` · `snapshots` · `historical` | The index universe, snapshots, and history at `1d` or `1m`. |
| `etf.search` · `info` · `holdings` · `equity_exposure` · `historical` | Funds, their top-ten holdings, and the reverse exposure lookup. |
| `crypto.historical` | Daily crypto pair history. |
| `options.chains` | Full chains, narrowable to one expiration for full per-contract detail and greeks. |
| `news.company` | Company news and press releases. |

### Nasdaq Nordic and Baltic

| Command | Description |
| ------- | ----------- |
| `nordic.screener` | 19 asset classes - shares, indexes, funds, ETPs, options, custom basket forwards, corporate/government/mortgage bonds, sustainable debt, FI derivatives, structured products, warrants, and certificates. |
| `nordic.info` | Reference and trading metadata, plus the company profile. |
| `nordic.fundamentals` | Morningstar statements, ratios, growth rates, and peers. |
| `nordic.dividends` | Declared distributions with ex and payment dates. |
| `nordic.historical` | Daily prices, with duration and yield for fixed income. |
| `nordic.historical_trades` | Trade-by-trade history with the buying and selling members. |
| `nordic.movers` · `derivatives_volume` | Most traded instruments and derivatives market volume. |
| `nordic.knocked_out` | Leverage instruments whose barrier has been breached. |
| `nordic.bond_yields` | Average Danish bond yields by segment and residual maturity. |
| `nordic.index_factors` | Inflation index factors for index-linked mortgage bonds. |
| `nordic.mortgage_rates` | Listed mortgage rates by lender and fixed-rate term. |
| `nordic.trading_hours` · `holidays` | Session hours and the exchange holiday calendar. |
| `nordic.symbol_choices` | The full instrument directory, for symbol pickers. |
| `nordic.news` | Company announcements and exchange notices. |

## Notes on the data

**Asset classes are resolved behind the scenes.** Nasdaq keys most endpoints by
an asset class (`stocks`, `etf`, `index`, `mutualfunds`, `crypto`). You pass a
symbol; the extension resolves the class from the listing directory, falling
back to a probe only for symbols the directory does not carry.

The same applies to Nasdaq Nordic, where instruments are keyed by an opaque
orderbook ID *and* an asset class. Every listing is indexed once per process
into a single directory of roughly 17,800 instruments, so the symbol alone
resolves both. Nasdaq refuses pages under load by returning them empty rather
than erroring, so a page that comes back empty when the listing claims more is
retried - otherwise the directory would silently come up short.

**`etf.holdings` covers mutual funds too.** ETFs are served from the company
holdings endpoint and mutual funds from the fund profile.

**Options chains carry the full detail.** Nasdaq's chain endpoint publishes only
last, change, bid, ask, volume, and open interest, and its greeks endpoint is
locked to the front expiration. The remaining fields - open, high, low, previous
close, sizes, contract high and low, tick, market, and the greeks for *every*
expiration - come from the per-strike contract endpoint, which is fanned out
with bounded concurrency and retried on refusal.

**Some Nordic data is only on the page.** The trading hours and the exchange
holiday calendar are published as server-rendered tables, not through an API,
so they are read out of the markup.

**Nordic fundamentals come from a PDF.** The JSON sections Nasdaq exposes for
Morningstar fundamentals return empty. The data is published only in the
co-branded fact sheet, which this extension parses from glyph positions - the
two-column layout interleaves the reading order, so plain text extraction is
unusable.

**Responses are cached on disk.** A SQLite-backed HTTP cache holds responses
with a TTL per endpoint family - sixty seconds for quotes and movers, up to a
day for statements and filings - so a repeat options chain does not re-fetch
thousands of unchanged contracts.

## Standalone usage

The extension registers its own router, so installing `openbb-nasdaq` alone
still exposes every dataset under `/nasdaq`. Each namespace registers its
model-backed commands only when the OpenBB extension that normally owns those
standard models is absent; when `openbb-equity` is installed, for example, the
equity models are served through it instead and Nasdaq's own routes step aside.

The fetchers can also be used directly, independent of the Python and API
interfaces:

```python
from openbb_nasdaq import nasdaq_provider

nasdaq_provider.fetcher_dict
```

## OpenBB Workspace

A bundled dashboard is served at `/api/v1/nasdaq/apps.json`, with the widget IDs
resolved against whichever extensions are installed. Start the API and add it as
a Workspace backend:

```bash
openbb-api
```

The app carries tabs for earnings, dividends, calendars, the economy, screeners,
options, funds, indexes, and the Nordic markets. Clicking a symbol in a screener,
mover, or snapshot table drives the linked widgets in that tab.

## Development

```bash
uv pip install -e '.'
uv pip install --group dev
pytest tests --cov=openbb_nasdaq --cov-report=term-missing
```

The unit suite runs entirely offline - no cassettes and no network. Integration
tests hit the live endpoints and are excluded by default:

```bash
pytest integration -m integration
```

## OpenBB Documentation

OpenBB Platform documentation is available [here](https://docs.openbb.co/platform).

OpenBB Workspace documentation is available [here](https://docs.openbb.co/workspace).
