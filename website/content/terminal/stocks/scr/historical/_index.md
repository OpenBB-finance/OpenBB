```
usage: historical [-l LIMIT] [-n] [-s START] [-t {o,h,l,c,a}] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

Historical price comparison between similar companies [Source: Yahoo Finance]

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        Limit of the most shorted stocks to retrieve.
  -n, --no-scale        Flag to not put all prices on same 0-1 scale
  -s START, --start START
                        The starting date (format YYYY-MM-DD) of the historical price to plot
  -t {o,h,l,c,a}, --type {o,h,l,c,a}
                        type of candles: o-open, h-high, l-low, c-close, a-adjusted close.
  -h, --help            show this help message
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg
```

![historical](https://user-images.githubusercontent.com/46355364/153897343-65a26523-0fb1-4b92-8988-85eb84e92c33.png)
