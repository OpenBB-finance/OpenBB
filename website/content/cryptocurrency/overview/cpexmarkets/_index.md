```
usage: cpexmarkets [-e EXCHANGE] [-t TOP]
                   [-s {pair,base_currency_name,quote_currency_name,category,reported_volume_24h_share,trust_score,market_url}] [--descend] [-l]
                   [--export {csv,json,xlsx}] [-h]
```

Get all exchange markets found for given exchange You can display only top N number of records with --top parameter. You can sort data by pair, base_currency_name, quote_currency_name, market_url, category, reported_volume_24h_share, trust_score --sort parameter and also with --descend flag to sort descending. You can use additional flag --links to see urls for each market Displays: exchange_id, pair, base_currency_name,
quote_currency_name, market_url, category, reported_volume_24h_share, trust_score,

```
optional arguments:
  -e EXCHANGE, --exchange EXCHANGE
                        Identifier of exchange e.g for Binance Exchange -> binance (default: binance)
  -t TOP, --top TOP     Limit of records (default: 10)
  -s {pair,base_currency_name,quote_currency_name,category,reported_volume_24h_share,trust_score,market_url}, --sort {pair,base_currency_name,quote_currency_name,category,reported_volume_24h_share,trust_score,market_url}
                        Sort by given column. Default: reported_volume_24h_share (default: reported_volume_24h_share)
  --descend             Flag to sort in descending order (lowest first) (default: False)
  -l, --links           Flag to show urls. If you will use that flag you will see only: exchange, pair, trust_score, market_url columns (default:
                        False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
