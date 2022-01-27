```
usage: trend [-s START] [-hr HOUR] [-n NUMBER] [-h] [--export {csv,json,xlsx}] [-l LIMIT]

```

Show most talked about tickers within the last one hour. Source: [Sentiment Investor]

```
optional arguments:
  -s START, --start START
                        The starting date (format YYYY-MM-DD). Default: Today (default: 2022-01-26)
  -hr HOUR, --hour HOUR
                        Hour of the day in the 24-hour notation. Example: 14 (default: 0)
  -n NUMBER, --number NUMBER
                        Number of results returned from Sentiment Investor. Default: 10 (default: 10)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 10)
```
