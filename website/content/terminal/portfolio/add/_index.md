```
usage: add [-h]
```

Adds an item to your portfolio

```
optional arguments:
  -h, --help  show this help message (default: False)
```

```
2022 Feb 14, 10:31 (✨) /portfolio/ $ add

Type (stock, cash):
stock
Action: (buy, sell, deposit, withdraw):
buy
Name (ticker or cash [if depositing cash]):
TSLA
Purchase date (YYYY-MM-DD):
2022-02-08
Quantity:
10
Price per share:
900
Fees:
0
TSLA successfully added

2022 Feb 14, 10:31 (✨) /portfolio/ $ show
┌──────┬───────┬──────────┬─────────────────────┬────────┬──────┬─────────┬──────┬────────┐
│ Name │ Type  │ Quantity │ Date                │ Price  │ Fees │ Premium │ Side │ Value  │
├──────┼───────┼──────────┼─────────────────────┼────────┼──────┼─────────┼──────┼────────┤
│ SPY  │ etf   │ 1.00     │ 2019-10-21 00:00:00 │ 200.00 │ nan  │ nan     │ 1    │ 200.00 │
├──────┼───────┼──────────┼─────────────────────┼────────┼──────┼─────────┼──────┼────────┤
│ CASH │ cash  │ 1.00     │ 2019-10-21 00:00:00 │ 200.00 │ nan  │ nan     │ 1    │ 200.00 │
├──────┼───────┼──────────┼─────────────────────┼────────┼──────┼─────────┼──────┼────────┤
│ CASH │ cash  │ 0.00     │ 2021-06-21 00:00:00 │ 200.00 │ nan  │ nan     │ 0    │ 0.00   │
├──────┼───────┼──────────┼─────────────────────┼────────┼──────┼─────────┼──────┼────────┤
│ TSLA │ stock │ 10.00    │ 2022-02-08          │ 900.00 │ 0.00 │         │ buy  │ 9000   │
└──────┴───────┴──────────┴─────────────────────┴────────┴──────┴─────────┴──────┴────────┘
```
