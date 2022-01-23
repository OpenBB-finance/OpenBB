```
usage: validators [-l LIMIT] [-s {validatorName,tokensAmount,votingPower,commissionRate,status,uptime}] [--descend] [-h] [--export {csv,json,xlsx}]
```
Displays information about terra validators. [Source: https://fcd.terra.dev/swagger]

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        Number of validators to show (default: 10)
  -s {validatorName,tokensAmount,votingPower,commissionRate,status,uptime}, --sort {validatorName,tokensAmount,votingPower,commissionRate,status,uptime}
                        Sort by given column. Default: votingPower (default: votingPower)
  --descend             Flag to sort in descending order (lowest first) (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```