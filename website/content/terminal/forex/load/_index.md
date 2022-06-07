```
usage: load [-t TICKER] [--source {yf,av,polygon}] [-r {i,d,w,m}] [-i {1min,2min,5min,15min,30min,60min,90min,1hour,1day,5day,1week,1month,3month}] [-s START_DATE] [-h]
```
Load historical exchange rate data.  Available data sources are Polygon, Alpha Vantage and YahooFinance.  Main default source is polygon, if a key is provided. To change it use
--source av
```
options:
  -t TICKER, --ticker TICKER
                        Currency pair to load. (default: None)
  --source {yf,av,polygon}
                        Source of historical data (default: polygon)
  -r {i,d,w,m}, --resolution {i,d,w,m}
                        [Alphavantage only] Resolution of data. Can be intraday, daily, weekly or monthly (default: d)
  -i {1min,2min,5min,15min,30min,60min,90min,1hour,1day,5day,1week,1month,3month}, --interval {1min,2min,5min,15min,30min,60min,90min,1hour,1day,5day,1week,1month,3month}
                        Interval of intraday data. Options: [YahooFinance] 1min, 2min, 5min, 15min, 30min, 60min, 90min, 1hour, 1day, 5day, 1week, 1month, 3month. [AlphaAdvantage]
                        1min, 5min, 15min, 30min, 60min (default: 1day)
  -s START_DATE, --start_date START_DATE
                        Start date of data. (default: 2021-05-26 15:04:04.138183)
  -h, --help            show this help message (default: False)

```