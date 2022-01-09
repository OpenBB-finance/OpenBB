```
usage: vaults [-c {ethereum,polygon,avalanche,bsc,terra,fantom,moonriver,celo,heco,okex,cronos,arbitrum,eth,harmony,fuse,defichain,solana,optimism}]
              [-p {aave,acryptos,alpaca,anchor,autofarm,balancer,bancor,beefy,belt,compound,convex,cream,curve,defichain,geist,lido,liquity,mirror,pancakeswap,raydium,sushi,tarot,traderjoe,tulip,ubeswap,uniswap,venus,yearn}] [-k {lp,single,noimploss,stable}]
              [-l LIMIT] [-s {name,chain,protocol,apy,tvl,risk}] [--descend] [-h] [--export {csv,json,xlsx}]
```

Display Top DeFi Vaults. [Source: https://coindix.com/]

```
optional arguments:
  -c {ethereum,polygon,avalanche,bsc,terra,fantom,moonriver,celo,heco,okex,cronos,arbitrum,eth,harmony,fuse,defichain,solana,optimism}, --chain {ethereum,polygon,avalanche,bsc,terra,fantom,moonriver,celo,heco,okex,cronos,arbitrum,eth,harmony,fuse,defichain,solana,optim
ism}
                        Blockchain name e.g. ethereum, terra (default: None)
  -p {aave,acryptos,alpaca,anchor,autofarm,balancer,bancor,beefy,belt,compound,convex,cream,curve,defichain,geist,lido,liquity,mirror,pancakeswap,raydium,sushi,tarot,traderjoe,tulip,ubeswap,uniswap,venus,yearn}, --protocol {aave,acryptos,alpaca,anchor,autofarm,balancer
,bancor,beefy,belt,compound,convex,cream,curve,defichain,geist,lido,liquity,mirror,pancakeswap,raydium,sushi,tarot,traderjoe,tulip,ubeswap,uniswap,venus,yearn}
                        DeFi protocol name e.g. aave, uniswap (default: None)
  -k {lp,single,noimploss,stable}, --kind {lp,single,noimploss,stable}
                        Kind/type of vault e.g. lp, single, noimploss, stable (default: None)
  -l LIMIT, --limit LIMIT
                        Number of records to display (default: 10)
  -s {name,chain,protocol,apy,tvl,risk}, --sort {name,chain,protocol,apy,tvl,risk}
                        Sort by given column. Default: timestamp (default: apy)
  --descend             Flag to sort in descending order (lowest first) (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```