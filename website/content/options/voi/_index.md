```
usage: voi [-v MIN_VOL] [-m MIN_SP] [-M MAX_SP] [-s {tr,yf}] [--export {csv,json,xlsx}] [-h]
```

Plots Volume + Open Interest of calls vs puts.

```
optional arguments:
  -v MIN_VOL, --minv MIN_VOL
                        minimum volume (considering open interest) threshold of the plot. (default: -1)
  -m MIN_SP, --min MIN_SP
                        minimum strike price to consider in the plot. (default: -1)
  -M MAX_SP, --max MAX_SP
                        maximum strike price to consider in the plot. (default: -1)
  -s {tr,yf}, --source {tr,yf}
                        Source to get data from (default: tr)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
