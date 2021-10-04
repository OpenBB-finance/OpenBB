```
usage: lasttrades [-g {congress,senate,house}] [-p PAST_TRANSACTIONS_DAYS] [-r REPRESENTATIVE] [-h]
                   [--export {png,jpg,pdf,svg,csv,json,xlsx}]
```

Last government trading trading. [Source: www.quiverquant.com]

```
optional arguments:
  -g {congress,senate,house}, --govtype {congress,senate,house}
  -p PAST_TRANSACTIONS_DAYS, --past_transactions_days PAST_TRANSACTIONS_DAYS
                        Past transaction days (default: 5)
  -r REPRESENTATIVE, --representative REPRESENTATIVE
                        Representative (default: )
  -h, --help            show this help message (default: False)
  --export {png,jpg,pdf,svg,csv,json,xlsx}
                        Export plot to png,jpg,pdf,svg file or export dataframe to csv,json,xlsx (default: )
```
