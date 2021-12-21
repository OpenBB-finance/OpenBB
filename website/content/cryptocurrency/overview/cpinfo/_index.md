```
usage: cpinfo
              [--vs {BTC,ETH,USD,EUR,PLN,KRW,GBP,CAD,JPY,RUB,TRY,NZD,AUD,CHF,UAH,HKD,SGD,NGN,PHP,MXN,BRL,THB,CLP,CNY,CZK,DKK,HUF,IDR,ILS,INR,MYR,NOK,PKR,SEK,TWD,ZAR,VND,BOB,COP,PEN,ARS,ISK}]
              [-l N] [-s {rank,name,symbol,price,volume_24h,circulating_supply,total_supply,max_supply,ath_price,market_cap,beta_value}]
              [--descend] [--export {csv,json,xlsx}] [-h]
```

Show basic coin information for all coins from CoinPaprika API You can display only N number of coins with --limit parameter. You can sort data by
rank, name, symbol, price, volume_24h, circulating_supply, total_supply, max_supply, market_cap, beta_value, ath_price --sort parameter and also with
--descend flag to sort descending. Displays: rank, name, symbol, price, volume_24h, circulating_supply, total_supply, max_supply, market_cap, beta_value, ath_price

```
optional arguments:
  --vs {BTC,ETH,USD,EUR,PLN,KRW,GBP,CAD,JPY,RUB,TRY,NZD,AUD,CHF,UAH,HKD,SGD,NGN,PHP,MXN,BRL,THB,CLP,CNY,CZK,DKK,HUF,IDR,ILS,INR,MYR,NOK,PKR,SEK,TWD,ZAR,VND,BOB,COP,PEN,ARS,ISK}
                        Quoted currency. Default USD (default: USD)
  -l N, --limit N     Limit of records (default: 20)
  -s {rank,name,symbol,price,volume_24h,circulating_supply,total_supply,max_supply,ath_price,market_cap,beta_value}, --sort {rank,name,symbol,price,volume_24h,circulating_supply,total_supply,max_supply,ath_price,market_cap,beta_value}
                        Sort by given column. Default: rank (default: rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
