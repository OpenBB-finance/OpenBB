```
usage: gacc [-l LIMIT] [--cumulative] [-k {active,total}] [--descend] [-h] [--export {csv,json,xlsx}]
```
Displays terra blockchain account growth history. [Source: https://fcd.terra.dev/swagger]

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        Number of days to show (default: 90)
  --cumulative          Show cumulative or discrete values. For active accounts only discrete value are available (default: True)
  -k {active,total}, --kind {active,total}
                        Total account count or active account count. Default: total (default: total)
  --descend             Flag to sort in descending order (lowest first) (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```