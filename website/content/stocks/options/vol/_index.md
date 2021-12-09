```
usage: vol [-m MIN] [-M MAX] [-c] [-p] [-s {tr,yf}] [--export {csv,json,xlsx}] [-h]
```

Plot volume against strike prioce. Volume refers to the number of contracts traded today.

```
optional arguments:
  -m MIN, --min MIN     Min strike to plot (default: -1)
  -M MAX, --max MAX     Max strike to plot (default: -1)
  -c, --calls           Flag to plot call options only (default: False)
  -p, --puts            Flag to plot put options only (default: False)
  -s {tr,yf}, --source {tr,yf}
                        Source to get data from (default: tr)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
<img size-="1400" alt="Feature Screenshot - vol" src="https://user-images.githubusercontent.com/85772166/144265560-1558aca5-c2a5-4c62-931d-580554453bf8.png">
