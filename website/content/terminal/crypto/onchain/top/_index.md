```
usage: top [-l N]
           [-s {rank,name,symbol,price,txsCount,transfersCount,holdersCount,address}]
           [--descend] [--export {csv,json,xlsx}] [-h]
```

Display top ERC20 tokens. [Source: Ethplorer]

```
optional arguments:
  -l N, --limit N     display N number records (default: 10)
  -s {rank,name,symbol,price,txsCount,transfersCount,holdersCount,address}, --sort {rank,name,symbol,price,txsCount,transfersCount,holdersCount,address}
                        Sort by given column. Default: rank (default: rank)
  --descend             Flag to sort in descending order (lowest first)
                        (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default:
                        )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 08:04 (✨) /crypto/onchain/ $ top
                                                   Top ERC20 Tokens
┌──────┬───────────────┬────────┬─────────┬──────────┬────────────────┬──────────────┬────────────────┬───────────────┐
│ rank │ name          │ symbol │ price   │ txsCount │ transfersCount │ holdersCount │ twitter        │ coingecko     │
├──────┼───────────────┼────────┼─────────┼──────────┼────────────────┼──────────────┼────────────────┼───────────────┤
│ 1    │ WETH          │ WETH   │ 3099.54 │ 6M       │ 90M            │ 440.2K       │                │ weth          │
├──────┼───────────────┼────────┼─────────┼──────────┼────────────────┼──────────────┼────────────────┼───────────────┤
│ 2    │ Tether USD    │ USDT   │ 1.00    │ 125.5M   │ 138.8M         │ 4.4M         │ Tether_to      │ tether        │
├──────┼───────────────┼────────┼─────────┼──────────┼────────────────┼──────────────┼────────────────┼───────────────┤
│ 3    │ USD Coin      │ USDC   │ 1.00    │ 19M      │ 34.8M          │ 1.4M         │                │ usd-coin      │
├──────┼───────────────┼────────┼─────────┼──────────┼────────────────┼──────────────┼────────────────┼───────────────┤
│ 4    │ Strong        │ STRONG │ 393.38  │ 464.9K   │ 4.7M           │ 31.5K        │ Strongblock_io │ strong        │
├──────┼───────────────┼────────┼─────────┼──────────┼────────────────┼──────────────┼────────────────┼───────────────┤
│ 5    │ LooksRare     │ LOOKS  │ 2.14    │ 263.9K   │ 1.2M           │ 19.6K        │ LooksRareNFT   │ looksrare     │
├──────┼───────────────┼────────┼─────────┼──────────┼────────────────┼──────────────┼────────────────┼───────────────┤
│ 6    │ Dai           │ DAI    │ 1.00    │ 4.1M     │ 13.1M          │ 453.7K       │ MakerDAO       │ dai           │
├──────┼───────────────┼────────┼─────────┼──────────┼────────────────┼──────────────┼────────────────┼───────────────┤
│ 7    │ Shiba Inu     │ SHIB   │ 0.00    │ 4.6M     │ 6.8M           │ 1.2M         │ Shibtoken      │ shiba-inu     │
├──────┼───────────────┼────────┼─────────┼──────────┼────────────────┼──────────────┼────────────────┼───────────────┤
│ 8    │ Matic Network │ MATIC  │ 1.79    │ 2.8M     │ 3.5M           │ 367.6K       │ maticnetwork   │ matic-network │
├──────┼───────────────┼────────┼─────────┼──────────┼────────────────┼──────────────┼────────────────┼───────────────┤
│ 9    │ Chainlink     │ LINK   │ 16.81   │ 5.5M     │ 10.9M          │ 651.2K       │ chainlink      │ chainlink     │
├──────┼───────────────┼────────┼─────────┼──────────┼────────────────┼──────────────┼────────────────┼───────────────┤
│ 10   │ Gala          │ GALA   │ 0.34    │ 678.5K   │ 869.8K         │ 105.5K       │ GoGalaGames    │ gala          │
└──────┴───────────────┴────────┴─────────┴──────────┴────────────────┴──────────────┴────────────────┴───────────────┘
```
