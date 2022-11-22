```
usage: account [--all] [-c CURRENCY] [--export {csv,json,xlsx}] [-h]
```

Display info about your trading accounts on Coinbase

```
optional arguments:
  --all                 Flag to display all your account (default: False)
  -c CURRENCY, --currency CURRENCY
                        Currency to display value in. (default: USD)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Sample Usage:

```
(🦋) (bro)>(cb)> account
╒════════════╤═════════════╤═════════════╤════════════╤═════════════════════╕
│ currency   │     balance │   available │       hold │   BalanceValue(USD) │
╞════════════╪═════════════╪═════════════╪════════════╪═════════════════════╡
│ ALGO       │ 14.62881400 │ 14.62881400 │ 0.00000000 │               24.06 │
├────────────┼─────────────┼─────────────┼────────────┼─────────────────────┤
│ ATOM       │  0.00085600 │  0.00085600 │ 0.00000000 │                0.03 │
├────────────┼─────────────┼─────────────┼────────────┼─────────────────────┤
│ BTC        │  0.00043358 │  0.00043358 │ 0.00000000 │               18.16 │
╘════════════╧═════════════╧═════════════╧════════════╧═════════════════════╛
```
