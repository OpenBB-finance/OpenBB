```
usage: headlines [-c COIN] [--export {csv,json,xlsx}] [-h]
```

Display sentiment analysis from FinBrain for chosen Cryptocurrencies

```
optional arguments:
  -c COIN, --coin COIN  Symbol of coin to load data for, ~100 symbols are available (default: BTC)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 07:52 (✨) /crypto/ $ headlines

date
2022-02-06    0.137
2022-02-07    0.137
2022-02-08    0.237
2022-02-09    0.123
2022-02-10    0.131
2022-02-11    0.014
2022-02-12   -0.057
2022-02-13     0.02
2022-02-14    0.103
2022-02-15    0.158
```
![headlines](https://user-images.githubusercontent.com/46355364/154066006-d281a8c8-bd25-4355-9cd5-3affd4477bd6.png)
