```
usage: ds [-p {uniswap-v3,uniswap-v2,sushiswap,curve}] [-h]
          [--export EXPORT] [--raw] [-l LIMIT]
```

Get daily transactions for certain symbols in ethereum blockchain
[Source: https://sdk.flipsidecrypto.xyz/shroomdk]

```
options:
  -p {uniswap-v3,uniswap-v2,sushiswap,curve}, --platform {uniswap-v3,uniswap-v2,sushiswap,curve}
                        Ethereum platform to check fees/number of
                        users over time (default: curve)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx and
                        figure into png, jpg, pdf, svg (default: )
  --raw                 Flag to display raw data (default: False)
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data.
                        (default: 10)
```