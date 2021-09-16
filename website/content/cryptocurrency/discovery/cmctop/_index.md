```
usage: cmctop [-t TOP] [-s {Symbol,CMC_Rank,LastPrice,DayPctChange,MarketCap}] [--descend] [--export {csv,json,xlsx}] [-h]
```

This gets the top ranked coins from coinmarketcap.com

```
optional arguments:
  -t TOP, --top TOP     Limit of records (default: 15)
  -s {Symbol,CMC_Rank,LastPrice,DayPctChange,MarketCap}, --sort {Symbol,CMC_Rank,LastPrice,DayPctChange,MarketCap}
                        column to sort data by. (default: CMC_Rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)

```
