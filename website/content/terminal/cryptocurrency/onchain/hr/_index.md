```
usage: hr       [-c COIN]
                [-s INITIAL_DATE]
                [-u END_DATE]
                [-i {1h, 24h, 10m, 1w, 1month}]
                [--export {csv,json,xlsx}] [-h]
```

Display the average hash rate of a certain network.[Source: https://glassnode.org]

Supported assets: BTC, ETH

```
arguments:
  -c COIN --coin  COIN          Coin to check hashrate (BTC or ETH)
  -s DATE --since DATE          Start date (default: 1 year before, e.g., 2020-10-22)
  -u DATE --until DATE          End date (default: current day, e.g., 2021-10-22)
  -i INTERV --interval INTERV   Interval frequency (default: 24h)
  --export {csv,json,xlsx}      Export dataframe data to csv,json,xlsx file (default: )
  -h, --help                    show this help message (default: False)
```

![hr](https://user-images.githubusercontent.com/46355364/154067420-9fdd9324-c4f2-4bb4-91c1-4c675e4b45d1.png)
