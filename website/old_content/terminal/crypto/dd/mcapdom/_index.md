```
usage: mcapdom [-i {5m,15m,30m,1h,1d,1w}] [-s START] [-end END] [-h]
               [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

Display asset's percentage share of total crypto circulating market cap [Source: https://messari.io]

```
optional arguments:
  -i {5m,15m,30m,1h,1d,1w}, --interval {5m,15m,30m,1h,1d,1w}
                        Frequency interval. Default: 1d (default: 1d)
  -s START, --start START
                        Initial date. Default: A year ago (default: 2021-03-14)
  -end END, --end END   End date. Default: Today (default: 2022-03-14)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg
                        (default: )
```
