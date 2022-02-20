```
usage: pairs [-l LIMIT] [-s {volumeUSD,token0.name,token0.symbol,token1.name,token1.symbol,volumeUSD,txCount}] [--descend] [-h] [--export {csv,json,xlsx}]
```

Display uniswap pools by volume. [Source: https://thegraph.com/en/]

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        Number of records to display (default: 10)
  -s {volumeUSD,token0.name,token0.symbol,token1.name,token1.symbol,volumeUSD,txCount}, --sort {volumeUSD,token0.name,token0.symbol,token1.name,token1.symbol,volumeUSD,txCount}
                        Sort by given column. Default: volumeUSD (default: volumeUSD)
  --descend             Flag to sort in descending order (lowest first) (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 15, 06:28 (✨) /crypto/defi/ $ pools
                                           Uniswap Pools
┌───────────────────────┬───────────────┬───────────────────┬───────────────┬───────────┬─────────┐
│ token0.name           │ token0.symbol │ token1.name       │ token1.symbol │ volumeUSD │ txCount │
├───────────────────────┼───────────────┼───────────────────┼───────────────┼───────────┼─────────┤
│ INFI                  │ INFI          │ Wrapped Ether     │ WETH          │ 99.5M     │ 41195   │
├───────────────────────┼───────────────┼───────────────────┼───────────────┼───────────┼─────────┤
│ UnFederalReserveToken │ eRSDL         │ Wrapped Ether     │ WETH          │ 994M      │ 148106  │
├───────────────────────┼───────────────┼───────────────────┼───────────────┼───────────┼─────────┤
│ Dinger Token          │ DINGER        │ Wrapped Ether     │ WETH          │ 99.4M     │ 27552   │
├───────────────────────┼───────────────┼───────────────────┼───────────────┼───────────┼─────────┤
│ CliffordInu           │ CLIFF         │ Wrapped Ether     │ WETH          │ 99.2M     │ 38398   │
├───────────────────────┼───────────────┼───────────────────┼───────────────┼───────────┼─────────┤
│ Wrapped Ether         │ WETH          │ Gen Shards        │ GS            │ 99M       │ 16773   │
├───────────────────────┼───────────────┼───────────────────┼───────────────┼───────────┼─────────┤
│ Wrapped Ether         │ WETH          │ 0x Protocol Token │ ZRX           │ 98.9M     │ 37163   │
├───────────────────────┼───────────────┼───────────────────┼───────────────┼───────────┼─────────┤
│ GET                   │ GET           │ Wrapped Ether     │ WETH          │ 98.9M     │ 21632   │
├───────────────────────┼───────────────┼───────────────────┼───────────────┼───────────┼─────────┤
│ AMPnet APX Token      │ AAPX          │ Wrapped Ether     │ WETH          │ 98.7M     │ 22957   │
├───────────────────────┼───────────────┼───────────────────┼───────────────┼───────────┼─────────┤
│ Wrapped Ether         │ WETH          │ RMPL              │ RMPL          │ 97.7M     │ 46404   │
├───────────────────────┼───────────────┼───────────────────┼───────────────┼───────────┼─────────┤
│ DSLA                  │ DSLA          │ Wrapped Ether     │ WETH          │ 97.5M     │ 37901   │
└───────────────────────┴───────────────┴───────────────────┴───────────────┴───────────┴─────────┘
```
