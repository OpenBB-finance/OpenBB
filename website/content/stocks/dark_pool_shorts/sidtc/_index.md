```
usage: sidtc [-n NUM] [-s {float,dtc,si}] [--export {csv,json,xlsx}] [-h]
```

Print short interest and days to cover. [Source: Stockgrid]

```
optional arguments:
  -n NUM, --number NUM  Number of top tickers to show (default: 10)
  -s {float,dtc,si}, --sort {float,dtc,si}
                        Field for which to sort by, where 'float': Float Short %, 'dtc': Days to Cover, 'si': Short Interest (default: float)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
