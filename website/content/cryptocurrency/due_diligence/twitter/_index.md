```
usage: twitter [-l N] [-s {date,user_name,status,retweet_count,like_count}] [--descend] [--export {csv,json,xlsx}] [-h]
```

Show last 10 tweets for given coin. You can display only N number of tweets with --limit parameter. You can sort data by date, user_name, status,
retweet_count, like_count --sort parameter and also with --descend flag to sort descending. Displays: date, user_name, status, retweet_count, like_count

```
optional arguments:
  -l N, --limit N     Limit of records (default: 10)
  -s {date,user_name,status,retweet_count,like_count}, --sort {date,user_name,status,retweet_count,like_count}
                        Sort by given column. Default: date (default: date)
  --descend             Flag to sort in descending order (lowest first) (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
