```text
usage: cashflow [-q] [-t S_TIMEFRAME] [--export {csv,json,xlsx}] [-h]
```

Compares the cashflow statements of the selected companies. 

```
optional arguments:
  -q, --quarter         Quarter financial data flag. (default: False)
  -t S_TIMEFRAME, --timeframe S_TIMEFRAME
                        Specify yearly/quarterly timeframe. Default is last. (default: None)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 08:35 (✨) /stocks/ca/ $ cashflow
Other available yearly timeframes are: 2017, 2018, 2019, 2020, 2021

                           Cashflow Comparison
┌────────────────────────────────────────┬──────────┬─────────┬─────────┐
│                                        │ AAPL     │ TSLA    │ MSFT    │
├────────────────────────────────────────┼──────────┼─────────┼─────────┤
│ Net Income before Extraordinaries      │ 94.68B   │ 5.64B   │ 61.27B  │
├────────────────────────────────────────┼──────────┼─────────┼─────────┤
│ Net Income Growth                      │ 64.92%   │ 554.76% │ 38.37%  │
├────────────────────────────────────────┼──────────┼─────────┼─────────┤
│ Depreciation, Depletion & Amortization │ 11.28B   │ 2.91B   │ 10.9B   │
├────────────────────────────────────────┼──────────┼─────────┼─────────┤
│ Depreciation and Depletion             │ 11.28B   │ 1.91B   │ 9.3B    │
├────────────────────────────────────────┼──────────┼─────────┼─────────┤
│ Amortization of Intangible Assets      │ -        │ 1B      │ 1.6B    │
├────────────────────────────────────────┼──────────┼─────────┼─────────┤
│ Deferred Taxes & Investment Tax Credit │ (4.77B)  │ -       │ (150M)  │
├────────────────────────────────────────┼──────────┼─────────┼─────────┤
│ Deferred Taxes                         │ (4.77B)  │ -       │ (150M)  │
├────────────────────────────────────────┼──────────┼─────────┼─────────┤
│ Investment Tax Credit                  │ -        │ -       │ -       │
├────────────────────────────────────────┼──────────┼─────────┼─────────┤
│ Other Funds                            │ 7.76B    │ 2.42B   │ 5.66B   │
├────────────────────────────────────────┼──────────┼─────────┼─────────┤
│ Funds from Operations                  │ 108.95B  │ 10.98B  │ 77.68B  │
├────────────────────────────────────────┼──────────┼─────────┼─────────┤
│ Extraordinaries                        │ -        │ -       │ -       │
├────────────────────────────────────────┼──────────┼─────────┼─────────┤
│ Changes in Working Capital             │ (4.91B)  │ 518M    │ (936M)  │
├────────────────────────────────────────┼──────────┼─────────┼─────────┤
│ Receivables                            │ (14.03B) │ (130M)  │ (6.48B) │
├────────────────────────────────────────┼──────────┼─────────┼─────────┤
│ Accounts Payable                       │ 12.33B   │ 4.58B   │ 2.8B    │
├────────────────────────────────────────┼──────────┼─────────┼─────────┤
│ Other Assets/Liabilities               │ (567M)   │ (2.22B) │ 5.79B   │
├────────────────────────────────────────┼──────────┼─────────┼─────────┤
│ Net Operating Cash Flow                │ 104.04B  │ 11.5B   │ 76.74B  │
├────────────────────────────────────────┼──────────┼─────────┼─────────┤
│ Net Operating Cash Flow Growth         │ 28.96%   │ 93.45%  │ 26.48%  │
├────────────────────────────────────────┼──────────┼─────────┼─────────┤
│ Net Operating Cash Flow / Sales        │ 28.44%   │ 21.36%  │ 45.65%  │
└────────────────────────────────────────┴──────────┴─────────┴─────────┘
```
