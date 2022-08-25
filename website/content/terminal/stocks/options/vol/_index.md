```
usage: vol [-m MIN] [-M MAX] [-c] [-p] [--source {tradier,yf}] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

Plot volume. Volume refers to the number of contracts traded today.

```
optional arguments:
  -m MIN, --min MIN          Min strike to plot (default: -1)
  -M MAX, --max MAX          Max strike to plot (default: -1)
  -c, --calls                Flag to plot call options only (default: False)
  -p, --puts                 Flag to plot put options only (default: False)
  --source  {tradier ,yf}    Source to get data from (default: tradier)
  -h, --help                 show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```

![vol](https://user-images.githubusercontent.com/46355364/154291303-c23edf53-4242-4d9b-a45e-22ce8a633aa8.png)
