```
usage: rmv [-o OPTION [OPTION ...]] [-a] [-h]

Remove one of the options to be shown in the hedge.

optional arguments:
  -o OPTION [OPTION ...], --option OPTION [OPTION ...]
                        index of the option to remove
  -a, --all             remove all of the options
  -h, --help            show this help message
```

Example:
```
2022 May 10, 09:32 (🦋) /stocks/options/hedge/ $ rmv Option A
          Current Option Positions           
┏━━━━━━┳━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Type ┃ Hold ┃ Strike ┃ Implied Volatility ┃
┡━━━━━━╇━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ Call │ Long │ 155.00 │ 0.06               │
└──────┴──────┴────────┴────────────────────┘
```