```
usage: topbuys [-g {congress,senate,house}] [-p PAST_TRANSACTIONS_MONTHS] [-n NUM] [--raw]
                [--export {png,jpg,pdf,svg,csv,json,xlsx}] [-h]
```
Top buys for government trading. [Source: www.quiverquant.com]

```
optional arguments:
  -g {congress,senate,house}, --govtype {congress,senate,house}
  -p PAST_TRANSACTIONS_MONTHS, --past_transactions_months PAST_TRANSACTIONS_MONTHS
                        Past transaction months (default: 6)
  -n NUM, --num NUM     Number of top tickers (default: 10)
  --raw                 Print raw data. (default: False)
  --export {png,jpg,pdf,svg,csv,json,xlsx}
                        Export plot to png,jpg,pdf,svg file or export dataframe to csv,json,xlsx (default: )
  -h, --help            show this help message (default: False)
```
