```
usage: prom [-n N_NUM] [-t N_TOP] [--tier {T1,T2,OTCE}] [--export {csv,json,xlsx}] [-h]
```

Display dark pool (ATS) data of tickers with growing trades activity

```
optional arguments:
  -n N_NUM, --num N_NUM
                        Number of tickers to filter from entire ATS data based on the sum of the total weekly shares quantity. (default: 1000)
  -t N_TOP, --top N_TOP
                        List of tickers from most promising with better linear regression slope. (default: 5)
  --tier {T1,T2,OTCE}   Tier to process data from. (default: )
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
