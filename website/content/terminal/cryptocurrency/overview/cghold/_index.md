```
usage: cghold [-c {ethereum,bitcoin}] [--bar] [--export {csv,json,xlsx}] [-h]
```

Shows overview of public companies that holds ethereum or bitcoin. You can find there most important metrics like: Total Bitcoin Holdings, Total
Value (USD), Public Companies Bitcoin Dominance, Companies

```
optional arguments:
  -c {ethereum,bitcoin}, --coin {ethereum,bitcoin}
                        companies with ethereum or bitcoin (default: bitcoin)
  --bar                 Shows bar chart comparing companies holding {ethereum,bitcoin}
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example
```
2022 Feb 15, 08:13 (✨) /crypto/ov/ $ cghold

27 companies hold a total of 217.240 K bitcoin (1.15% of market cap dominance) with the current value of 9.618 B USD dollars

                                                        Public Companies Holding BTC or ETH
┌─────────────────────────┬──────────────┬─────────┬────────────────┬───────────────────────┬─────────────────────────┬────────────────────────────┐
│ Name                    │ Symbol       │ Country │ Total Holdings │ Total Entry Value Usd │ Total Current Value Usd │ Percentage Of Total Supply │
├─────────────────────────┼──────────────┼─────────┼────────────────┼───────────────────────┼─────────────────────────┼────────────────────────────┤
│ MicroStrategy Inc.      │ NASDAQ:MSTR  │ US      │ 121.044 K      │ 3.574 B               │ 5.359 B                 │ 0.576                      │
├─────────────────────────┼──────────────┼─────────┼────────────────┼───────────────────────┼─────────────────────────┼────────────────────────────┤
│ Tesla                   │ NASDAQ: TSLA │ US      │ 48 K           │ 1.500 B               │ 2.125 B                 │ 0.229                      │
├─────────────────────────┼──────────────┼─────────┼────────────────┼───────────────────────┼─────────────────────────┼────────────────────────────┤
│ Galaxy Digital Holdings │ TSE:GLXY     │ CA      │ 16.402 K       │ 134 M                 │ 726.154 M               │ 0.078                      │
├─────────────────────────┼──────────────┼─────────┼────────────────┼───────────────────────┼─────────────────────────┼────────────────────────────┤
│ Square Inc.             │ NASDAQ:SQ    │ US      │ 8.027 K        │ 220 M                 │ 355.374 M               │ 0.038                      │
├─────────────────────────┼──────────────┼─────────┼────────────────┼───────────────────────┼─────────────────────────┼────────────────────────────┤
│ Marathon Patent Group   │ NASDAQ:MARA  │ US      │ 4.813 K        │ 150 M                 │ 213.083 M               │ 0.023                      │
└─────────────────────────┴──────────────┴─────────┴────────────────┴───────────────────────┴─────────────────────────┴────────────────────────────┘
```
