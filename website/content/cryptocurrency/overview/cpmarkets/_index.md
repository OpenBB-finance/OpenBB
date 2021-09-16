```
usage: cpmarkets
                 [--vs {BTC,ETH,USD,EUR,PLN,KRW,GBP,CAD,JPY,RUB,TRY,NZD,AUD,CHF,UAH,HKD,SGD,NGN,PHP,MXN,BRL,THB,CLP,CNY,CZK,DKK,HUF,IDR,ILS,INR,MYR,NOK,PKR,SEK,TWD,ZAR,VND,BOB,COP,PEN,ARS,ISK}]
                 [-t TOP] [-s {rank,name,symbol,price,volume_24h,mcap_change_24h,pct_change_1h,pct_change_24h,ath_price,pct_from_ath}] [--descend]
                 [--export {csv,json,xlsx}] [-h]
```

Show market related (price, supply, volume) coin information for all coins on CoinPaprika. You can display only top N number of coins with --top
parameter. You can sort data by rank, name, symbol, price, volume_24h, mcap_change_24h, pct_change_1h, pct_change_24h, ath_price, pct_from_ath,
--sort parameter and also with --descend flag to sort descending. Displays: rank, name, symbol, price, volume_24h, mcap_change_24h, pct_change_1h,
pct_change_24h, ath_price, pct_from_ath,

```
optional arguments:
  --vs {BTC,ETH,USD,EUR,PLN,KRW,GBP,CAD,JPY,RUB,TRY,NZD,AUD,CHF,UAH,HKD,SGD,NGN,PHP,MXN,BRL,THB,CLP,CNY,CZK,DKK,HUF,IDR,ILS,INR,MYR,NOK,PKR,SEK,TWD,ZAR,VND,BOB,COP,PEN,ARS,ISK}
                        Quoted currency. Default USD (default: USD)
  -t TOP, --top TOP     Limit of records (default: 15)
  -s {rank,name,symbol,price,volume_24h,mcap_change_24h,pct_change_1h,pct_change_24h,ath_price,pct_from_ath}, --sort {rank,name,symbol,price,volume_24h,mcap_change_24h,pct_change_1h,pct_change_24h,ath_price,pct_from_ath}
                        Sort by given column. Default: rank (default: rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
