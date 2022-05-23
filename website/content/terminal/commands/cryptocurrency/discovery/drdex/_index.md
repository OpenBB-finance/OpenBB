```
usage: drdex [-l N] [-s {Name,Daily Users,Daily Volume [$]}] [--descend] [-l] [--export {csv,json,xlsx}] [-h]
```

Shows top decentralized exchanges [Source: https://dappradar.com/]

Accepts --sort {Name,Daily Users,Daily Volume [$]} to sort by column

```
optional arguments:
  -l N, --limit N       display N records (default: 15)
  -s --sort {Name,Daily Users,Daily Volume [$]}
                        Sort by given column
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 06:52 (✨) /crypto/disc/ $ drdex
           Top Decentralized Exchanges
┌───────────────┬─────────────┬──────────────────┐
│ Name          │ Daily Users │ Daily Volume [$] │
├───────────────┼─────────────┼──────────────────┤
│ Splinterlands │ 305.1K      │ 8K               │
├───────────────┼─────────────┼──────────────────┤
│ PancakeSwap   │ 289.3K      │ 223.7M           │
├───────────────┼─────────────┼──────────────────┤
│ Alien Worlds  │ 235.6K      │ 759.2K           │
├───────────────┼─────────────┼──────────────────┤
│ Farmers World │ 111.7K      │ 2.3K             │
├───────────────┼─────────────┼──────────────────┤
│ AtomicAssets  │ 108.9K      │ 226.3K           │
├───────────────┼─────────────┼──────────────────┤
│ Axie Infinity │ 90.9K       │ 11.6M            │
├───────────────┼─────────────┼──────────────────┤
│ Upland        │ 63.3K       │ 0                │
├───────────────┼─────────────┼──────────────────┤
│ OpenSea       │ 54K         │ 200M             │
├───────────────┼─────────────┼──────────────────┤
│ Katana        │ 45.9K       │ 92.7M            │
├───────────────┼─────────────┼──────────────────┤
│ Magic Eden    │ 40.2K       │ 18.5M            │
└───────────────┴─────────────┴──────────────────┘
```
