```
usage: gtrades [-p PAST_TRANSACTIONS_MONTHS] [-g {congress,senate,house}] [--raw] [-h] [--export {png,jpg,pdf,svg,csv,json,xlsx}]
```

US Representatives trading in the loaded ticker. [Source: www.quiverquant.com]

```
optional arguments:
  -p PAST_TRANSACTIONS_MONTHS, --past_transactions_months PAST_TRANSACTIONS_MONTHS
                        Past transaction months (default: 6)
  -g {congress,senate,house}, --govtype {congress,senate,house}
  --raw                 Print raw data. (default: False)
  -h, --help            show this help message (default: False)
  --export {png,jpg,pdf,svg,csv,json,xlsx}
                        Export plot to png,jpg,pdf,svg file or export dataframe to csv,json,xlsx (default: )
```
<img size="1400" alt="Feature Screenshot - gtrades chart" src="https://user-images.githubusercontent.com/85772166/141688611-dddaeb53-b732-49f5-8ebb-b7599b316626.png">
<img size="1400" alt="Feature Screenshot - gtrades raw" src="https://user-images.githubusercontent.com/85772166/141688672-bc605098-6e18-4767-8ef8-66706ebe5606.png">
  
