```
usage: historical [-t {o,h,l,c,a}] [-n] [-s START] [-h] [--export EXPORT]
```
Historical price comparison between similar companies.
```
optional arguments:
  -t {o,h,l,c,a}, --type {o,h,l,c,a}
                        Candle data to use: o-open, h-high, l-low, c-close, a-adjusted close. (default: a)
  -n, --normalize       Flag to normalize all prices on same 0-1 scale (default: False)
  -s START, --start START
                        The starting date (format YYYY-MM-DD) of the stock (default: 2021-03-23)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```

![historical](https://user-images.githubusercontent.com/46355364/154073378-935eddd4-167e-48e8-9e3d-34029e5ba42f.png)
