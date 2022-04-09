```
usage: cgplatforms [-l N] [-s {Rank,Name,Category,Centralized}] [--descend] [--export {csv,json,xlsx}] [-h]
```

Shows Top Crypto Financial Platforms in which you can borrow or lend your crypto. e.g Celsius, Nexo, Crypto.com, Aave and others. You can display
only N number of platforms with --limit parameter. You can sort data by Rank, Name, Category, Centralized with --sort and also with --descend flag
to sort descending. Displays: Rank, Name, Category, Centralized, Url

```
optional arguments:
  -l N, --limit N     display N number records (default: 15)
  -s {Rank,Name,Category,Centralized}, --sort {Rank,Name,Category,Centralized}
                        Sort by given column. Default: Rank (default: Rank)
  --descend             Flag to sort in descending order (lowest first) (default: True)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 08:15 (✨) /crypto/ov/ $ cgplatforms
                                     Financial Platforms
┌──────┬──────────────────┬───────────────┬─────────────┬────────────────────────────────────┐
│ Rank │ Name             │ Category      │ Centralized │ Url                                │
├──────┼──────────────────┼───────────────┼─────────────┼────────────────────────────────────┤
│ 1    │ Binance Staking  │ CeFi Platform │ True        │ https://www.binance.com/en/staking │
├──────┼──────────────────┼───────────────┼─────────────┼────────────────────────────────────┤
│ 2    │ Celsius Network  │ CeFi Platform │ True        │ https://celsius.network/           │
├──────┼──────────────────┼───────────────┼─────────────┼────────────────────────────────────┤
│ 3    │ Cobo             │ CeFi Platform │ True        │ https://cobo.com/                  │
├──────┼──────────────────┼───────────────┼─────────────┼────────────────────────────────────┤
│ 4    │ Dai Savings Rate │ DeFi Platform │ False       │ https://oasis.app/save             │
├──────┼──────────────────┼───────────────┼─────────────┼────────────────────────────────────┤
│ 5    │ dYdX             │ DeFi Platform │ False       │ https://dydx.exchange/             │
├──────┼──────────────────┼───────────────┼─────────────┼────────────────────────────────────┤
│ 6    │ Idle Finance     │ DeFi Platform │ False       │ https://idle.finance/#/            │
├──────┼──────────────────┼───────────────┼─────────────┼────────────────────────────────────┤
│ 7    │ Staked US        │ CeFi Platform │ True        │ https://staked.us/                 │
├──────┼──────────────────┼───────────────┼─────────────┼────────────────────────────────────┤
│ 8    │ Crypto.com       │ CeFi Platform │ True        │ https://crypto.com/en/             │
├──────┼──────────────────┼───────────────┼─────────────┼────────────────────────────────────┤
│ 9    │ Aave             │ DeFi Platform │ False       │ https://aave.com/                  │
├──────┼──────────────────┼───────────────┼─────────────┼────────────────────────────────────┤
│ 10   │ Nexo             │ CeFi Platform │ True        │ https://nexo.io/                   │
├──────┼──────────────────┼───────────────┼─────────────┼────────────────────────────────────┤
│ 11   │ Inlock           │ CeFi Platform │ True        │ https://inlock.io/                 │
├──────┼──────────────────┼───────────────┼─────────────┼────────────────────────────────────┤
│ 12   │ Bitfinex         │ CeFi Platform │ True        │ https://www.bitfinex.com           │
├──────┼──────────────────┼───────────────┼─────────────┼────────────────────────────────────┤
│ 13   │ Compound Finance │ DeFi Platform │ False       │ https://compound.finance/          │
├──────┼──────────────────┼───────────────┼─────────────┼────────────────────────────────────┤
│ 14   │ Fulcrum          │ DeFi Platform │ False       │ https://fulcrum.trade/lending      │
├──────┼──────────────────┼───────────────┼─────────────┼────────────────────────────────────┤
│ 15   │ Binance Savings  │ CeFi Platform │ True        │ https://www.binance.com/en/lending │
└──────┴──────────────────┴───────────────┴─────────────┴────────────────────────────────────┘
```
