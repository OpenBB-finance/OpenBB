```
usage: cgexrates [-l N] [-s {Index,Name,Unit,Value,Type}] [--descend] [--export {csv,json,xlsx}] [-h]
```

Shows list of crypto, fiats, commodity exchange rates from CoinGecko You can look on only display N number records with --limit, You can sort by Index,
Name, Unit, Value, Type, and also use --descend flag to sort descending.

```
optional arguments:
  -l N, --limit N     display N number records (default: 15)
  -s {Index,Name,Unit,Value,Type}, --sort {Index,Name,Unit,Value,Type}
                        Sort by given column. Default: Index (default: Index)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 08:12 (✨) /crypto/ov/ $ cgexrates
                           Exchange Rates
┌───────┬─────────────────────────────┬──────┬────────────┬────────┐
│ Index │ Name                        │ Unit │ Value      │ Type   │
├───────┼─────────────────────────────┼──────┼────────────┼────────┤
│ 1     │ Bitcoin                     │ BTC  │ 1.00       │ crypto │
├───────┼─────────────────────────────┼──────┼────────────┼────────┤
│ 2     │ Ether                       │ ETH  │ 14.20      │ crypto │
├───────┼─────────────────────────────┼──────┼────────────┼────────┤
│ 3     │ Litecoin                    │ LTC  │ 337.43     │ crypto │
├───────┼─────────────────────────────┼──────┼────────────┼────────┤
│ 4     │ Bitcoin Cash                │ BCH  │ 130.59     │ crypto │
├───────┼─────────────────────────────┼──────┼────────────┼────────┤
│ 5     │ Binance Coin                │ BNB  │ 103.36     │ crypto │
├───────┼─────────────────────────────┼──────┼────────────┼────────┤
│ 6     │ EOS                         │ EOS  │ 17907.80   │ crypto │
├───────┼─────────────────────────────┼──────┼────────────┼────────┤
│ 7     │ XRP                         │ XRP  │ 53041.60   │ crypto │
├───────┼─────────────────────────────┼──────┼────────────┼────────┤
│ 8     │ Lumens                      │ XLM  │ 201835.99  │ crypto │
├───────┼─────────────────────────────┼──────┼────────────┼────────┤
│ 9     │ Chainlink                   │ LINK │ 2619.11    │ crypto │
├───────┼─────────────────────────────┼──────┼────────────┼────────┤
│ 10    │ Polkadot                    │ DOT  │ 2235.39    │ crypto │
├───────┼─────────────────────────────┼──────┼────────────┼────────┤
│ 11    │ Yearn.finance               │ YFI  │ 1.85       │ crypto │
├───────┼─────────────────────────────┼──────┼────────────┼────────┤
│ 12    │ US Dollar                   │ $    │ 44258.09   │ fiat   │
├───────┼─────────────────────────────┼──────┼────────────┼────────┤
│ 13    │ United Arab Emirates Dirham │ DH   │ 162560.27  │ fiat   │
├───────┼─────────────────────────────┼──────┼────────────┼────────┤
│ 14    │ Argentine Peso              │ $    │ 4711797.18 │ fiat   │
├───────┼─────────────────────────────┼──────┼────────────┼────────┤
│ 15    │ Australian Dollar           │ A$   │ 61998.28   │ fiat   │
└───────┴─────────────────────────────┴──────┴────────────┴────────┘
```
