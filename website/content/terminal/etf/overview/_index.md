```
usage: overview [-h] [--export {csv,json,xlsx}]
```

Get overview data for selected etf

```
optional arguments:
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 15, 04:14 (✨) /etf/ $ overview
   ETF Overview Information
┌────────────────┬────────────┐
│                │ VOO        │
├────────────────┼────────────┤
│ Assets         │ $283.52B   │
├────────────────┼────────────┤
│ NAV            │ $413.03    │
├────────────────┼────────────┤
│ Expense Ratio  │ 0.03%      │
├────────────────┼────────────┤
│ PE Ratio       │ 24.90      │
├────────────────┼────────────┤
│ Shares Out     │ 686.44M    │
├────────────────┼────────────┤
│ Dividend (ttm) │ $5.44      │
├────────────────┼────────────┤
│ Dividend Yield │ 1.35%      │
├────────────────┼────────────┤
│ Volume         │ 10,167,584 │
├────────────────┼────────────┤
│ Open           │ 404.43     │
├────────────────┼────────────┤
│ Previous Close │ 404.94     │
├────────────────┼────────────┤
│ 52-Week Low    │ 341.92     │
├────────────────┼────────────┤
│ 52-Week High   │ 341.92     │
├────────────────┼────────────┤
│ Beta           │ 0.99       │
├────────────────┼────────────┤
│ Holdings       │ 510        │
└────────────────┴────────────┘
```
