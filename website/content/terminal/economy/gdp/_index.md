```
usage: gdp [-i {annual,quarter}] [-s START] [--raw] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

US Real GDP, on either annual or quarterly intervals. [Source: Alpha Vantage]

```
optional arguments:
  -i {annual,quarter}, --interval {annual,quarter}
                        Interval for GDP data (default: annual)
  -s START, --start START
                        Start year. Quarterly only goes back to 2002. (default: 2010)
  --raw                 Display raw data (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```

Example:
![gdp](https://user-images.githubusercontent.com/46355364/154037947-b2464523-9dd3-497d-abd5-5ac403f92788.png)
