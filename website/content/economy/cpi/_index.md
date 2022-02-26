```
usage: cpi [-i {semiannual,monthly}] [-s START] [--raw] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

Get historical inflation numbers for the United States. Source: https://www.alphavantage.co/documentation/

```
optional arguments:
  -i {semiannual,monthly}, --interval {semiannual,monthly}
                        Interval for GDP data (default: semiannual)
  -s START, --start START
                        Start year. (default: 2010)
  --raw                 Display raw data (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```

Example

![cpi semi annually](https://user-images.githubusercontent.com/46355364/154036181-e3f51b7b-a90a-4c1e-ada3-a225b0e82a1f.png)
