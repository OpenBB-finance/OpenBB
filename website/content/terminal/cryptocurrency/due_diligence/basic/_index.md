```
usage: basic [--export {csv,json,xlsx}] [-h]
```

Get basic information for coin. Like: name, symbol, rank, type, description, platform, proof_type, contract, tags, parent

```
optional arguments:
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 07:10 (✨) /crypto/dd/ $ basic
                                    Basic Coin Information
┌─────────────┬───────────────────────────────────────────────────────────────────────────────┐
│ Metric      │ Value                                                                         │
├─────────────┼───────────────────────────────────────────────────────────────────────────────┤
│ id          │ btc-bitcoin                                                                   │
├─────────────┼───────────────────────────────────────────────────────────────────────────────┤
│ name        │ Bitcoin                                                                       │
├─────────────┼───────────────────────────────────────────────────────────────────────────────┤
│ symbol      │ BTC                                                                           │
├─────────────┼───────────────────────────────────────────────────────────────────────────────┤
│ rank        │ 1                                                                             │
├─────────────┼───────────────────────────────────────────────────────────────────────────────┤
│ type        │ coin                                                                          │
├─────────────┼───────────────────────────────────────────────────────────────────────────────┤
│ description │ Bitcoin is a cryptocurrency and worldwide payment system. It is the first     │
│             │ decentralized digital currency, as the system works without a central bank or │
│             │ single administrator.                                                         │
├─────────────┼───────────────────────────────────────────────────────────────────────────────┤
│ platform    │ bnb-binance-coin                                                              │
├─────────────┼───────────────────────────────────────────────────────────────────────────────┤
│ proof_type  │ Proof of Work                                                                 │
├─────────────┼───────────────────────────────────────────────────────────────────────────────┤
│ contract    │ 0x719bd7b3d60f0b194fdbe4570aeda1b3712b4986                                    │
├─────────────┼───────────────────────────────────────────────────────────────────────────────┤
│ tags        │ Segwit, Cryptocurrency, Proof Of Work, Payments, Sha256, Mining, Lightning    │
│             │ Network                                                                       │
├─────────────┼───────────────────────────────────────────────────────────────────────────────┤
│ parent      │ bnb-binance-coin                                                              │
└─────────────┴───────────────────────────────────────────────────────────────────────────────┘
```
