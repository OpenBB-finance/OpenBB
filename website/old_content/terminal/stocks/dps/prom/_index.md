```
usage: prom [-n N_NUM] [-l LIMIT] [-t {T1,T2,OTCE}] [-h] [--export {csv,json,xlsx}]
```

Display and filter dark pool (ATS) data of tickers with growing trades activity outside of the NYSE/NASDAQ/AMEX/CBOE/ICE systems. Source: http://finra-markets.morningstar.com/MarketData/EquityOptions/default.jsp

```
optional arguments:
  -n N_NUM, --num N_NUM
                        Number of tickers to filter from entire ATS data based on the sum of the total weekly shares quantity. (default: 1000)
  -l LIMIT, --limit LIMIT
                        Limit of most promising tickers to display. (default: 10)
  -t {T1,T2,OTCE}, --tier {T1,T2,OTCE}
                        Tier to process data from. (default: )
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

![prom](https://user-images.githubusercontent.com/46355364/154076323-2d031477-a70d-4065-b649-c8493fecdcbc.png)
