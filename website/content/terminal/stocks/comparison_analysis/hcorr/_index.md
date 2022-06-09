```text
usage: hcorr [-t {o,h,l,c,a}] [-s START] [-h]
```

A correlation heatmap for the selected tickers, using optional arguments described below. Scores range from +1 to -1 with 0 being completely neutral. 

```
optional arguments:
  -t {o,h,l,c,a}, --type {o,h,l,c,a}
                        Candle data to use: o-open, h-high, l-low, c-close, a-adjusted close. (default: a)
  -s START, --start START
                        The starting date (format YYYY-MM-DD) of the stock (default: 2021-02-14)
  -h, --help            show this help message (default: False)
  --display-full-matrix Display all values in the matrix, rather than masking off half (default: False)
  --raw                 show the raw output as a table in the terminal window (default: False)
```

![hcorr](https://user-images.githubusercontent.com/46355364/154073186-45336f5f-85e1-4cb9-9307-9694295b1f80.png)
