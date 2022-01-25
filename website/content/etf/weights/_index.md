```text
usage: weights [-m MIN] [--raw] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]

Look at ETF sector holdings

optional arguments:
  -m MIN, --min MIN     Minimum positive float to display sector (default: 5)
  --raw                 Only output raw data (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```

Displays the weighted holdings of the loaded ETF by sector.

<img width="1400" alt="weights" src="https://user-images.githubusercontent.com/85772166/150070875-39cd9c03-5cdd-4457-915f-48ecf5249c41.png">