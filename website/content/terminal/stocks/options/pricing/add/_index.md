```
usage: add [-p PRICE] [-c CHANCE] [-h]
```

Add price and probability points to the list

```
optional arguments:
  -p PRICE, --price PRICE
                        Projected price of the stock at the expiration date (default: None)
  -c CHANCE, --chance CHANCE
                        Chance that the stock is at a given projected price (default: None)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 16, 09:42 (✨) /stocks/options/pricing/ $ add -p 175 -c 0.5

2022 Feb 16, 09:43 (✨) /stocks/options/pricing/ $ add -p 165 -c 0.5

2022 Feb 16, 09:43 (✨) /stocks/options/pricing/ $ show
Estimated price(s) of AAPL at 2022-05-20
┏━━━━━━━━┳━━━━━━━━┓
┃ Price  ┃ Chance ┃
┡━━━━━━━━╇━━━━━━━━┩
│ 165.00 │ 0.50   │
├────────┼────────┤
│ 175.00 │ 0.50   │
└────────┴────────┘
```
