```
usage: btcct    [-s INITIAL_DATE]
                [-u END_DATE]
                [--export {csv,json,xlsx}] [-h]
```

Displays bitcoin confirmed transactions. [Source: https://api.blockchain.info/]

```
arguments:
  -s DATE --since DATE          Initial date. Default is initial BTC date: 2010-01-01
  -u DATE --until DATE          Final date. Default is current date
  --export {csv,json,xlsx}      Export dataframe data to csv,json,xlsx file (default: )
  -h, --help                    show this help message (default: False)
```
