---
title: load
description: OpenBB Terminal Function
---

# load

Load a ticker into option menu

### Usage

```python
load -t TICKER
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| ticker | Stock ticker | None | False | None |


---

## Examples

```python
2022 Feb 16, 09:13 (🦋) /stocks/options/ $ load TSLA

2022 Feb 16, 09:13 (🦋) /stocks/options/ $ ?
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── Stocks - Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                                                                                                                                                                                              │
│     unu           show unusual options activity [Fdscanner.com]                                                                                                                                                                                                              │
│     calc          basic call/put PnL calculator                                                                                                                                                                                                                              │
│                                                                                                                                                                                                                                                                              │
│     load          load new ticker                                                                                                                                                                                                                                            │
│     exp           see and set expiration dates                                                                                                                                                                                                                               │
│                                                                                                                                                                                                                                                                              │
│ Ticker: TSLA                                                                                                                                                                                                                                                                 │
│ Expiry: None                                                                                                                                                                                                                                                                 │
│                                                                                                                                                                                                                                                                              │
│     pcr           display put call ratio for ticker [AlphaQuery.com]                                                                                                                                                                                                         │
│     info          display option information (volatility, IV rank etc) [Barchart.com]                                                                                                                                                                                        │
│     chains        display option chains with greeks [Tradier]                                                                                                                                                                                                                │
│     oi            plot open interest [Tradier/YFinance]                                                                                                                                                                                                                      │
│     vol           plot volume [Tradier/YFinance]                                                                                                                                                                                                                             │
│     voi           plot volume and open interest [Tradier/YFinance]                                                                                                                                                                                                           │
│     hist          plot option history [Tradier]                                                                                                                                                                                                                              │
│     vsurf         show 3D volatility surface [Yfinance]                                                                                                                                                                                                                      │
│     grhist        plot option greek history [Syncretism.io]                                                                                                                                                                                                                  │
│     plot          plot variables provided by the user [Yfinance]                                                                                                                                                                                                             │
│     parity        shows whether options are above or below expected price [Yfinance]                                                                                                                                                                                         │
│     binom         shows the value of an option using binomial options pricing [Yfinance]                                                                                                                                                                                     │
│     greeks        shows the greeks for a given option [Yfinance]                                                                                                                                                                                                             │
│                                                                                                                                                                                                                                                                              │
│    screen        screens tickers based on preset [Syncretism.io]                                                                                                                                                                                                            │
│    payoff        shows payoff diagram for a selection of options [Yfinance]                                                                                                                                                                                                 │
│    pricing       shows options pricing and risk neutral valuation [Yfinance]                                                                                                                                                                                                │
│                                                                                                                                                                                                                                                                              │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── OpenBB Terminal ─╯
```
---
