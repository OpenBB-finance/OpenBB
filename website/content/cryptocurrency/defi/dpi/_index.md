```
usage: dpi [-l LIMIT] [-s {Rank,Name,Chain,Category,TVL,Change_1D}] [--descend] [-h] [--export {csv,json,xlsx}]
```

Displays DeFi Pulse crypto protocols. [Source: https://defipulse.com/]

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        Number of records to display (default: 15)
  -s {Rank,Name,Chain,Category,TVL,Change_1D}, --sort {Rank,Name,Chain,Category,TVL,Change_1D}
                        Sort by given column. Default: Rank (default: Rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 15, 06:06 (✨) /crypto/defi/ $ dpi
                       DeFi Pulse Crypto Protocols
┌──────┬────────────────┬────────────┬─────────────┬─────────┬───────────┐
│ Rank │ Name           │ Chain      │ Sector      │ TVL     │ 1 Day (%) │
├──────┼────────────────┼────────────┼─────────────┼─────────┼───────────┤
│ 0    │ Maker          │ Ethereum   │ Lending     │ $17.29B │ 2.82%     │
├──────┼────────────────┼────────────┼─────────────┼─────────┼───────────┤
│ 1    │ Curve Finance  │ Ethereum   │ DEXes       │ $11.40B │ -1.05%    │
├──────┼────────────────┼────────────┼─────────────┼─────────┼───────────┤
│ 2    │ Aave           │ Multichain │ Lending     │ $10.73B │ -1.51%    │
├──────┼────────────────┼────────────┼─────────────┼─────────┼───────────┤
│ 3    │ Convex Finance │ Ethereum   │ Assets      │ $10.34B │ 2.07%     │
├──────┼────────────────┼────────────┼─────────────┼─────────┼───────────┤
│ 4    │ Compound       │ Ethereum   │ Lending     │ $7.17B  │ 3.39%     │
├──────┼────────────────┼────────────┼─────────────┼─────────┼───────────┤
│ 5    │ InstaDApp      │ Ethereum   │ Lending     │ $5.75B  │ 1.62%     │
├──────┼────────────────┼────────────┼─────────────┼─────────┼───────────┤
│ 6    │ yearn.finance  │ Ethereum   │ Assets      │ $3.15B  │ 1.27%     │
├──────┼────────────────┼────────────┼─────────────┼─────────┼───────────┤
│ 7    │ Uniswap        │ ethereum   │ DEXes       │ $2.28B  │ 50.80%    │
├──────┼────────────────┼────────────┼─────────────┼─────────┼───────────┤
│ 8    │ Balancer       │ Ethereum   │ DEXes       │ $2.19B  │ -1.68%    │
├──────┼────────────────┼────────────┼─────────────┼─────────┼───────────┤
│ 9    │ Bancor         │ Ethereum   │ DEXes       │ $1.84B  │ -0.05%    │
├──────┼────────────────┼────────────┼─────────────┼─────────┼───────────┤
│ 10   │ SushiSwap      │ Ethereum   │ DEXes       │ $1.83B  │ 4.16%     │
├──────┼────────────────┼────────────┼─────────────┼─────────┼───────────┤
│ 11   │ Liquity        │ Ethereum   │ Lending     │ $1.49B  │ 4.37%     │
├──────┼────────────────┼────────────┼─────────────┼─────────┼───────────┤
│ 12   │ dYdX           │ Ethereum   │ Derivatives │ $986.7M │ -0.36%    │
├──────┼────────────────┼────────────┼─────────────┼─────────┼───────────┤
│ 13   │ Rari Capital   │ Ethereum   │ Assets      │ $935.3M │ 3.25%     │
├──────┼────────────────┼────────────┼─────────────┼─────────┼───────────┤
│ 14   │ Flexa          │ Ethereum   │ Payments    │ $842.1M │ 0.36%     │
└──────┴────────────────┴────────────┴─────────────┴─────────┴───────────┘
```
