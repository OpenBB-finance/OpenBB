```
usage: topsells [-g {congress,senate,house}] [-p PAST_TRANSACTIONS_MONTHS] [-l LIMIT] [--raw] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

Companies experiencing the most stock sales by US governement representatives. [Source: www.quiverquant.com]

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

![topsells](https://user-images.githubusercontent.com/46355364/154266700-49526982-e5fd-4be1-b415-17816cfe2c75.png)
