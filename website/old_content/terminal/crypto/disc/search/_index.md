```
usage: search [-q QUERY [QUERY ...]] [-c {currencies,exchanges,icos,people,tags,all}] [-l LIMIT] [-s {category,id,name}] [--reverse] [-h] [--export {csv,json,xlsx}]
```

Search over CoinPaprika API You can display only top N number of results with --top parameter. You can sort data by id, name , category --sort
parameter and also with --reverse flag to sort ascending. To choose category in which you are searching for use --cat/-c parameter. Available
categories: currencies|exchanges|icos|people|tags|all Displays: id, name, category

```
optional arguments:
  -q QUERY [QUERY ...], --query QUERY [QUERY ...]
                        phrase for search (default: None)
  -c {currencies,exchanges,icos,people,tags,all}, --cat {currencies,exchanges,icos,people,tags,all}
                        Categories to search: currencies|exchanges|icos|people|tags|all. Default: all (default: all)
  -l LIMIT, --limit LIMIT
                        Limit of records (default: 10)
  -s {category,id,name}, --sort {category,id,name}
                        Sort by given column. Default: id (default: id)
-r, --reverse           Data is sorted in descending order by default. Reverse flag will sort it in an ascending way.
                        Only works when raw data is displayed. (default: False)
-h, --help              show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:

```
2022 Feb 15, 06:51 (🦋) /crypto/disc/ $ search -q bitcoin
                      CoinPaprika Results
┌─────────────────────────┬──────────────────────┬────────────┐
│ id                      │ name                 │ category   │
├─────────────────────────┼──────────────────────┼────────────┤
│ bbtc-baby-bitcoin       │ Baby Bitcoin         │ currencies │
├─────────────────────────┼──────────────────────┼────────────┤
│ bc-bitcoin-confidential │ Bitcoin Confidential │ currencies │
├─────────────────────────┼──────────────────────┼────────────┤
│ bca-bitcoin-atom        │ Bitcoin Atom         │ currencies │
├─────────────────────────┼──────────────────────┼────────────┤
│ bcd-bitcoin-diamond     │ Bitcoin Diamond      │ currencies │
├─────────────────────────┼──────────────────────┼────────────┤
│ bcf-bitcoin-fast        │ Bitcoin Fast         │ currencies │
├─────────────────────────┼──────────────────────┼────────────┤
│ bch-bitcoin-cash        │ Bitcoin Cash         │ currencies │
├─────────────────────────┼──────────────────────┼────────────┤
│ bch-bitcoin-cash-token  │ Bitcoin Cash Token   │ currencies │
├─────────────────────────┼──────────────────────┼────────────┤
│ bci-bitcoin-interest    │ Bitcoin Interest     │ currencies │
├─────────────────────────┼──────────────────────┼────────────┤
│ bcr-bitcoinrock         │ BITCOINROCK          │ currencies │
├─────────────────────────┼──────────────────────┼────────────┤
│ bct-bitcointrust        │ BitcoinTrust         │ currencies │
└─────────────────────────┴──────────────────────┴────────────┘
```
