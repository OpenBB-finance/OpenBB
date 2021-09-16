```
usage: rsi [-p PERIODS] [-u HIGH] [-l LOW] [--spy] [--no_bench] [--no_short] [--export {csv,json,xlsx}] [-h]
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
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

![rsi](https://user-images.githubusercontent.com/25267873/116769576-19eec880-aa35-11eb-9e60-f77a31e51db0.png)
<img width="980" alt="rsi2" src="https://user-images.githubusercontent.com/25267873/116769579-1c512280-aa35-11eb-928b-aa4e8b90c1ec.png">
