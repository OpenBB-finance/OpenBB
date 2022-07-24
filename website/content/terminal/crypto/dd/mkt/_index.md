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

Example:
```
2022 Feb 15, 07:41 (✨) /crypto/dd/ $ mkt
                                          All Markets
┌─────────────────────┬──────────┬─────────────┬──────────────────┬───────────┬────────────────┐
│ exchange            │ pair     │ trust_score │ pct_volume_share │ usd_price │ usd_volume     │
├─────────────────────┼──────────┼─────────────┼──────────────────┼───────────┼────────────────┤
│ QB                  │ BTC/USDT │ low         │ 76.66            │ 44335.56  │ 83125013156.79 │
├─────────────────────┼──────────┼─────────────┼──────────────────┼───────────┼────────────────┤
│ Bitenium            │ BTC/USDT │ no_data     │ 1.70             │ 44337.16  │ 1840286891.89  │
├─────────────────────┼──────────┼─────────────┼──────────────────┼───────────┼────────────────┤
│ Binance             │ BTC/USDT │ high        │ 1.69             │ 44340.62  │ 1829582324.62  │
├─────────────────────┼──────────┼─────────────┼──────────────────┼───────────┼────────────────┤
│ Crypto.com Exchange │ BTC/USDT │ low         │ 1.41             │ 44329.00  │ 1524907447.06  │
├─────────────────────┼──────────┼─────────────┼──────────────────┼───────────┼────────────────┤
│ Indoex              │ BTC/USD  │ no_data     │ 0.71             │ 44257.37  │ 767372786.82   │
├─────────────────────┼──────────┼─────────────┼──────────────────┼───────────┼────────────────┤
│ Coinbase            │ BTC/USD  │ high        │ 0.65             │ 44305.95  │ 700692544.59   │
├─────────────────────┼──────────┼─────────────┼──────────────────┼───────────┼────────────────┤
│ Gleec BTC Exchange  │ BTC/USDT │ no_data     │ 0.63             │ 44353.43  │ 681039760.57   │
├─────────────────────┼──────────┼─────────────┼──────────────────┼───────────┼────────────────┤
│ HitBTC              │ BTC/USDT │ high        │ 0.63             │ 44351.01  │ 681002641.50   │
├─────────────────────┼──────────┼─────────────┼──────────────────┼───────────┼────────────────┤
│ Bequant             │ BTC/USDT │ low         │ 0.63             │ 44331.91  │ 679750799.42   │
├─────────────────────┼──────────┼─────────────┼──────────────────┼───────────┼────────────────┤
│ FMFW.io             │ BTC/USD  │ low         │ 0.63             │ 44205.77  │ 678518719.32   │
├─────────────────────┼──────────┼─────────────┼──────────────────┼───────────┼────────────────┤
│ Binance             │ BTC/BUSD │ high        │ 0.53             │ 44309.66  │ 572365752.88   │
├─────────────────────┼──────────┼─────────────┼──────────────────┼───────────┼────────────────┤
│ FTX (Spot)          │ BTC/USD  │ medium      │ 0.45             │ 44209.00  │ 492815904.21   │
├─────────────────────┼──────────┼─────────────┼──────────────────┼───────────┼────────────────┤
│ Huobi               │ BTC/USDT │ low         │ 0.44             │ 44340.66  │ 479152896.05   │
├─────────────────────┼──────────┼─────────────┼──────────────────┼───────────┼────────────────┤
│ Indoex              │ BTC/EUR  │ no_data     │ 0.42             │ 44250.15  │ 453236652.77   │
├─────────────────────┼──────────┼─────────────┼──────────────────┼───────────┼────────────────┤
│ Kucoin              │ BTC/USDT │ low         │ 0.40             │ 44341.16  │ 436318305.41   │
├─────────────────────┼──────────┼─────────────┼──────────────────┼───────────┼────────────────┤
│ Bitrue              │ BTC/USDT │ low         │ 0.37             │ 44337.33  │ 403067095.03   │
├─────────────────────┼──────────┼─────────────┼──────────────────┼───────────┼────────────────┤
│ Lbank               │ BTC/USDT │ low         │ 0.36             │ 44343.55  │ 385493474.14   │
├─────────────────────┼──────────┼─────────────┼──────────────────┼───────────┼────────────────┤
│ BigONE              │ BTC/USDT │ low         │ 0.35             │ 44334.78  │ 377459785.89   │
├─────────────────────┼──────────┼─────────────┼──────────────────┼───────────┼────────────────┤
│ Simex               │ BTC/USD  │ low         │ 0.33             │ 44237.02  │ 355967120.52   │
├─────────────────────┼──────────┼─────────────┼──────────────────┼───────────┼────────────────┤
│ DigiFinex           │ BTC/USDT │ high        │ 0.31             │ 44394.03  │ 339944185.15   │
└─────────────────────┴──────────┴─────────────┴──────────────────┴───────────┴────────────────┘
```
