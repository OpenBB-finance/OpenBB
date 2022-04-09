```
usage: rsi [-p PERIODS] [-u HIGH] [-l LOW] [--spy] [--no_bench] [--no_short] [-h] [--export {csv,json,xlsx}]
```

Strategy that buys when the stock is less than a threshold and shorts when it exceeds a threshold.

```
optional arguments:
  -p PERIODS, --periods PERIODS
                        Number of periods for RSI calculation (default: 14)
  -u HIGH, --high HIGH  High (upper) RSI Level (default: 70)
  -l LOW, --low LOW     Low RSI Level (default: 30)
  --spy                 Flag to add spy hold comparison (default: False)
  --no_bench            Flag to not show buy and hold comparison (default: False)
  --no_short            Flag that disables the short sell (default: True)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

![rsi](https://user-images.githubusercontent.com/46355364/154292682-4a666507-dfc6-440d-a719-c7f734f55aee.png)
