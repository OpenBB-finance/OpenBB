```text
usage: hcorr [-t {o,h,l,c,a}] [-s START] [-h]
```

A correlation heatmap for the selected tickers, using optional arguments described below. Scores range from +1 to -1 with 0 being completely neutral. 

```
optional arguments:
  -t {o,h,l,c,a,r}, --type {o,h,l,c,a,r}
                        Candle data to use: o-open, h-high, l-low, c-close, a-adjusted close, r-returns. (default: a)
  -s START, --start START
                        The starting date (format YYYY-MM-DD) of the stock (default: 2021-06-08)
  --display-full-matrix
                        Display all matrix values, rather than masking off half. (default: False)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
  --raw                 Flag to display raw data (default: False)
```

![hcorr](https://user-images.githubusercontent.com/46355364/154073186-45336f5f-85e1-4cb9-9307-9694295b1f80.png)
