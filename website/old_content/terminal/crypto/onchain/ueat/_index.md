```
usage: ueat [-l N]
            [-s {date,uniqueSenders,transactions,averageGasPrice,mediumGasPrice,maximumGasPrice}]
            [-i {day,month,week}] [--reverse] [-h] [--export {csv,json,xlsx}]
```

Display number of unique ethereum addresses which made a transaction in given
time interval [Source: https://graphql.bitquery.io/]

```
optional arguments:
  -l N, --limit N     display N number records. (Maximum available time period
                        is 90 days.Depending on chosen time period, top N
                        records will be recalculated. E.g.For interval: month,
                        and top: 10, period of calculation equals to 300, but
                        because of max days limit: 90, it will only return
                        last 3 months (3 records). (default: 10)
  -s {date,uniqueSenders,transactions,averageGasPrice,mediumGasPrice,maximumGasPrice}, --sort {date,uniqueSenders,transactions,averageGasPrice,mediumGasPrice,maximumGasPrice}
                        Sort by given column. (default: date)
  -i {day,month,week}, --interval {day,month,week}
                        Time interval in which ethereum address made
                        transaction. month, week or day. Maximum time period
                        is 90 days (3 months, 14 weeks) (default: day)
  -r, --reverse         Data is sorted in descending order by default.
                        Reverse flag will sort it in an ascending way.
                        Only works when raw data is displayed. (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )

```
