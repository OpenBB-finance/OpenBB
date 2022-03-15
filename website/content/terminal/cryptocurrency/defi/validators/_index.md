```
usage: validators [-l LIMIT] [-s {validatorName,tokensAmount,votingPower,commissionRate,status,uptime}] [--descend] [-h] [--export {csv,json,xlsx}]
```

Displays information about terra validators. [Source: https://fcd.terra.dev/swagger]

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        Number of validators to show (default: 10)
  -s {validatorName,tokensAmount,votingPower,commissionRate,status,uptime}, --sort {validatorName,tokensAmount,votingPower,commissionRate,status,uptime}
                        Sort by given column. Default: votingPower (default: votingPower)
  --descend             Flag to sort in descending order (lowest first) (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 15, 06:36 (✨) /crypto/defi/ $ validators
┌──────────────────────────────────────────────┬─────────────────────┬───────────────┬────────────────┬───────────────────┬────────┬──────────┐
│ Account address                              │ Validator name      │ Tokens amount │ Voting power % │ Commission rate % │ Status │ Uptime % │
├──────────────────────────────────────────────┼─────────────────────┼───────────────┼────────────────┼───────────────────┼────────┼──────────┤
│ terra1259cmu5zyklsdkmgstxhwqpe0utfe5hhyygjdc │ Orion.Money         │ 21.9M         │ 7.20           │ 5.00              │ active │ 100.00   │
├──────────────────────────────────────────────┼─────────────────────┼───────────────┼────────────────┼───────────────────┼────────┼──────────┤
│ terra15zcjduavxc5mkp8qcqs9eyhwlqwdlrzy6anwpg │ B-Harvest           │ 17.9M         │ 5.88           │ 5.00              │ active │ 100.00   │
├──────────────────────────────────────────────┼─────────────────────┼───────────────┼────────────────┼───────────────────┼────────┼──────────┤
│ terra123gn6j23lmexu0qx5qhmgxgunmjcqsx8g5ueq2 │ Staking Fund        │ 15.7M         │ 5.17           │ 10.00             │ active │ 100.00   │
├──────────────────────────────────────────────┼─────────────────────┼───────────────┼────────────────┼───────────────────┼────────┼──────────┤
│ terra1v5hrqlv8dqgzvy0pwzqzg0gxy899rm4kdn0jp4 │ DokiaCapital        │ 10.3M         │ 3.38           │ 5.00              │ active │ 100.00   │
├──────────────────────────────────────────────┼─────────────────────┼───────────────┼────────────────┼───────────────────┼────────┼──────────┤
│ terra1kprce6kc08a6l03gzzh99hfpazfjeczfpd6td0 │ Certus One          │ 9M            │ 2.96           │ 10.00             │ active │ 100.00   │
├──────────────────────────────────────────────┼─────────────────────┼───────────────┼────────────────┼───────────────────┼────────┼──────────┤
│ terra1p54hc4yy2ajg67j645dn73w3378j6k05v52cnk │ hashed              │ 7.7M          │ 2.53           │ 10.00             │ active │ 100.00   │
├──────────────────────────────────────────────┼─────────────────────┼───────────────┼────────────────┼───────────────────┼────────┼──────────┤
│ terra1va2ew92dtkhffduswr83elf3nfvl4xg48rguwl │ NOD Games           │ 7.4M          │ 2.44           │ 0.00              │ active │ 99.99    │
├──────────────────────────────────────────────┼─────────────────────┼───────────────┼────────────────┼───────────────────┼────────┼──────────┤
│ terra175hhkyxmkp8hf2zrzka7cnn7lk6mudtv4nsp2x │ DSRV - CHAISCAN.com │ 6.7M          │ 2.22           │ 10.00             │ active │ 100.00   │
├──────────────────────────────────────────────┼─────────────────────┼───────────────┼────────────────┼───────────────────┼────────┼──────────┤
│ terra162892yn0tf8dxl8ghgneqykyr8ufrwmcs6vft5 │ Luna Maximalists    │ 6.5M          │ 2.14           │ 20.00             │ active │ 99.98    │
├──────────────────────────────────────────────┼─────────────────────┼───────────────┼────────────────┼───────────────────┼────────┼──────────┤
│ terra1h6rf7y2ar5vz64q8rchz5443s3tqnswrpxe69f │ Staked              │ 6.3M          │ 2.08           │ 10.00             │ active │ 100.00   │
└──────────────────────────────────────────────┴─────────────────────┴───────────────┴────────────────┴───────────────────┴────────┴──────────┘
```
