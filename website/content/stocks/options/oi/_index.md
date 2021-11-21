```
usage: oi [-m MIN] [-M MAX] [-c] [-p] [-s {tr,yf}] [--export {csv,json,xlsx}] [-h]
```

Plot of the open interest aross a selected chain. Open interest is the number of outstanding contracts, which typically represent one hundred shares. 

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
<img size="1400" alt="Feature Screenshot - oi" src="https://user-images.githubusercontent.com/85772166/142368338-403b2d8d-00ea-4052-a643-683f5ee79711.png">
