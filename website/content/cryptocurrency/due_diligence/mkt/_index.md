```
usage: mkt
           [--vs {BTC,ETH,USD,EUR,PLN,KRW,GBP,CAD,JPY,RUB,TRY,NZD,AUD,CHF,UAH,HKD,SGD,NGN,PHP,MXN,BRL,THB,CLP,CNY,CZK,DKK,HUF,IDR,ILS,INR,MYR,NOK,PKR,SEK,TWD,ZAR,VND,BOB,COP,PEN,ARS,ISK}]
           [-l N] [-s {pct_volume_share,exchange,pair,trust_score,volume,price}] [--descend] [-u] [--export {csv,json,xlsx}] [-h]
```

Get all markets found for given coin. You can display only N number of markets with --limit parameter. You can sort data by pct_volume_share,
exchange, pair, trust_score, volume, price --sort parameter and also with --descend flag to sort descending. You can use additional flag --urls to
see urls for each market Displays: exchange, pair, trust_score, volume, price, pct_volume_share,

```
optional arguments:
  --vs {BTC,ETH,USD,EUR,PLN,KRW,GBP,CAD,JPY,RUB,TRY,NZD,AUD,CHF,UAH,HKD,SGD,NGN,PHP,MXN,BRL,THB,CLP,CNY,CZK,DKK,HUF,IDR,ILS,INR,MYR,NOK,PKR,SEK,TWD,ZAR,VND,BOB,COP,PEN,ARS,ISK}
                        Quoted currency. Default USD (default: USD)
  -t TOP, --top TOP     Limit of records (default: 20)
  -s {pct_volume_share,exchange,pair,trust_score,volume,price}, --sort {pct_volume_share,exchange,pair,trust_score,volume,price}
                        Sort by given column. Default: pct_volume_share (default: pct_volume_share)
  --descend             Flag to sort in descending order (lowest first) (default: False)
  -u, --urls           Flag to show urls. If you will use that flag you will see only: exchange, pair, trust_score, market_url columns (default:
                        False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
