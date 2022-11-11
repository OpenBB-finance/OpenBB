```
usage: deposits [-t {internal_deposit,deposit}] [-l LIMIT] [-s {created_at,amount}] [--reverse]
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
  -r, --reverse         Data is sorted in descending order by default.
                        Reverse flag will sort it in an ascending way.
                        Only works when raw data is displayed. (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
