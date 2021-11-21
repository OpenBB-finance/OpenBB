```
usage: topbuys [-g {congress,senate,house}] [-p PAST_TRANSACTIONS_MONTHS] [-n NUM] [--raw]
                [--export {png,jpg,pdf,svg,csv,json,xlsx}] [-h]
```
Top stock buys amongst US representatives. Source: https://www.quiverquant.com

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
<img size="1400" alt="Feature Screenshot - topbuys" src="https://user-images.githubusercontent.com/85772166/142279690-1a80d4a0-5ede-4257-8ba5-ac6588b8ce76.png">
