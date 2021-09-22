```
usage: calc [--put] [--sell] [-s STRIKE] [-p PREMIUM] [-m MIN] [-M MAX] [-h]
```

Calculate profit or loss for given option settings.

```
optional arguments:
  --put                 Flag to calculate put option (default: False)
  --sell                Flag to get profit chart of selling contract (default: False)
  -s STRIKE, --strike STRIKE
                        Option strike price (default: 10)
  -p PREMIUM, --premium PREMIUM
                        Premium price (default: 1)
  -m MIN, --min MIN     Min price to look at (default: -1)
  -M MAX, --max MAX     Max price to look at (default: -1)
  -h, --help            show this help message (default: False)
```
