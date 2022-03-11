```
usage: show [-h]
```

Shows the list of prices and probabilities entered using the add command.

```
optional arguments:
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 16, 09:45 (✨) /stocks/options/pricing/ $ add -p 100 -c 0.5

2022 Feb 16, 09:46 (✨) /stocks/options/pricing/ $ add -p 200 -c 0.5

2022 Feb 16, 09:46 (✨) /stocks/options/pricing/ $ show
Estimated price(s) of AAPL at 2022-05-20
┏━━━━━━━━┳━━━━━━━━┓
┃ Price  ┃ Chance ┃
┡━━━━━━━━╇━━━━━━━━┩
│ 100.00 │ 0.50   │
├────────┼────────┤
│ 200.00 │ 0.50   │
└────────┴────────┘
```
