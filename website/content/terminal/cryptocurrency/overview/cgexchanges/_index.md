```
usage: cgexchanges [-l N] [-s {Rank,Trust_Score,Id,Name,Country,Year Established,Trade_Volume_24h_BTC}] [--descend] [-l] [--export {csv,json,xlsx}] [-h]
```

Shows Top Crypto Exchanges You can display only N number exchanges with --limit parameter. You can sort data by Trust_Score, Id, Name, Country,
Year_Established, Trade_Volume_24h_BTC with --sort and also with --descend flag to sort descending. Flag --urls will display urls. Displays:
Trust_Score, Id, Name, Country, Year_Established, Trade_Volume_24h_BTC

```
optional arguments:
  -l N, --limit N     display N number records (default: 15)
  -s {Rank,Trust_Score,Id,Name,Country,Year Established,Trade_Volume_24h_BTC}, --sort {Rank,Trust_Score,Id,Name,Country,Year Established,Trade_Volume_24h_BTC}
                        Sort by given column. Default: Rank (default: Rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  -u, --urls           Flag to show urls (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 08:12 (✨) /crypto/ov/ $ cgexchanges
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
