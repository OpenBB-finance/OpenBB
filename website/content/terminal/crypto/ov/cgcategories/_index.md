```
usage: cgcategories [-l N] [-s {Rank,Name,Change_1h,Change_24h,Change_7d,Market_Cap,Volume_24h,Coins}] [--descend] [-l] [--export {csv,json,xlsx}] [--pie] [-h]

```

Shows top cryptocurrency categories by market capitalization. It includes categories like: stablecoins, defi, solana ecosystem, polkadot ecosystem and many others. You can sort by each column using --sort parameter

```
optional arguments:
  -l N, --limit N     display N number records (default: 15)
  -s {Rank,Name,Change_1h,Change_24h,Change_7d,Market_Cap,Volume_24h,Coins}, --sort {Rank,Name,Change_1h,Change_24h,Change_7d,Market_Cap,Volume_24h,Coins}
                        Sort by given column. Default: Rank (default: Rank)
  --pie               Show pie chart with market cap distribution
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 08:10 (✨) /crypto/ov/ $ cgcategories
┌──────────────────────────────────┬────────────┬───────────────────────┬───────────────────────────────────────────────────────┬────────────┐
│ Name                             │ Market Cap │ Market Cap Change 24H │ Top 3 Coins                                           │ Volume 24H │
├──────────────────────────────────┼────────────┼───────────────────────┼───────────────────────────────────────────────────────┼────────────┤
│ Smart Contract Platform          │ 678.047 B  │ 8.095                 │ ethereum,binance-coin-logo,cardano                    │ 27.408 B   │
├──────────────────────────────────┼────────────┼───────────────────────┼───────────────────────────────────────────────────────┼────────────┤
│ Binance Smart Chain Ecosystem    │ 339.679 B  │ 3.876                 │ Tether-logo,binance-coin-logo,USD_Coin_icon           │ 58.906 B   │
├──────────────────────────────────┼────────────┼───────────────────────┼───────────────────────────────────────────────────────┼────────────┤
│ Polygon Ecosystem                │ 311.497 B  │ 3.644                 │ Tether-logo,binance-coin-logo,USD_Coin_icon           │ 58.872 B   │
├──────────────────────────────────┼────────────┼───────────────────────┼───────────────────────────────────────────────────────┼────────────┤
│ Avalanche Ecosystem              │ 299.726 B  │ 3.620                 │ Tether-logo,binance-coin-logo,USD_Coin_icon           │ 53.420 B   │
├──────────────────────────────────┼────────────┼───────────────────────┼───────────────────────────────────────────────────────┼────────────┤
│ Moonriver Ecosystem              │ 288.048 B  │ 3.709                 │ Tether-logo,binance-coin-logo,USD_Coin_icon           │ 55.035 B   │
├──────────────────────────────────┼────────────┼───────────────────────┼───────────────────────────────────────────────────────┼────────────┤
│ Fantom Ecosystem                 │ 215.497 B  │ 1.760                 │ Tether-logo,USD_Coin_icon,luna1557227471663           │ 53.904 B   │
├──────────────────────────────────┼────────────┼───────────────────────┼───────────────────────────────────────────────────────┼────────────┤
│ Stablecoins                      │ 182.561 B  │ -0.108                │ Tether-logo,USD_Coin_icon,BUSD                        │ 50.694 B   │
├──────────────────────────────────┼────────────┼───────────────────────┼───────────────────────────────────────────────────────┼────────────┤
│ Arbitrum Ecosystem               │ 180.827 B  │ 1.536                 │ Tether-logo,USD_Coin_icon,wrapped_bitcoin_wbtc        │ 49.169 B   │
├──────────────────────────────────┼────────────┼───────────────────────┼───────────────────────────────────────────────────────┼────────────┤
│ Near Protocol Ecosystem          │ 173.873 B  │ 1.585                 │ Tether-logo,USD_Coin_icon,4943                        │ 49.034 B   │
├──────────────────────────────────┼────────────┼───────────────────────┼───────────────────────────────────────────────────────┼────────────┤
│ Exchange-based Tokens            │ 129.556 B  │ 7.082                 │ binance-coin-logo,cypto,F                             │ 6.532 B    │
├──────────────────────────────────┼────────────┼───────────────────────┼───────────────────────────────────────────────────────┼────────────┤
│ Decentralized Finance (DeFi)     │ 115.516 B  │ 6.310                 │ luna1557227471663,4943,chainlink-new-logo             │ 5.141 B    │
├──────────────────────────────────┼────────────┼───────────────────────┼───────────────────────────────────────────────────────┼────────────┤
│ Centralized Exchange Token (CEX) │ 109.267 B  │ 6.734                 │ binance-coin-logo,cypto,F                             │ 2.138 B    │
├──────────────────────────────────┼────────────┼───────────────────────┼───────────────────────────────────────────────────────┼────────────┤
│ Gnosis Chain Ecosystem           │ 86.569 B   │ 3.015                 │ USD_Coin_icon,wrapped_bitcoin_wbtc,chainlink-new-logo │ 5.255 B    │
├──────────────────────────────────┼────────────┼───────────────────────┼───────────────────────────────────────────────────────┼────────────┤
│ Cosmos Ecosystem                 │ 56.514 B   │ 7.509                 │ luna1557227471663,cypto,cosmos_hub                    │ 2.653 B    │
├──────────────────────────────────┼────────────┼───────────────────────┼───────────────────────────────────────────────────────┼────────────┤
│ Solana Ecosystem                 │ 51.051 B   │ 8.194                 │ solana,chainlink-new-logo,Graph_Token                 │ 2.925 B    │
└──────────────────────────────────┴────────────┴───────────────────────┴───────────────────────────────────────────────────────┴────────────┘
```
