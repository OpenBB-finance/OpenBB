```
usage: lasttrades [-g {congress,senate,house}] [-p PAST_TRANSACTIONS_DAYS] [-r REPRESENTATIVE] [-h]
                   [--export {png,jpg,pdf,svg,csv,json,xlsx}]
```

Latest government representative trading, searchable by representative. [Source: www.quiverquant.com]

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
<img size="1400" alt="Feature Screenshot - lasttrades" src="https://user-images.githubusercontent.com/85772166/141689036-49a7e6ac-a978-435e-a59f-953f476af5f1.png">
