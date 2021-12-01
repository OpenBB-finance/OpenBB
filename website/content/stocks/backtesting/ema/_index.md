```
usage: ema [-l LENGTH] [--spy] [--no_bench] [--export {csv,json,xlsx}] [-h]
```

A simple investment strategy where stock is bought when Price > EMA(l)

```
optional arguments:
  -l LENGTH             EMA period to consider (default: 20)
  --spy                 Flag to add spy hold comparison (default: False)
  --no_bench            Flag to not show buy and hold comparison (default: False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

<img size="1400" alt="ema" src="https://user-images.githubusercontent.com/25267873/116769584-1eb37c80-aa35-11eb-898b-efa36d4a8f5c.png">
<img width="1400" alt="ema2" src="https://user-images.githubusercontent.com/25267873/116769582-1d824f80-aa35-11eb-94bd-ecd4abe3b415.png">
