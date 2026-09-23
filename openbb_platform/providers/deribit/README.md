# OpenBB Deribit Provider Extension

This package adds the `openbb-deribit` provider and router extension to the Open Data Platform by
OpenBB.

It implements the complete public market data surface of [Deribit](https://docs.deribit.com/) — the
crypto derivatives exchange listing options, futures, perpetuals, spot pairs, and multi-leg combos —
as OpenBB Platform endpoints. No API key is required, and nothing here trades.

## Installation

Install from PyPI with:

```sh
pip install openbb-deribit
```

Then build the Python static assets by running:

```sh
openbb-build
```

## Quick Start

The fastest way to get started is by connecting to the OpenBB Workspace as a custom backend.

### Start Server

```sh
openbb-api
```

This starts the FastAPI server over localhost on port 6900.

### Add to Workspace

See the documentation [here](https://docs.openbb.co/python/quickstart/workspace) for more details.
The extension ships an `apps.json` describing a ready-made dashboard with Markets, Futures, Options,
Analysis, Volatility, and Reference tabs.

## Conditional Registration

Five of the Deribit models implement OpenBB standard models — `FuturesCurve`, `FuturesHistorical`,
`FuturesInfo`, `FuturesInstruments`, and `OptionsChains` — which are normally served by the
`openbb-derivatives` extension. When it is installed, Deribit registers as a provider under its
existing commands and no Deribit-specific route is added for them.

When it is absent, the same data is served from this extension's own router under
`/deribit/futures/...` and `/deribit/options/...`, so installing `openbb-deribit` on its own still
exposes every dataset. The bundled `apps.json` resolves its widget IDs the same way.

Everything else is Deribit-specific and always lives under `/deribit/...`.

## Coverage

### Endpoints

```python
from openbb import obb

obb.deribit
# /deribit
#     index
#         delivery_prices
#         historical
#         price
#     market
#         block_rfq_trades
#         book_summary
#         order_book
#         settlements
#         ticker
#         trade_volumes
#         trades
#     rates
#         apr_history
#         funding_chart
#         funding_history
#         funding_value         <- utility endpoint, returns a single rate
#     reference
#         announcements
#         combo_choices         <- utility endpoint serving choices to Workspace widgets
#         combos
#         contract_size         <- utility endpoint
#         currencies
#         currency_choices      <- utility endpoint
#         expirations
#         index_choices         <- utility endpoint
#         instrument_choices    <- utility endpoint
#         instruments
#         server_time           <- utility endpoint
#         status                <- utility endpoint
#     volatility
#         index
#         realized
#     futures
#         curve
#         curve_choices         <- utility endpoint
#         historical
#         info
#         instruments
#         perpetual_choices     <- utility endpoint
#     options
#         chains
#         optimizer
#         payoff
#         smile
#         spreads
#         stats
#         straddle
#         strangle
#         surface
#         term_structure
#         underlying_choices    <- utility endpoint
```

Every public data method the exchange documents is reachable. The methods that exist only to open a
websocket session — `auth`, `hello`, `subscribe`, `set_heartbeat`, `test` — are not exposed, because
they carry no data.

### Datasets

- **Options chains** — the full chain of an underlying, with all five greeks, mark/bid/ask implied
  volatility, and open interest. Read over a websocket subscription, which is the only way the
  exchange publishes greeks. BTC and ETH contracts are quoted in the underlying, so their premiums
  are carried to USD at the index level each quote was published against.
- **Order books** — the resting depth of any instrument, one row per level, by name or by numeric
  instrument identifier.
- **Quotes** — the live ticker of any instrument, and the whole-currency book summary carrying the
  top of book and trailing session statistics of every instrument at once.
- **Trades** — the prints that crossed, by instrument or across a currency, optionally over a span.
  Option prints carry the volatility they implied.
- **Block RFQ** — the block requests that traded, one row per leg, with the index levels each
  structure was marked against.
- **Futures** — the term structure of any underlying with a dated curve, priced off each contract's
  mark, optionally against how the curve stood some hours ago. Candles are available for any listed
  instrument, not only futures.
- **Funding and yield** — the hourly funding a perpetual has paid, the funding accrued over the
  current window, the single rate for a span, and the daily yield of each yield-bearing currency.
- **Volatility** — the DVOL volatility index as candles, and the volatility an asset has actually
  realized. Both accept several at once, and both offer only what the reading means something for:
  DVOL is computed for BTC and ETH alone, and a dollar-pegged token has no volatility against the
  dollar to realize, so USDC and USDT are not offered on either. EURR is, because a euro token
  measured against the dollar reads the euro rate — around 5 percent against their 0.5.

  This is separate from a currency contracts are *settled* in. USDC margins a real book on Deribit,
  so it stays on the instrument, book summary, settlement and trade views, and the dashboard binds
  the two meanings to two different controls rather than one.

### Options Are Listed By Underlying, Not By Settlement Currency

Only BTC and ETH are both a settlement currency and an underlying, which is the only reason the
exchange's by-currency listings read sensibly for them. USDC settles options written on seven
different underlyings, so asking for `kind=option` by USDC returns 3,656 contracts across AVAX,
BTC, ETH, HYPE, SOL, TRON and XRP — a settlement rail, not a chain. USDT and EURR settle no options
at all.

So a listing of option contracts scoped to a currency that only settles them is refused, and says
to ask by the underlying instead. Every one of those underlyings is offered by name, and naming an
instrument directly still works. The same views keep USDC for what it genuinely carries — 174
futures, 47 spot pairs — and settlements, which are a settlement-currency fact, keep every
currency the exchange collateralises in.
- **Indices** — the current level of any of the 344 published indices, its history over a span, and
  the level each index has delivered at.
- **Settlements** — the settlements, deliveries, and bankruptcies the exchange has processed.
- **Reference** — the full contract specification of every listed instrument, every currency the
  exchange lists, the expirations listed on each currency, every multi-leg combo, and the exchange's
  own announcements.

## Options Analysis

The chain is also the input to an analysis suite built on it. Every figure below is computed from
the quotes the exchange publishes — there is no second data source, and no assumption about a rate
or a dividend the exchange does not quote.

- **Strategy optimizer** — builds every Deribit combo structure the chosen expiration can form,
  bought and sold: call and put spreads (CS, PS), straddles and strangles (STRD, STRG), risk
  reversals and synthetics (RR, REV), 1x2 ratio spreads (CSR12, PSR12), butterflies and iron
  butterflies (CBUT, PBUT, IBUT), condors and iron condors (CCOND, PCOND, ICOND), calendars and
  diagonals against the expiration about a month later (CCAL, PCAL, CDIAG, PDIAG), and single
  calls and puts. A position Deribit lists as a combo book is priced from that book's bid or offer,
  and every listed combo on the expiration is ranked even outside the strike window. Each position
  is sized so its worst loss across a threefold move either way is the budget, which is what lets
  credit structures rank alongside debit ones. The best position of each structure is returned,
  ranked by what it returns if the underlying reaches a price by a date.
- **Payoff** — the profit and loss of one ranked strategy, drawn only over the prices where the
  position actually responds. A payoff is a straight line everywhere outside its strikes, so the
  range is taken from the position rather than from a fixed span either side of spot, and the
  target and breakevens are added when they sit within reach of it.
- **Straddle, strangle, vertical spreads** — the standard structures priced at every listed
  expiration, each with its cost, its cost as a share of spot, its breakevens, and its bounds.
- **Volatility smile** — implied volatility or skew against strike for calls and puts, up to five
  expirations, optionally only out of the money. Drawn the same way as the Cboe smile.
- **Volatility term structure** — implied volatility or price at the nearest out-of-the-money
  strike, a chosen strike, or a moneyness, across every expiration. Drawn the same way as Cboe's.
- **Volatility surface** — implied volatility, a greek, or delta and gamma exposure, raised over
  days to expiration and strike, for either side of the chain. Drawn the same way as Cboe's.
- **Statistics** — call and put open interest or volume by expiration, or by strike for one
  expiration, as values, shares of the total, or put/call ratios. Drawn the same way as Cboe's.

### Priced and Sized in the Quote Currency

Budgets and profits are expressed in what the underlying is quoted in — USD for the coin-margined
roots, USDC for the linear ones — so a budget means the same thing whichever contract it buys, and
the numbers are readable without converting anything.

BTC and ETH options are still settled in the coin, and that is not hidden. The premium is coin the
account no longer holds, so what it cost depends on what the coin is worth at the price being
valued: at the price the position was opened at the loss is exactly the premium, above it more,
below it less. This is why an inverse position's loss is not the flat line a linear payoff has, and
the chart says which contract settles in what.

The settlement style, contract size and tick size are read from the exchange's own instrument
specification rather than assumed. The tick matters for sizing: far out of the money the published
mark can run below the smallest price the instrument trades in — a TRON contract marked at 3.1e-07
against a tick of 5e-05 — and sizing a budget against a price nobody can pay invents a position
hundreds of times larger than the money would really buy. A contract that is priced at all is
entered at no less than one tick; a contract with no price is left out.

### Greeks Are Modelled, Not Subscribed

The `options.chains` table reads the greeks the exchange itself publishes, which means subscribing
to every contract over a websocket — about twelve seconds for BTC. The analysis views do not need
the exchange's greeks, only its quotes and volatilities, and those come from three REST calls in
well under a second. They read that path instead and model the greeks from the quoted volatility.

Measured against the greeks Deribit publishes, across all 972 BTC contracts: delta agrees to a
median of 0.0001, gamma to 0.000002, vega to 0.03. Theta follows the exchange's own two
conventions rather than the bare derivative — scaled down inside the last day, where the
derivative diverges but a contract cannot decay faster than it expires, and floored at the
contract's own value, because nothing decays by more than it is worth. Both rules bind on real
contracts; together they bring the worst disagreement across the chain from 193 per day to 0.11.

The whole nine-widget Analysis tab loads in under three seconds cold and about one warm, against
fourteen seconds before. The last read of a chain is held briefly and shared, so nine views of one
underlying read it once.

### Choices Are Read Live

The exchange lists 52 currencies, 344 indices, and roughly 5,800 instruments, and the set changes
week to week. Nothing in this extension freezes those into a literal: the underlyings with listed
options, the underlyings with a futures curve, the perpetuals, the indices, and the combo
identifiers are all read from the exchange when asked for. The utility endpoints marked above serve
them to Workspace widgets as `[{label, value}]`.

## Example

```python
from openbb import obb

# The full BTC option chain, with greeks.
chains = obb.deribit.options.chains(symbol="BTC", provider="deribit")

# The BTC futures term structure, against where it stood a day ago.
curve = obb.deribit.futures.curve(symbol="BTC", hours_ago=24, provider="deribit")

# The resting depth of the BTC perpetual.
book = obb.deribit.market.order_book(
    symbol="BTC-PERPETUAL", depth=20, provider="deribit"
)

# The top of book of every BTC instrument at once.
summary = obb.deribit.market.book_summary(
    currency="BTC", kind="option", provider="deribit"
)

# The hourly funding the BTC perpetual has paid.
funding = obb.deribit.rates.funding_history(symbol="BTC-PERPETUAL", provider="deribit")

# The DVOL volatility index, as daily candles.
dvol = obb.deribit.volatility.index(currency="BTC", interval="1d", provider="deribit")

# Every instrument the exchange lists, with its full specification.
instruments = obb.deribit.reference.instruments(currency="any", provider="deribit")

# The best position of every combo structure for a view of 100,000 BTC by year end,
# each risking 5,000 USD.
ranked = obb.deribit.options.optimizer(
    symbol="BTC", target_price=100000, target_date="2026-12-25", budget=5000
)

# The payoff of the best of them.
diagram = obb.deribit.options.payoff(
    symbol="BTC", target_price=100000, target_date="2026-12-25"
)

# At-the-money volatility against time to expiration.
term = obb.deribit.options.term_structure(symbol="BTC")
```

When `openbb-derivatives` is installed, the five shared models are reached through the standard
namespace instead — `obb.derivatives.options.chains(provider="deribit")`,
`obb.derivatives.futures.curve(provider="deribit")`, and so on.

## Notes

Responses are cached on disk with a lifetime chosen per endpoint: a day for the currency and index
directories, an hour for the instrument listings, minutes for the historical series, and not at all
for quotes, books, and the server clock. The cache file is swept once per process and capped at
128 MiB.

Perpetuals can be named either in full — `SOL_USDC-PERPETUAL` — or by their shortened root,
`SOLUSDC`.

