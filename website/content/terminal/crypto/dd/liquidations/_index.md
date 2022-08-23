```
usage: liquidations
            [--export {csv,json,xlsx}] [-h]
```

Display the liquidation data for a certain cryptocurrency. [Source: https://coinglass.github.io/API-Reference/]
Crypto must be loaded (e.g., `load btc`) before running this feature.

The  Liquidations counts the daily Liquidations of futures contracts across all exchanges and currencies. The liquidation history across all exchanges can be viewed through the historical Liquidations. 

```
optional arguments:
  --export {csv,json,xlsx}      Export dataframe data to csv,json,xlsx file (default: )
  -h, --help                    show this help message (default: False)
```

![oi](https://user-images.githubusercontent.com/1673206/186211230-e095fe05-6d86-4d6a-aa2d-dd84dee4ad52.png)