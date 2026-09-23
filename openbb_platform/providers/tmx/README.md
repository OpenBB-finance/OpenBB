# OpenBB TMX Provider

This extension integrates [TMX Group](https://www.tmx.com) data into the OpenBB Platform.

Every dataset is read from public endpoints. **No API key or account is required.**

> This extension is unofficial. It is not affiliated with, endorsed by, or authorized by TMX Group Limited.

## Installation

Install from PyPI:

```bash
pip install openbb-tmx
```

Or from the source tree:

```bash
uv pip install -e openbb_platform/providers/tmx
```

Then rebuild the Python interface:

```python
import openbb

openbb.build()
```

### Optional extras

Two surfaces need a package no dataset requires, so each is declared as an
extra:

| Extra | Pulls in | Needed by | Without it |
| ----- | -------- | --------- | ---------- |
| `charting` | `openbb-charting` | `derivatives.options.smile` · `surface` · `stats` · `term_structure` | The four chart routes are not registered. |
| `builder` | `pywry` | `equity.screener_builder` and its `/screener_builder/view` iframe | The iframe raises `ImportError`, so the Workspace app's Screener tab cannot render, and the native window cannot open. |

```bash
pip install 'openbb-tmx[all]'
```

## Coverage

TMX publishes far more than Canadian equities. This extension covers the TMX
Money quote feed, the Montreal Exchange derivatives universe, and the CIRO debt
trade reporting facility.

| Command | Description |
| ------- | ----------- |
| `equity.search` | Search the instrument symbology across every market and asset class. |
| `equity.screener` | Screen by venue, type, and size, joined to vendor fundamentals. Indices are quoted over the directory, and futures are read from the Montreal Exchange session summary and settlement prices. |
| `equity.screener_builder` | The screen built interactively, in a native window or as a Workspace iframe. |
| `equity.symbol_reference` | Resolve symbols to their canonical form, validity, and listing venue. |
| `equity.quote` · `profile` · `historical` | Quotes, company reference data, and price history. |
| `equity.filings` | SEDAR filings, with links to the filed PDFs, and a viewer that serves the documents themselves. |
| `equity.gainers` | Curated stock lists, including the CIBC CDR list. |
| `equity.fundamental.income` · `balance` · `cash` | Statements, annual or quarterly, one record per period, with a view that lays the periods out as columns. |
| `equity.fundamental.dividends` · `splits` | Declared distributions and share splits. |
| `equity.calendar.earnings` | Earnings calendar with estimated and actual EPS. |
| `equity.ownership.insider_trading` · `insider_transactions` | Activity summary, and every SEDI filing. |
| `equity.estimates.consensus` | Analyst consensus, ratings, and price targets. |
| `equity.rankings` | The TSX 30 and TSX Venture 50 annual rankings. |
| `etf.search` · `info` · `holdings` · `sectors` · `countries` · `historical` | The TMX-listed fund universe. |
| `index.available` · `info` · `historical` · `constituents` · `sectors` · `snapshots` | The S&P/TSX index family, with profiles, levels, and key data. |
| `index.documents` | Factsheet and methodology PDFs, served through a file viewer. |
| `derivatives.options.chains` | Full option chains with greeks, Canadian and US. |
| `derivatives.options.covered_calls` | Listed calls screened by annualized premium return. |
| `derivatives.options.straddle` · `strangle` · `spreads` | Strategy pricing over the loaded chain. |
| `derivatives.options.smile` · `surface` · `stats` · `term_structure` | Plotly views of the chain. Registered only when `openbb-charting` is installed. |
| `derivatives.futures.instruments` · `futures.historical` | The Montreal Exchange universe and its history. |
| `currency.historical` | Currency pair history. |
| `fixedincome.prices` · `treasury_prices` · `trades` | The CIRO bond master and reported trades. |
| `markets.movers` · `trades` · `short_interest` | Market breadth, time and sales, and short interest. |
| `news.company` | Company news, press releases, and upcoming events. |
| `news.feed` · `market` · `blog` · `search` | Per-symbol, cross-symbol, editorial, and full-text news, each with the article body. |

## Symbology

A bare symbol is a Canadian listing; `.TO` and `.TSX` suffixes are accepted and
stripped. A prefix or exchange suffix selects something else:

| Form | Meaning | Example |
| ---- | ------- | ------- |
| `^` | Index | `^TSX` |
| `/` | Future | `/CGB`, `/CL:NMX` |
| `$` | Currency pair | `$USDCAD` |
| `~` | Cryptocurrency pair | `~BTCUSD:US`, `~ETHUSD:US` |
| `@` | Option contract | `@AC    260918P00011000:CA` |
| `:XX` | Exchange suffix | `IBM:US`, `AIR:PA`, `ASML:AS` |

Thirty-six exchange suffixes are addressable, spanning Europe, Asia, Latin
America, and the Middle East. Price history reaches back to each listing's
start - `IBM:US` to 1990, `$USDCAD` to 1996, the European venues to 2006.

Cryptocurrency pairs carry the `:US` suffix and quote against the US dollar.
An option contract is addressed by the padded symbol the chain publishes as
`contract_symbol`, so a contract is quoted and charted like any other listing.

## Notes on the data

**Options cover both sides of the border.** A bare symbol resolves to the
Montreal Exchange listing; suffix `:US` for the OPRA-listed contracts. Both
carry implied volatility and the full greeks on every expiry. Historical
end-of-day chains are available from the Montreal Exchange back to 2009.

**The instrument directory is swept, not listed.** The symbology has no
enumeration endpoint, so the directory is built by sweeping symbol prefixes and
de-duplicating on the vendor's symbol id. A prefix that saturates the row cap is
re-swept one character deeper, so a dense letter cannot silently truncate the
result. The Canadian sweep yields roughly 120,000 instruments, most of them
mutual funds.

**Fixed income comes from CIRO, behind Cloudflare.** The bond master is about
195,000 securities and 70MB, so it is fetched through a browser-impersonating
session and held on disk as parquet for the day rather than in the HTTP cache.
The edge refuses individual requests at random rather than blocking the session
- a warmup that is itself refused is routinely followed by a request that
succeeds - so every call rides out a refusal by retrying, backing off between
attempts. Trade history is capped at ninety days per query, so a longer range
is bracketed into consecutive windows; an unbounded request starts at the
bond's original issue date. A window still refused after every attempt is
reported rather than read as a window with no trades, so a partial answer is
never returned as a whole one. Trades carry the CIRO record id and the
submission date, which is later than the execution date when a trade is
reported late or amended.

**The file viewers serve the documents, not links to them.** A browser cannot
fetch either publisher's PDFs from a Workspace page, so a selected document is
downloaded and handed over whole. QuoteMedia serves the SEDAR filings to any
client; S&P refuses every server-side request for its index factsheets and
methodologies, so those are still passed through as URLs for the browser to
load.

**Most futures do not trade every session.** The exchange's intra-session
summary reports a last price only for contracts that have traded, which on a
given day is a handful of the roughly three hundred it lists. Every screened
contract therefore also carries the settlement price the exchange publishes for
it, read from that product's quotes page - a request per product root, held for
an hour, and made only for the products in the rows being returned. A contract
reported at the root level, as share and ETF futures are, carries its front
month's settlement.

**Insider trading does not use the standard model shape.** The values returned
are aggregate shares traded over the previous three, six, and twelve months.

**Price history intervals.** Daily, weekly, monthly, and intraday at any number
of minutes. Weekly and monthly bars are for the period beginning. Intraday
history is a rolling window of roughly one year, whatever start date is asked
for. Split-adjusted, split-and-dividend-adjusted, and unadjusted prices are
available for daily intervals only; other intervals are split-adjusted. The feed
leaves the high and low empty on a handful of historical foreign bars, so both
are optional.

**Responses are cached on disk.** A SQLite-backed HTTP cache holds responses
with a TTL per endpoint family - sixty seconds for quotes and movers, up to a
day for statements and reference data - and GraphQL operations carry their own
TTL table. Any request can bypass it with `use_cache=False`.

## TradingView charting

The extension serves TradingView's Universal Data Feed at `/tmx/udf`, so the
historical price widgets are declared as `advanced_charting` and render as
interactive charts over the same universe the provider addresses. The feed
implements `config`, `search`, `symbols`, `history`, and `time`, at every
resolution from one minute to monthly.

## Standalone usage

The extension registers its own router, so installing `openbb-tmx` alone still
exposes every dataset under `/tmx`. Each namespace registers its model-backed
commands only when the OpenBB extension that normally owns those standard models
is absent; when `openbb-equity` is installed, for example, the equity models are
served through it instead and the TMX routes step aside.

The fetchers can also be used directly, independent of the Python and API
interfaces:

```python
from openbb_tmx import tmx_provider

tmx_provider.fetcher_dict
```

## OpenBB Workspace

A bundled dashboard is served at `/api/v1/tmx/apps.json`. Start the API and add
it as a Workspace backend:

```bash
openbb-api
```

The app carries tabs for the market overview, the screener, company detail,
financials, options, futures and FX, fixed income, ETFs, indices, and news.
Clicking a row in a search, mover, or directory table drives the linked widgets
in that tab.

## Development

```bash
uv pip install -e '.[all]'
uv pip install --group dev
pytest tests --cov=openbb_tmx --cov-report=term-missing --cov-fail-under=100
```

The suite exercises both extras, so the unit run needs `.[all]` installed.

The unit suite runs entirely offline - no cassettes and no network - and is held
at one hundred percent coverage. Integration tests hit the live endpoints and
are excluded by default. The API half calls `http://0.0.0.0:8000`, so start the
API first:

```bash
openbb-api &
pytest integration -m integration
```

## OpenBB Documentation

OpenBB Platform documentation is available [here](https://docs.openbb.co/platform).

OpenBB Workspace documentation is available [here](https://docs.openbb.co/workspace).
