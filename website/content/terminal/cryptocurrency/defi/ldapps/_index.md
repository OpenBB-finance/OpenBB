```
usage: ldapps [-l LIMIT] [-s {tvl,symbol,category,chains,change_1h,change_1d,change_7d,name}] [--descend] [--desc] [-h] [--export {csv,json,xlsx}]
```

Display information about listed DeFi Protocols on DeFi Llama. [Source:https://docs.llama.fi/api]

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        Number of records to display (default: 10)
  -s {tvl,symbol,category,chains,change_1h,change_1d,change_7d,name}, --sort {tvl,symbol,category,chains,change_1h,change_1d,change_7d,name}
                        Sort by given column. Default: tvl (default: tvl)
  --descend             Flag to sort in descending order (lowest first) (default: False)
  --desc                Flag to display description of protocol (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 15, 06:24 (✨) /crypto/defi/ $ ldapps
┌──────────────────────────┬────────┬──────────┬──────────────────────────────────────────────────┬───────────────┬───────────────┬───────────────┬──────────┐
│ Name                     │ Symbol │ Category │ Chains                                           │ Change 1H (%) │ Change 1D (%) │ Change 7D (%) │ TVL ($)  │
├──────────────────────────┼────────┼──────────┼──────────────────────────────────────────────────┼───────────────┼───────────────┼───────────────┼──────────┤
│ Curve                    │ CRV    │ Dexes    │ Ethereum, Avalanche, Fantom, Polygon, Arbitrum,  │ 0.00          │ 1.26          │ 1.24          │ 19.752 B │
│                          │        │          │ xDai, Harmony, Optimism                          │               │               │               │          │
├──────────────────────────┼────────┼──────────┼──────────────────────────────────────────────────┼───────────────┼───────────────┼───────────────┼──────────┤
│ MakerDAO                 │ MKR    │ CDP      │ Ethereum                                         │ 0.00          │ 4.68          │ -0.35         │ 17.551 B │
├──────────────────────────┼────────┼──────────┼──────────────────────────────────────────────────┼───────────────┼───────────────┼───────────────┼──────────┤
│ Convex Finance           │ CVX    │ Yield    │ Ethereum                                         │ -0.00         │ 1.98          │ 0.40          │ 13.657 B │
├──────────────────────────┼────────┼──────────┼──────────────────────────────────────────────────┼───────────────┼───────────────┼───────────────┼──────────┤
│ AAVE                     │ AAVE   │ Lending  │ Ethereum, Avalanche, Polygon                     │ 0.00          │ 3.06          │ -0.02         │ 13.597 B │
├──────────────────────────┼────────┼──────────┼──────────────────────────────────────────────────┼───────────────┼───────────────┼───────────────┼──────────┤
│ WBTC                     │ WBTC   │ Bridge   │ Ethereum                                         │ 0.13          │ 5.03          │ 1.06          │ 11.633 B │
├──────────────────────────┼────────┼──────────┼──────────────────────────────────────────────────┼───────────────┼───────────────┼───────────────┼──────────┤
│ Polygon Bridge & Staking │ MATIC  │ Chain    │ Polygon                                          │ 0.00          │ -1.84         │ 1.42          │ 10.344 B │
├──────────────────────────┼────────┼──────────┼──────────────────────────────────────────────────┼───────────────┼───────────────┼───────────────┼──────────┤
│ Lido                     │ LDO    │ Staking  │ Ethereum, Terra, Solana                          │ 0.00          │ 8.70          │ 0.42          │ 9.626 B  │
├──────────────────────────┼────────┼──────────┼──────────────────────────────────────────────────┼───────────────┼───────────────┼───────────────┼──────────┤
│ Anchor                   │ ANC    │ Lending  │ Terra                                            │ -0.00         │ 5.25          │ 5.51          │ 8.401 B  │
├──────────────────────────┼────────┼──────────┼──────────────────────────────────────────────────┼───────────────┼───────────────┼───────────────┼──────────┤
│ Uniswap                  │ UNI    │ Dexes    │ Ethereum, Polygon, Arbitrum, Optimism            │ 0.78          │ 5.38          │ 0.13          │ 7.652 B  │
├──────────────────────────┼────────┼──────────┼──────────────────────────────────────────────────┼───────────────┼───────────────┼───────────────┼──────────┤
│ Multichain               │ MULTI  │ Bridge   │ Fantom, Avalanche, Ethereum, Binance, Moonriver, │ 0.00          │ 3.05          │ -5.37         │ 7.305 B  │
│                          │        │          │ Arbitrum, Harmony, OKExChain, Polygon, Telos,    │               │               │               │          │
│                          │        │          │ Heco, xDai, Kucoin, Syscoin                      │               │               │               │          │
└──────────────────────────┴────────┴──────────┴──────────────────────────────────────────────────┴───────────────┴───────────────┴───────────────┴──────────┘
```
