```
usage: cpexchanges
                   [--vs {BTC,ETH,USD,EUR,PLN,KRW,GBP,CAD,JPY,RUB,TRY,NZD,AUD,CHF,UAH,HKD,SGD,NGN,PHP,MXN,BRL,THB,CLP,CNY,CZK,DKK,HUF,IDR,ILS,INR,MYR,NOK,PKR,SEK,TWD,ZAR,VND,BOB,COP,PEN,ARS,ISK}]
                   [-t TOP] [-s {rank,name,currencies,markets,fiats,confidence,volume_24h,volume_7d,volume_30d,sessions_per_month}] [--descend]
                   [--export {csv,json,xlsx}] [-h]
```

Show all exchanges from CoinPaprika You can display only top N number of coins with --top parameter. You can sort data by rank, name, currencies, markets, fiats, confidence, volume_24h,volume_7d ,volume_30d, sessions_per_month --sort parameter and also with --descend flag to sort descending.
Displays: rank, name, currencies, markets, fiats, confidence, volume_24h, volume_7d ,volume_30d, sessions_per_month

```
optional arguments:
  --vs {BTC,ETH,USD,EUR,PLN,KRW,GBP,CAD,JPY,RUB,TRY,NZD,AUD,CHF,UAH,HKD,SGD,NGN,PHP,MXN,BRL,THB,CLP,CNY,CZK,DKK,HUF,IDR,ILS,INR,MYR,NOK,PKR,SEK,TWD,ZAR,VND,BOB,COP,PEN,ARS,ISK}
                        Quoted currency. Default USD (default: USD)
  -t TOP, --top TOP     Limit of records (default: 20)
  -s {rank,name,currencies,markets,fiats,confidence,volume_24h,volume_7d,volume_30d,sessions_per_month}, --sort {rank,name,currencies,markets,fiats,confidence,volume_24h,volume_7d,volume_30d,sessions_per_month}
                        Sort by given column. Default: rank (default: rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
