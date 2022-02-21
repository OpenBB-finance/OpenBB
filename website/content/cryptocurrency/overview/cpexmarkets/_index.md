```
usage: cpexmarkets [-e EXCHANGE] [-l N]
                   [-s {pair,base_currency_name,quote_currency_name,category,reported_volume_24h_share,trust_score,market_url}] [--descend] [-l]
                   [--export {csv,json,xlsx}] [-h]
```

Get all exchange markets found for given exchange You can display only display N number records with --limit parameter. You can sort data by pair, base_currency_name, quote_currency_name, market_url, category, reported_volume_24h_share, trust_score --sort parameter and also with --descend flag to sort descending. You can use additional flag --urls to see urls for each market Displays: exchange_id, pair, base_currency_name,
quote_currency_name, market_url, category, reported_volume_24h_share, trust_score,

```
optional arguments:
  -e EXCHANGE, --exchange EXCHANGE
                        Identifier of exchange e.g for Binance Exchange -> binance (default: binance)
  -l N, --limit N     Limit of records (default: 10)
  -s {pair,base_currency_name,quote_currency_name,category,reported_volume_24h_share,trust_score,market_url}, --sort {pair,base_currency_name,quote_currency_name,category,reported_volume_24h_share,trust_score,market_url}
                        Sort by given column. Default: reported_volume_24h_share (default: reported_volume_24h_share)
  --descend             Flag to sort in descending order (lowest first) (default: False)
  -u, --urls           Flag to show urls. If you will use that flag you will see only: exchange, pair, trust_score, market_url columns (default:
                        False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 08:18 (✨) /crypto/ov/ $ cpexmarkets
                                                     Exchange Markets
┌─────────────┬───────────┬────────────────────┬─────────────────────┬──────────┬───────────────────────────┬─────────────┐
│ exchange_id │ pair      │ base_currency_name │ quote_currency_name │ category │ reported_volume_24h_share │ trust_score │
├─────────────┼───────────┼────────────────────┼─────────────────────┼──────────┼───────────────────────────┼─────────────┤
│ binance     │ BTC/USDT  │ Bitcoin            │ Tether              │ Spot     │ 14.25                     │ high        │
├─────────────┼───────────┼────────────────────┼─────────────────────┼──────────┼───────────────────────────┼─────────────┤
│ binance     │ ETH/USDT  │ Ethereum           │ Tether              │ Spot     │ 11.87                     │ high        │
├─────────────┼───────────┼────────────────────┼─────────────────────┼──────────┼───────────────────────────┼─────────────┤
│ binance     │ BTC/BUSD  │ Bitcoin            │ Binance USD         │ Spot     │ 4.44                      │ high        │
├─────────────┼───────────┼────────────────────┼─────────────────────┼──────────┼───────────────────────────┼─────────────┤
│ binance     │ BNB/USDT  │ Binance Coin       │ Tether              │ Spot     │ 3.58                      │ medium      │
├─────────────┼───────────┼────────────────────┼─────────────────────┼──────────┼───────────────────────────┼─────────────┤
│ binance     │ BUSD/USDT │ Binance USD        │ Tether              │ Spot     │ 3.54                      │ high        │
├─────────────┼───────────┼────────────────────┼─────────────────────┼──────────┼───────────────────────────┼─────────────┤
│ binance     │ ETH/BUSD  │ Ethereum           │ Binance USD         │ Spot     │ 2.97                      │ high        │
├─────────────┼───────────┼────────────────────┼─────────────────────┼──────────┼───────────────────────────┼─────────────┤
│ binance     │ SLP/USDT  │ Smooth Love Potion │ Tether              │ Spot     │ 2.86                      │ medium      │
├─────────────┼───────────┼────────────────────┼─────────────────────┼──────────┼───────────────────────────┼─────────────┤
│ binance     │ SHIB/USDT │ Shiba Inu          │ Tether              │ Spot     │ 2.41                      │ high        │
├─────────────┼───────────┼────────────────────┼─────────────────────┼──────────┼───────────────────────────┼─────────────┤
│ binance     │ XRP/USDT  │ XRP                │ Tether              │ Spot     │ 2.01                      │ high        │
├─────────────┼───────────┼────────────────────┼─────────────────────┼──────────┼───────────────────────────┼─────────────┤
│ binance     │ SOL/USDT  │ Solana             │ Tether              │ Spot     │ 1.95                      │ high        │
└─────────────┴───────────┴────────────────────┴─────────────────────┴──────────┴───────────────────────────┴─────────────┘
```
