```
usage: currencies [--export {csv,json,xlsx}] [-h]
```

Shows a basket of global currencies from the Wall Street Journal. (https://www.wsj.com/market-data/currencies)

```
optional arguments:
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 04:48 (✨) /economy/ $ currencies
                      Currencies
┌────────────────────────┬─────────┬─────────┬───────┐
│                        │ Last    │ Chng    │ %Chng │
├────────────────────────┼─────────┼─────────┼───────┤
│ Euro (EUR/USD)         │ 1.1340  │ 0.0033  │ 0.29  │
├────────────────────────┼─────────┼─────────┼───────┤
│ Japanese Yen (USD/JPY) │ 115.61  │ 0.07    │ 0.06  │
├────────────────────────┼─────────┼─────────┼───────┤
│ U.K. Pound (GBP/USD)   │ 1.3548  │ 0.0020  │ 0.15  │
├────────────────────────┼─────────┼─────────┼───────┤
│ Swiss Franc (USD/CHF)  │ 0.9261  │ 0.0015  │ 0.16  │
├────────────────────────┼─────────┼─────────┼───────┤
│ Chinese Yuan (USD/CNY) │ 6.3508  │ -0.0068 │ -0.11 │
├────────────────────────┼─────────┼─────────┼───────┤
│ Canadian $ (USD/CAD)   │ 1.2712  │ -0.0017 │ -0.13 │
├────────────────────────┼─────────┼─────────┼───────┤
│ Mexican Peso (USD/MXN) │ 20.3832 │ -0.0323 │ -0.16 │
├────────────────────────┼─────────┼─────────┼───────┤
│ Bitcoin (BTC/USD)      │ 44066   │ 1809    │ 4.28  │
├────────────────────────┼─────────┼─────────┼───────┤
│ WSJ Dollar Index       │ 89.89   │ -0.14   │ -0.15 │
├────────────────────────┼─────────┼─────────┼───────┤
│ U.S. Dollar Index      │ 96.08   │ -0.29   │ -0.30 │
└────────────────────────┴─────────┴─────────┴───────┘
```
