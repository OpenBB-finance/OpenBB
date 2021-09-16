```
usage: cbpairs [-t TOP] [-s {id,display_name,base_currency,quote_currency,base_min_size,base_max_size,min_market_funds,max_market_funds}] [--descend]
               [--export {csv,json,xlsx}] [-h]
```

Shows available trading pairs on Coinbase

```
optional arguments:
  -t TOP, --top TOP     top N number of news >=10 (default: 15)
  -s {id,display_name,base_currency,quote_currency,base_min_size,base_max_size,min_market_funds,max_market_funds}, --sort {id,display_name,base_currency,quote_currency,base_min_size,base_max_size,min_market_funds,max_market_funds}
                        Sort by given column. Default: id (default: id)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
