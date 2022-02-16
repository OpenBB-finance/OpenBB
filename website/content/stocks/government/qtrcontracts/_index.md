```
usage: qtrcontracts [-l LIMIT] [-a {total,upmom,downmom}] [--raw] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

Total value of contracts awarded to individual companiens. [Source: www.quiverquant.com]

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        Limit of tickers to get (default: 5)
  -a {total,upmom,downmom}, --analysis {total,upmom,downmom}
                        Analysis to look at contracts. 'Total' shows summed contracts. 'Upmom' shows highest sloped contacts while 'downmom' shows highest decreasing slopes. (default: total)
  --raw                 Print raw data. (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```
<img size="1400" alt="Feature Screenshot - qtrcontracts" src="https://user-images.githubusercontent.com/85772166/141689259-49939721-4250-40f1-80a7-ea5d935b8d5d.png">
