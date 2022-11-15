```
usage: exchanges [-l LIMIT] [-s {rank,name,currencies,markets,fiats,confidence,volume_24h,volume_7d,volume_30d,sessions_per_month}] [--reverse] [-u]
                 [--vs {BTC,ETH,USD,EUR,PLN,KRW,GBP,CAD,JPY,RUB,TRY,NZD,AUD,CHF,UAH,HKD,SGD,NGN,PHP,MXN,BRL,THB,CLP,CNY,CZK,DKK,HUF,IDR,ILS,INR,MYR,NOK,PKR,SEK,TWD,ZAR,VND,BOB,COP,PEN,ARS,ISK}]
                 [-h] [--export EXPORT] [--source {CoinGecko,CoinPaprika}]
```

Shows Top Crypto Exchanges You can display only N number exchanges with --limit parameter. You can sort data by Trust_Score, Id, Name, Country,
Year_Established, Trade_Volume_24h_BTC with --sort and also with --reverse flag to sort ascending. Flag --urls will display urls. Displays:
Trust_Score, Id, Name, Country, Year_Established, Trade_Volume_24h_BTC

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        display N number records (default: 15)
  -s {rank,name,currencies,markets,fiats,confidence,volume_24h,volume_7d,volume_30d,sessions_per_month}, --sort {rank,name,currencies,markets,fiats,confidence,volume_24h,volume_7d,volume_30d,sessions_per_month}
                        Sort by given column. Default: Rank (default: Rank)
  -r, --reverse         Data is sorted in descending order by default.
                        Reverse flag will sort it in an ascending way.
                        Only works when raw data is displayed. (default: False)
  -u, --urls            Flag to add a url column. Works only with CoinGecko source (default: False)
  --vs {BTC,ETH,USD,EUR,PLN,KRW,GBP,CAD,JPY,RUB,TRY,NZD,AUD,CHF,UAH,HKD,SGD,NGN,PHP,MXN,BRL,THB,CLP,CNY,CZK,DKK,HUF,IDR,ILS,INR,MYR,NOK,PKR,SEK,TWD,ZAR,VND,BOB,COP,PEN,ARS,ISK}
                        Quoted currency. Default: USD. Works only with CoinPaprika source (default: USD)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
  --source {CoinGecko,CoinPaprika}
                        Data source to select from (default: CoinGecko)
```

Example:
```
2022 Feb 15, 08:12 (✨) /crypto/ov/ $ exchanges
                                                  Top CoinGecko Exchanges
┌──────┬─────────────┬────────────┬─────────────────────┬────────────────────────┬──────────────────┬──────────────────────┐
│ Rank │ Trust_Score │ Id         │ Name                │ Country                │ Year_Established │ Trade_Volume_24h_BTC │
├──────┼─────────────┼────────────┼─────────────────────┼────────────────────────┼──────────────────┼──────────────────────┤
│ 1    │ 10.00       │ binance    │ Binance             │ Cayman Islands         │ 2017.00          │ 307450.76            │
├──────┼─────────────┼────────────┼─────────────────────┼────────────────────────┼──────────────────┼──────────────────────┤
│ 2    │ 10.00       │ okex       │ OKX                 │ Belize                 │ 2013.00          │ 80452.05             │
├──────┼─────────────┼────────────┼─────────────────────┼────────────────────────┼──────────────────┼──────────────────────┤
│ 3    │ 10.00       │ gdax       │ Coinbase Exchange   │ United States          │ 2012.00          │ 68358.93             │
├──────┼─────────────┼────────────┼─────────────────────┼────────────────────────┼──────────────────┼──────────────────────┤
│ 4    │ 10.00       │ crypto_com │ Crypto.com Exchange │ Cayman Islands         │ 2019.00          │ 60342.43             │
├──────┼─────────────┼────────────┼─────────────────────┼────────────────────────┼──────────────────┼──────────────────────┤
│ 5    │ 10.00       │ kucoin     │ KuCoin              │ Seychelles             │ 2014.00          │ 53539.44             │
├──────┼─────────────┼────────────┼─────────────────────┼────────────────────────┼──────────────────┼──────────────────────┤
│ 6    │ 10.00       │ ftx_spot   │ FTX                 │ Antigua and Barbuda    │ 2019.00          │ 40360.67             │
├──────┼─────────────┼────────────┼─────────────────────┼────────────────────────┼──────────────────┼──────────────────────┤
│ 7    │ 10.00       │ huobi      │ Huobi Global        │ Seychelles             │ 2013.00          │ 34851.50             │
├──────┼─────────────┼────────────┼─────────────────────┼────────────────────────┼──────────────────┼──────────────────────┤
│ 8    │ 10.00       │ gate       │ Gate.io             │ Hong Kong              │ None             │ 30159.12             │
├──────┼─────────────┼────────────┼─────────────────────┼────────────────────────┼──────────────────┼──────────────────────┤
│ 9    │ 10.00       │ bitmart    │ BitMart             │ Cayman Islands         │ 2017.00          │ 21782.37             │
├──────┼─────────────┼────────────┼─────────────────────┼────────────────────────┼──────────────────┼──────────────────────┤
│ 10   │ 10.00       │ kraken     │ Kraken              │ United States          │ 2011.00          │ 19819.63             │
├──────┼─────────────┼────────────┼─────────────────────┼────────────────────────┼──────────────────┼──────────────────────┤
│ 11   │ 10.00       │ bitfinex   │ Bitfinex            │ British Virgin Islands │ 2014.00          │ 13254.81             │
├──────┼─────────────┼────────────┼─────────────────────┼────────────────────────┼──────────────────┼──────────────────────┤
│ 12   │ 10.00       │ bybit_spot │ Bybit (spot)        │ None                   │ 2018.00          │ 7823.03              │
├──────┼─────────────┼────────────┼─────────────────────┼────────────────────────┼──────────────────┼──────────────────────┤
│ 13   │ 10.00       │ binance_us │ Binance US          │ United States          │ 2019.00          │ 7384.36              │
├──────┼─────────────┼────────────┼─────────────────────┼────────────────────────┼──────────────────┼──────────────────────┤
│ 14   │ 10.00       │ gemini     │ Gemini              │ United States          │ 2014.00          │ 2876.09              │
├──────┼─────────────┼────────────┼─────────────────────┼────────────────────────┼──────────────────┼──────────────────────┤
│ 15   │ 10.00       │ bitkub     │ Bitkub              │ Thailand               │ 2018.00          │ 2163.91              │
└──────┴─────────────┴────────────┴─────────────────────┴────────────────────────┴──────────────────┴──────────────────────┘
```
