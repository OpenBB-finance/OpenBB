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

Example:
```
2022 Feb 16, 08:45 (✨) /stocks/options/ $ calc -s 30 -p 6 -m 1 -M 50

Strike: $30.0
Premium: $6.0
Breakeven price: $36.0
Max profit: Unlimited
Max loss: $-600.0
```

![calc](https://user-images.githubusercontent.com/46355364/154277755-a6640bee-8621-4a7d-9fc6-9c197daca0e1.png)
