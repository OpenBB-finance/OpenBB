```
usage: ps
          [--vs {BTC,ETH,USD,EUR,PLN,KRW,GBP,CAD,JPY,RUB,TRY,NZD,AUD,CHF,UAH,HKD,SGD,NGN,PHP,MXN,BRL,THB,CLP,CNY,CZK,DKK,HUF,IDR,ILS,INR,MYR,NOK,PKR,SEK,TWD,ZAR,VND,BOB,COP,PEN,ARS,ISK}]
          [--export {csv,json,xlsx}] [-h]
```

Get price and supply related metrics for given coin.

```
optional arguments:
  --vs {BTC,ETH,USD,EUR,PLN,KRW,GBP,CAD,JPY,RUB,TRY,NZD,AUD,CHF,UAH,HKD,SGD,NGN,PHP,MXN,BRL,THB,CLP,CNY,CZK,DKK,HUF,IDR,ILS,INR,MYR,NOK,PKR,SEK,TWD,ZAR,VND,BOB,COP,PEN,ARS,ISK}
                        Quoted currency. Default USD (default: USD)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 15, 07:46 (✨) /crypto/dd/ $ ps
                  Coin Information
┌────────────────────────────┬─────────────────────┐
│ Metric                     │ Value               │
├────────────────────────────┼─────────────────────┤
│ id                         │ btc-bitcoin         │
├────────────────────────────┼─────────────────────┤
│ name                       │ Bitcoin             │
├────────────────────────────┼─────────────────────┤
│ symbol                     │ BTC                 │
├────────────────────────────┼─────────────────────┤
│ rank                       │ 1                   │
├────────────────────────────┼─────────────────────┤
│ circulating_supply         │ 18.959 M            │
├────────────────────────────┼─────────────────────┤
│ total_supply               │ 18.959 M            │
├────────────────────────────┼─────────────────────┤
│ max_supply                 │ 21 M                │
├────────────────────────────┼─────────────────────┤
│ beta_value                 │ 0.896               │
├────────────────────────────┼─────────────────────┤
│ first_data_at              │ 2010-07-17 00:00:00 │
├────────────────────────────┼─────────────────────┤
│ last_updated               │ 2022-02-15 12:43:09 │
├────────────────────────────┼─────────────────────┤
│ usd_price                  │ 44.331 K            │
├────────────────────────────┼─────────────────────┤
│ usd_volume_24h             │ 108.460 B           │
├────────────────────────────┼─────────────────────┤
│ usd_volume_24h_change_24h  │ 122.920             │
├────────────────────────────┼─────────────────────┤
│ usd_market_cap             │ 840.463 B           │
├────────────────────────────┼─────────────────────┤
│ usd_market_cap_change_24h  │ 4.540               │
├────────────────────────────┼─────────────────────┤
│ usd_percent_change_15m     │ 0.020               │
├────────────────────────────┼─────────────────────┤
│ usd_percent_change_30m     │ -0.200              │
├────────────────────────────┼─────────────────────┤
│ usd_percent_change_1h      │ -0.100              │
├────────────────────────────┼─────────────────────┤
│ usd_percent_change_6h      │ 1.450               │
├────────────────────────────┼─────────────────────┤
│ usd_percent_change_12h     │ 3.980               │
├────────────────────────────┼─────────────────────┤
│ usd_percent_change_24h     │ 4.530               │
├────────────────────────────┼─────────────────────┤
│ usd_percent_change_7d      │ 2.010               │
├────────────────────────────┼─────────────────────┤
│ usd_percent_change_30d     │ 2.860               │
├────────────────────────────┼─────────────────────┤
│ usd_percent_change_1y      │ -6.670              │
├────────────────────────────┼─────────────────────┤
│ usd_ath_price              │ 68.692 K            │
├────────────────────────────┼─────────────────────┤
│ usd_ath_date               │ 2021-11-10 16:51:15 │
├────────────────────────────┼─────────────────────┤
│ usd_percent_from_price_ath │ -35.370             │
└────────────────────────────┴─────────────────────┘
```
