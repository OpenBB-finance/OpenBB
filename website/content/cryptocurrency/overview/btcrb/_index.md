```
usage: btcrb    [-s INITIAL_DATE]
                [-u END_DATE]
                [--export {csv,json,xlsx}] [-h]
```

Displays bitcoin rainbow chart. It also includes halving dates.

[Price data from source: https://glassnode.com]
[Inspired by: https://blockchaincenter.net]

```
arguments:
  -s DATE --since DATE          Initial date. Default is initial BTC date: 2010-01-01
  -u DATE --until DATE          Final date. Default is current date
  --export {csv,json,xlsx}      Export dataframe data to csv,json,xlsx file (default: )
  -h, --help                    show this help message (default: False)
```
