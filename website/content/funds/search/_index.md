```
usage: search [-b {name,issuer,isin,symbol}] [-f FUND] [-s {country,name,symbol,issuer,isin,asset_class,currency,underlying}] [-l LIMIT] [-a] [-h]
```
Search mutual funds in selected country based on selected field.

```
optional arguments:
  -b {name,issuer,isin,symbol}, --by {name,issuer,isin,symbol}
                        Field to search by (default: name)
  -f FUND, --fund FUND  Fund string to search for (default: None)
  -s {country,name,symbol,issuer,isin,asset_class,currency,underlying}, --sortby {country,name,symbol,issuer,isin,asset_class,currency,underlying}
                        Column to sort by (default: name)
  -l LIMIT, --limit LIMIT
                        Number of search results to show (default: 10)
  -a, --ascend          Sort in ascending order (default: False)
  -h, --help            show this help message (default: False)
```