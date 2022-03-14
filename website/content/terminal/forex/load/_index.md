```
usage: load [-r {i,d,w,m}] [-i {1,5,15,30,60}] [-s START_DATE] [-h]
```

Load historical exchange rate data.

```
optional arguments:
  -r {i,d,w,m}, --resolution {i,d,w,m}
                        Resolution of data. Can be intraday, daily, weekly or monthly (default: d)
  -i {1,5,15,30,60}, --interval {1,5,15,30,60}
                        Interval of intraday data. Can be 1, 5, 15, 30 or 60. (default: 5)
  -s START_DATE, --start_date START_DATE
                        Start date of data. (default: 2020-11-01 16:41:01.349343)
  -h, --help            show this help message (default: False)
```
