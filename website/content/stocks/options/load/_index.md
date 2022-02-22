```
usage: load [-t TICKER] [-s {tr,yf}] [-h]
```

Load a ticker into the Options menu

```
optional arguments:
  -t TICKER, --ticker TICKER
                        Stock ticker (default: None)
  -s {tr,yf}, --source {tr,yf}
                        Source to get option expirations from (default: None)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 16, 09:13 (✨) /stocks/options/ $ load TSLA

2022 Feb 16, 09:13 (✨) /stocks/options/ $ ?
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
│ >   screen        screens tickers based on preset [Syncretism.io]                                                                                                                                                                                                            │
│ >   payoff        shows payoff diagram for a selection of options [Yfinance]                                                                                                                                                                                                 │
│ >   pricing       shows options pricing and risk neutral valuation [Yfinance]                                                                                                                                                                                                │
│                                                                                                                                                                                                                                                                              │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── Gamestonk Terminal ─╯
```
