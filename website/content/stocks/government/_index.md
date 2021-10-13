```
usage: topsells [-g {congress,senate,house}] [-p PAST_TRANSACTIONS_MONTHS] [-n NUM] [--raw] [-h] [--export {png,jpg,pdf,svg}]
```

Top sells for government trading. [Source: www.quiverquant.com]

```
optional arguments:
  -g {congress,senate,house}, --govtype {congress,senate,house}
  -p PAST_TRANSACTIONS_MONTHS, --past_transactions_months PAST_TRANSACTIONS_MONTHS
                        Past transaction months (default: 6)
  -n NUM, --num NUM     Number of top tickers (default: 10)
  --raw                 Print raw data. (default: False)
  -h, --help            show this help message (default: False)
  --export {png,jpg,pdf,svg}
                        Export or figure into png, jpg, pdf, svg (default: )
```
