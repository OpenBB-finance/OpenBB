```
usage: topbuys [-g {congress,senate,house}] [-p PAST_TRANSACTIONS_MONTHS] [-l LIMIT] [--raw] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

Top stock buys amongst US representatives. Source: https://www.quiverquant.com

```
optional arguments:
  -g {congress,senate,house}, --govtype {congress,senate,house}
  -p PAST_TRANSACTIONS_MONTHS, --past_transactions_months PAST_TRANSACTIONS_MONTHS
                        Past transaction months (default: 6)
  -l LIMIT, --limit LIMIT
                        Limit of top tickers to display (default: 10)
  --raw                 Print raw data. (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```

![topbuys](https://user-images.githubusercontent.com/46355364/154266344-944b0c5b-f7b0-4fdb-a020-a93565f6c13c.png)
