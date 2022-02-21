```
usage: cgdefi [--export {csv,json,xlsx}] [-h]
```

Shows global DeFi statistics DeFi or Decentralized Finance refers to financial services that are built on top of distributed networks with no central
intermediaries. Displays metrics like: Market Cap, Trading Volume, Defi Dominance, Top Coins...

```
optional arguments:
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 08:11 (✨) /crypto/ov/ $ cgdefi
           Global DEFI Statistics
┌─────────────────────────┬─────────────────┐
│ Metric                  │ Value           │
├─────────────────────────┼─────────────────┤
│ Defi Market Cap         │ 110361000917.64 │
├─────────────────────────┼─────────────────┤
│ Eth Market Cap          │ 372708922218.61 │
├─────────────────────────┼─────────────────┤
│ Defi To Eth Ratio       │ 29.61           │
├─────────────────────────┼─────────────────┤
│ Trading Volume 24H      │ 4839623761.93   │
├─────────────────────────┼─────────────────┤
│ Defi Dominance          │ 5.32            │
├─────────────────────────┼─────────────────┤
│ Top Coin Name           │ Terra           │
├─────────────────────────┼─────────────────┤
│ Top Coin Defi Dominance │ 20.40           │
└─────────────────────────┴─────────────────┘
```
