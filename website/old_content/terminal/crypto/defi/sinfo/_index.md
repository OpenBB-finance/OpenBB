```
usage: sinfo [-a ADDRESS] [-l LIMIT] [-h] [--export {csv,json,xlsx}]
```
Displays staking info of a certain terra address. [Source: https://fcd.terra.dev/swagger]

```
optional arguments:
  -a ADDRESS, --address ADDRESS
                        Terra address. Valid terra addresses start with 'terra' (default: None)
  -l LIMIT, --limit LIMIT
                        Number of delegations (default: 10)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```