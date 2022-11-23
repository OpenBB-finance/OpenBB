```
usage: whales [-m MIN] [-l N]
             [-s {date,symbol,blockchain,amount,amount_usd,from,to}]
             [--reverse] [-a] [--export {csv,json,xlsx}] [-h]
```

Display huge value transactions from major blockchains. [Source: https://docs.whale-alert.io/]

```
optional arguments:
  -m MIN, --min MIN     Minimum value of transactions. (default: 1000000)
  -l N, --limit N       display N number of records (default: 10)
  -s {date,symbol,blockchain,amount,amount_usd,from,to}, --sort {date,symbol,blockchain,amount,amount_usd,from,to}
                        Sort by given column (default: date)
  -r, --reverse         Data is sorted in descending order by default.
                        Reverse flag will sort it in an ascending way.
                        Only works when raw data is displayed. (default: False)
  -a, --address         Flag to show addresses of transactions (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default:
                        )
  -h, --help            show this help message (default: False)
```
