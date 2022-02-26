```
usage: tyld [-i {daily,weekly,monthly}] [-m {3m,5y,10y,30y}] [-s START] [--raw] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

Get historical Treasury Yield [Source: Alpha Vantage]

```
optional arguments:
  -i {daily,weekly,monthly}, --interval {daily,weekly,monthly}
                        Interval for treasury data (default: weekly)
  -m {3m,5y,10y,30y}, --maturity {3m,5y,10y,30y}
                        Maturity timeline for treasury (default: 5y)
  -s START, --start START
                        Start date. (default: 2021-02-14 11:38:01.977328)
  --raw                 Display raw data (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```

![tyld](https://user-images.githubusercontent.com/46355364/154045710-b46d9989-9c5b-4095-8387-6a77b6d4004a.png)
