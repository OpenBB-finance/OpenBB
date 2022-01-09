```
usage: vaults [-c {ethereum,polygon,avalanche,bsc,terra,fantom,moonriver,celo,heco,okex,cronos,arbitrum,eth,harmony,fuse,defichain,solana,optimism}]
              [-p {aave,acryptos,alpaca,anchor,autofarm,balancer,bancor,beefy,belt,compound,convex,cream,curve,defichain,geist,lido,liquity,mirror,pancakeswap,raydium,sushi,tarot,traderjoe,tulip,ubeswap,uniswap,ven
us,yearn}]
              [-k {lp,single,noimploss,stable}] [-t LIMIT] [-s {name,chain,protocol,apy,tvl,risk,link}] [--descend] [-l] [-h] [--export {csv,json,xlsx}]
```

Display Top DeFi Vaults. [Source: https://coindix.com/]

```
optional arguments:
  -c {ethereum,polygon,avalanche,bsc,terra,fantom,moonriver,celo,heco,okex,cronos,arbitrum,eth,harmony,fuse,defichain,solana,optimism}, --chain {ethereum,polygon,avalanche,bsc,terra,fantom,moonriver,celo,heco,okex,
cronos,arbitrum,eth,harmony,fuse,defichain,solana,optimism}
                        Blockchain name e.g. ethereum, terra (default: None)
  -p {aave,acryptos,alpaca,anchor,autofarm,balancer,bancor,beefy,belt,compound,convex,cream,curve,defichain,geist,lido,liquity,mirror,pancakeswap,raydium,sushi,tarot,traderjoe,tulip,ubeswap,uniswap,venus,yearn}, --
protocol {aave,acryptos,alpaca,anchor,autofarm,balancer,bancor,beefy,belt,compound,convex,cream,curve,defichain,geist,lido,liquity,mirror,pancakeswap,raydium,sushi,tarot,traderjoe,tulip,ubeswap,uniswap,venus,yearn}
                        DeFi protocol name e.g. aave, uniswap (default: None)
  -k {lp,single,noimploss,stable}, --kind {lp,single,noimploss,stable}
                        Kind/type of vault e.g. lp, single, noimploss, stable (default: None)
  -t LIMIT, --top LIMIT
                        Number of records to display (default: 10)
  -s {name,chain,protocol,apy,tvl,risk,link}, --sort {name,chain,protocol,apy,tvl,risk,link}
                        Sort by given column. Default: timestamp (default: apy)
  --descend             Flag to sort in descending order (lowest first) (default: False)
  -l, --links           Flag to show vault link (default: True)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )

```