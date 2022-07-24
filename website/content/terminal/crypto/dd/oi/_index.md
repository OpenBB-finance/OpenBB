```
usage: oi [-i {0, 1, 2, 4}]
            [--export {csv,json,xlsx}] [-h]
```

Display the open interest per exchange for a certain cryptocurrency. [Source: https://bybt.gitbook.io]
Crypto must be loaded (e.g., `load btc`) before running this feature.

The total Bitcoin futures open interest across cryptocurrency exchanges, where open interest is calculated as the estimated notional value of all open futures positions, or the aggregate dollar value of outstanding contract specified BTC deliverables. Includes the largest exchanges with trustworthy reporting of exchange volume metrics.

Interval:

- ALL: 0
- 1H: 2
- 4H: 1
- 12H: 4

```
optional arguments:
  -i INTERV --interval INTERV   Interval frequency (default: 0)
  --export {csv,json,xlsx}      Export dataframe data to csv,json,xlsx file (default: )
  -h, --help                    show this help message (default: False)
```

![oi](https://user-images.githubusercontent.com/46355364/154086745-17c2b33a-e1bf-40b1-8ac8-3422fe081e96.png)
