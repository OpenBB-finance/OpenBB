```
usage: pairs [-l LIMIT] [-v VOL] [-tx TX] [--days DAYS] [-s {created,pair,token0,token1,volumeUSD,txCount,totalSupply}] [--descend] [-h] [--export {csv,json,xlsx}]
```

Display Lastly added pairs on Uniswap DEX. [Source: https://thegraph.com/en/]

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        Number of records to display (default: 10)
  -v VOL, --vol VOL     Minimum trading volume (default: 100)
  -tx TX, --tx TX       Minimum number of transactions (default: 100)
  --days DAYS           Number of days the pair has been active, (default: 10)
  -s {created,pair,token0,token1,volumeUSD,txCount,totalSupply}, --sort {created,pair,token0,token1,volumeUSD,txCount,totalSupply}
                        Sort by given column. Default: created (default: created)
  --descend             Flag to sort in descending order (lowest first) (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 15, 06:27 (✨) /crypto/defi/ $ pairs
                                                   Latest Added Pairs on Uniswap DEX
┌─────────────────────┬────────────────┬──────────────────────────────────────┬────────────────────┬───────────┬─────────┬─────────────┐
│ created             │ pair           │ token0                               │ token1             │ volumeUSD │ txCount │ totalSupply │
├─────────────────────┼────────────────┼──────────────────────────────────────┼────────────────────┼───────────┼─────────┼─────────────┤
│ 2022-02-15 07:28:54 │ LIKI/WETH      │ Lion King                            │ Wrapped Ether      │ 1.3M      │ 327     │ 0           │
├─────────────────────┼────────────────┼──────────────────────────────────────┼────────────────────┼───────────┼─────────┼─────────────┤
│ 2022-02-15 05:26:25 │ X2Y2/WETH      │ X2Y2Token                            │ Wrapped Ether      │ 51.1M     │ 2550    │ 124K        │
├─────────────────────┼────────────────┼──────────────────────────────────────┼────────────────────┼───────────┼─────────┼─────────────┤
│ 2022-02-14 20:09:09 │ SIN/WETH       │ Sins                                 │ Wrapped Ether      │ 2.5M      │ 1334    │ 0           │
├─────────────────────┼────────────────┼──────────────────────────────────────┼────────────────────┼───────────┼─────────┼─────────────┤
│ 2022-02-14 19:41:24 │ YouTube/WETH   │ YouTube Metaverse                    │ Wrapped Ether      │ 637.5K    │ 105     │ 1.2M        │
├─────────────────────┼────────────────┼──────────────────────────────────────┼────────────────────┼───────────┼─────────┼─────────────┤
│ 2022-02-14 18:13:14 │ ALI/USDC       │ Artificial Liquid Intelligence Token │ USD//C             │ 4.3M      │ 490     │ 3           │
├─────────────────────┼────────────────┼──────────────────────────────────────┼────────────────────┼───────────┼─────────┼─────────────┤
│ 2022-02-14 16:49:02 │ SuperBowl/WETH │ SuperBowl Metaverse                  │ Wrapped Ether      │ 3.1M      │ 161     │ 1.3M        │
├─────────────────────┼────────────────┼──────────────────────────────────────┼────────────────────┼───────────┼─────────┼─────────────┤
│ 2022-02-14 13:31:57 │ LUSHI/WETH     │ LuckyShinu                           │ Wrapped Ether      │ 485.3K    │ 770     │ 1.3K        │
├─────────────────────┼────────────────┼──────────────────────────────────────┼────────────────────┼───────────┼─────────┼─────────────┤
│ 2022-02-14 13:22:44 │ Google/WETH    │ Google Metaverse                     │ Wrapped Ether      │ 3.4M      │ 189     │ 745.7K      │
├─────────────────────┼────────────────┼──────────────────────────────────────┼────────────────────┼───────────┼─────────┼─────────────┤
│ 2022-02-13 18:04:58 │ WETH/SKYWALKER │ Wrapped Ether                        │ Skywalker Protocol │ 888.2K    │ 104     │ 54          │
├─────────────────────┼────────────────┼──────────────────────────────────────┼────────────────────┼───────────┼─────────┼─────────────┤
│ 2022-02-13 17:56:36 │ McDonalds/WETH │ McDonalds Metaverse                  │ Wrapped Ether      │ 2.6M      │ 208     │ 1.9M        │
└─────────────────────┴────────────────┴──────────────────────────────────────┴────────────────────┴───────────┴─────────┴─────────────┘
```
