```
usage: find [-c COIN] [-k {id,symbol,name}] [-t TOP] [--source {cp,cg,bin,cb}] [--export {csv,json,xlsx}] [-h]
```

Find similar coin by coin name,symbol or id. If you don't remember exact name or id of the Coin at CoinGecko, Binance, Coinbase or CoinPaprika you
can use this command to display coins with similar name, symbol or id to your search query. Example of usage: coin name is something like "polka". So
I can try: find -c polka -k name -t 25 It will search for coin that has similar name to polka and display top 25 matches. -c, --coin stands for coin
- you provide here your search query -k, --key it's a searching key. You can search by symbol, id or name of coin -t, --top it displays top N number
of records.

```
optional arguments:
  -c COIN, --coin COIN  Symbol Name or Id of Coin (default: None)
  -k {id,symbol,name}, --key {id,symbol,name}
                        Specify by which column you would like to search: symbol, name, id (default: symbol)
  -t TOP, --top TOP     Limit of records (default: 10)
  --source {cp,cg,bin,cb}
                        Source of data. (default: cg)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
