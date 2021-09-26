```
usage: deposits [-t {internal_deposit,deposit}] [-l LIMIT] [-s {created_at,amount}] [--descend]
                [--export {csv,json,xlsx}] [-h]
```
Display a list of deposits for your account.
```
optional arguments:
  -t {internal_deposit,deposit}, --type {internal_deposit,deposit}
                        Deposit type. Either: internal_deposits (transfer between portfolios) or deposit
                        (default: deposit)
  -l LIMIT, --limit LIMIT
                        Limit parameter. (default: 20)
  -s {created_at,amount}, --sort {created_at,amount}
                        Sort by given column. Default: created_at (default: created_at)
  --descend             Flag to sort in descending order (lowest first) (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
