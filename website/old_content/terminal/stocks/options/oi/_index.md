```
usage: oi [-m MIN] [-M MAX] [-c] [-p] [--source {tradier,yf}] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

Plot open interest. Open interest is the number of outstanding contracts, which typically represent one hundred shares.

```
optional arguments:
  -m MIN, --min MIN           Min strike to plot (default: -1)
  -M MAX, --max MAX           Max strike to plot (default: -1)
  -c, --calls                 Flag to plot call options only (default: False)
  -p, --puts                  Flag to plot put options only (default: False)
  --source  {tradier ,yf}     Source to get data from (default: tradier)

  -h, --help                  show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```

Example:

```
2022 Feb 16, 09:13 (🦋) /stocks/options/ $ load SPY

2022 Feb 16, 09:14 (🦋) /stocks/options/ $ exp 10
Expiration set to 2022-03-11

2022 Feb 16, 09:14 (🦋) /stocks/options/ $ oi
```

![oi](https://user-images.githubusercontent.com/46355364/154282811-b8b7d36b-2e4e-44c0-8026-b244d97a8608.png)
