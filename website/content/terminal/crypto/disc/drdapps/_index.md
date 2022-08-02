```
usage: drdapps [-l N] [-s {Name,Category,Protocols,Daily Users,Daily Volume [$]}] [--descend] [-l] [--export {csv,json,xlsx}] [-h]
```

Shows top decentralized applications [Source: https://dappradar.com/]

Accepts --sort {Name,Category,Protocols,Daily Users,Daily Volume [$]} to sort by column

```
optional arguments:
  -l N, --limit N       display N records (default: 15)
  -s --sort {Name,Category,Protocols,Daily Users,Daily Volume [$]}
                        Sort by given column
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 06:52 (✨) /crypto/disc/ $ drdapps
                              Top Decentralized Applications
┌───────────────┬──────────────┬─────────────────────────┬─────────────┬──────────────────┐
│ Name          │ Category     │ Protocols               │ Daily Users │ Daily Volume [$] │
├───────────────┼──────────────┼─────────────────────────┼─────────────┼──────────────────┤
│ Splinterlands │ games        │ hive,wax                │ 305.1K      │ 8K               │
├───────────────┼──────────────┼─────────────────────────┼─────────────┼──────────────────┤
│ PancakeSwap   │ defi         │ binance-smart-chain     │ 289.3K      │ 223.7M           │
├───────────────┼──────────────┼─────────────────────────┼─────────────┼──────────────────┤
│ Alien Worlds  │ games        │ wax,binance-smart-chain │ 235.6K      │ 759.2K           │
├───────────────┼──────────────┼─────────────────────────┼─────────────┼──────────────────┤
│ Farmers World │ games        │ wax                     │ 111.7K      │ 2.3K             │
├───────────────┼──────────────┼─────────────────────────┼─────────────┼──────────────────┤
│ AtomicAssets  │ other        │ wax,eos                 │ 108.9K      │ 226.3K           │
├───────────────┼──────────────┼─────────────────────────┼─────────────┼──────────────────┤
│ Axie Infinity │ games        │ ronin,ethereum          │ 90.9K       │ 11.6M            │
├───────────────┼──────────────┼─────────────────────────┼─────────────┼──────────────────┤
│ Upland        │ games        │ eos                     │ 63.3K       │ 0                │
├───────────────┼──────────────┼─────────────────────────┼─────────────┼──────────────────┤
│ OpenSea       │ marketplaces │ ethereum,polygon        │ 54K         │ 200M             │
├───────────────┼──────────────┼─────────────────────────┼─────────────┼──────────────────┤
│ Katana        │ defi         │ ronin                   │ 45.9K       │ 92.7M            │
├───────────────┼──────────────┼─────────────────────────┼─────────────┼──────────────────┤
│ Magic Eden    │ marketplaces │ solana                  │ 40.2K       │ 18.5M            │
└───────────────┴──────────────┴─────────────────────────┴─────────────┴──────────────────┘
```
