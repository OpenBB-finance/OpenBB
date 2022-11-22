```
usage: rmv [-p PRICE] [-a] [-h]
```

Removes one or all entries from the list.

```
optional arguments:
  -p PRICE, --price PRICE
                        Price you want to remove from the list (default: None)
  -a, --all             Remove all prices from the list (default: False)
  -h, --help            show this help message (default: False)
```

Example:

```
2022 Feb 16, 09:44 (🦋) /stocks/options/pricing/ $ rmv -p 165

2022 Feb 16, 09:44 (🦋) /stocks/options/pricing/ $ show
Estimated price(s) of AAPL at 2022-05-20
┏━━━━━━━━┳━━━━━━━━┓
┃ Price  ┃ Chance ┃
┡━━━━━━━━╇━━━━━━━━┩
│ 175.00 │ 0.50   │
└────────┴────────┘
```
