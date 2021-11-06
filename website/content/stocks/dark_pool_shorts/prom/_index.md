```
usage: prom [-n N_NUM] [-t N_TOP] [--tier {T1,T2,OTCE}] [--export {csv,json,xlsx}] [-h]
```

Display and filter dark pool (ATS) data of tickers with growing trades activity outside of the NYSE/NASDAQ/AMEX/CBOE/ICE systems. Source: http://finra-markets.morningstar.com/MarketData/EquityOptions/default.jsp
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
<img width="1400" alt="Feature Screenshot - prom" src="https://user-images.githubusercontent.com/85772166/140616333-f1ea7c43-663f-433b-b6fc-a8e514ec7a1e.png">
