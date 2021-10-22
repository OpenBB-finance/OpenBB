```
usage: whales [-m MIN] [-t TOP]
             [-s {date,symbol,blockchain,amount,amount_usd,from,to}]
             [--descend] [-a] [--export {csv,json,xlsx}] [-h]
```

Display huge value transactions from major blockchains. [Source: https://docs.whale-alert.io/]

```
optional arguments:
  -m MIN, --min MIN     Minimum value of transactions. (default: 1000000)
  -t TOP, --top TOP     top N number of records (default: 10)
  -s {date,symbol,blockchain,amount,amount_usd,from,to}, --sort {date,symbol,blockchain,amount,amount_usd,from,to}
                        Sort by given column (default: date)
  --descend             Flag to sort in descending order (lowest first)
                        (default: True)
  -a, --address         Flag to show addresses of transactions (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default:
                        )
  -h, --help            show this help message (default: False)
```
