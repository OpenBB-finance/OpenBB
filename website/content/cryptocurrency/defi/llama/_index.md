```
usage: llama [-l N]
             [-s {tvl,symbol,category,chains,change_1h,change_1d,change_7d,tvl}]
             [--descend] [--desc] [--export {csv,json,xlsx}] [-h]
```

Display information about listed DeFi Protocols on DeFi Llama. [Source:https://docs.llama.fi/api]

```
optional arguments:
  -l N, --limit N       display N records (default: 10)
  -s {tvl,symbol,category,chains,change_1h,change_1d,change_7d,tvl}, --sort {tvl,symbol,category,chains,change_1h,change_1d,change_7d,tvl}
                        Sort by given column. Default: tvl (default: tvl)
  --descend             Flag to sort in descending order (lowest first)
                        (default: False)
  --desc                Flag to display description of protocol (default:
                        False)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default:
                        )
  -h, --help            show this help message (default: False)
```
