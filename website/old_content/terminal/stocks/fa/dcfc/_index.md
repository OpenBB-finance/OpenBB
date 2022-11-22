```
usage: dcfc [-l LIMIT] [-q] [-h] [--export {csv,json,xlsx}]h]
```

Prints the discounted cash flow of a company over time including the DCF of today. The following fields are expected: DCF, Stock price, and Date. [Source: Financial Modeling Prep]

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        Limit of latest years/quarters. (default: 1)
  -q, --quarter         Quarter fundamental data flag. (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```
<img size="1400" alt-="Feature Screenshot - dcfc" src="https://user-images.githubusercontent.com/85772166/141524262-3bff332f-d11c-4cd3-9dc3-2f7a13a94a03.png">
