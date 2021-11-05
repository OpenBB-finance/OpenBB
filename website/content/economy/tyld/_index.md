```
usage: tyld [-i {d,w,m}] [-m {3m,5y,10y,30y}] [-s START] [--raw] [-h] [--export {png,jpg,pdf,svg}]

Get historical Treasury Yield [Source: Alpha Vantage]

optional arguments:
  -i {d,w,m}, --interval {d,w,m}
                        Interval for treasury data (default: w)
  -m {3m,5y,10y,30y}, --maturity {3m,5y,10y,30y}
                        Maturity timeline for treasury (default: 5y)
  -s START, --start START
                        Start date. (default: 2020-11-04 14:03:29.757932)
  --raw                 Display raw data (default: False)
  -h, --help            show this help message (default: False)
  --export {png,jpg,pdf,svg}
                        Export or figure into png, jpg, pdf, svg (default: )
```
