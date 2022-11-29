```text
usage: load [-t TICKER] [-s START] [-e END] [-l LIMIT] [-h]
```

Load ETF ticker to perform analysis on.

````
optional arguments:
  -t TICKER, --ticker TICKER
                        ETF ticker (default: None)
  -s START, --start START
                        The starting date (format YYYY-MM-DD) of the ETF (default: 2021-06-20)
  -e END, --end END     The ending date (format YYYY-MM-DD) of the ETF (default: 2022-06-21)
  -l LIMIT, --limit LIMIT
                        Limit of holdings to display (default: 5)
  -h, --help            show this help message (default: False)
````

Example:

```
2022 Jun 21, 09:18 (🦋) /etf/ $ load voo
Top company holdings found: AAPL, MSFT, AMZN, GOOGL, TSLA


2022 Jun 21, 09:18 (🦋) /etf/ $ ?
╭─────────────────────────────────────────────────────────────────────────────────────────────────────── ETF ────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                                                                                                                                    │
│     ln                 lookup by name                                                  [FinanceDatabase / StockAnalysis]                                                                                           │
│     ld                 lookup by description                                           [FinanceDatabase]                                                                                                           │
│     load               load ETF data                                                   [Yahoo Finance]                                                                                                             │
│                                                                                                                                                                                                                    │
│ Symbol: VOO                                                                                                                                                                                                        │
│ Major holdings: AAPL, MSFT, AMZN, GOOGL, TSLA                                                                                                                                                                      │
│                                                                                                                                                                                                                    │
│ >   ca                 comparison analysis,          get similar, historical, correlation, financials                                                                                                              │
│ >   disc               discover ETFs,                gainers/decliners/active                                                                                                                                      │
│ >   scr                screener ETFs,                overview/performance, using preset filters                                                                                                                    │
│                                                                                                                                                                                                                    │
│     overview           get overview                                                    [StockAnalysis]                                                                                                             │
│     holdings           top company holdings                                            [StockAnalysis]                                                                                                             │
│     weights            sector weights allocation                                       [Yahoo Finance]                                                                                                             │
│     summary            summary description of the ETF                                  [Yahoo Finance]                                                                                                             │
│     news               latest news of the company                                      [News API]                                                                                                                  │
│     candle             view a candle chart for ETF                                                                                                                                                                 │
│                                                                                                                                                                                                                    │
│     pir                create (multiple) passive investor excel report(s)              [PassiveInvestor]                                                                                                           │
│     compare            compare multiple different ETFs                                 [StockAnalysis]                                                                                                             │
│                                                                                                                                                                                                                    │
│ >   ta                 technical analysis,           ema, macd, rsi, adx, bbands, obv                                                                                                                              │
│ >   pred               prediction techniques,        regression, arima, rnn, lstm                                                                                                                                  │
│                                                                                                                                                                                                                    │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── OpenBB Terminal v1.3.0 (https://openbb.co) ─╯
```
