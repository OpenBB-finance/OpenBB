```
usage: vaults [-c {ethereum,polygon,avalanche,bsc,terra,fantom,moonriver,celo,heco,okex,cronos,arbitrum,eth,harmony,fuse,defichain,solana,optimism}]
              [-p {aave,acryptos,alpaca,anchor,autofarm,balancer,bancor,beefy,belt,compound,convex,cream,curve,defichain,geist,lido,liquity,mirror,pancakeswap,raydium,sushi,tarot,traderjoe,tulip,ubeswap,uniswap,venus,yearn}]
              [-k {lp,single,noimploss,stable}] [-t LIMIT] [-s {name,chain,protocol,apy,tvl,risk,link}] [--descend] [-l] [-h] [--export {csv,json,xlsx}]
```

Display Top DeFi Vaults. [Source: https://coindix.com/]

```
optional arguments:
  -c {ethereum,polygon,avalanche,bsc,terra,fantom,moonriver,celo,heco,okex,cronos,arbitrum,eth,harmony,fuse,defichain,solana,optimism}, --chain {ethereum,polygon,avalanche,bsc,terra,fantom,moonriver,celo,heco,okex,cronos,arbitrum,eth,harmony,fuse,defichain,solana,optimism}
                        Blockchain name e.g. ethereum, terra (default: None)
  -p {aave,acryptos,alpaca,anchor,autofarm,balancer,bancor,beefy,belt,compound,convex,cream,curve,defichain,geist,lido,liquity,mirror,pancakeswap,raydium,sushi,tarot,traderjoe,tulip,ubeswap,uniswap,venus,yearn}, --protocol {aave,acryptos,alpaca,anchor,autofarm,balancer,bancor,beefy,belt,compound,convex,cream,curve,defichain,geist,lido,liquity,mirror,pancakeswap,raydium,sushi,tarot,traderjoe,tulip,ubeswap,uniswap,venus,yearn}
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

Example:
```
2022 Feb 15, 06:37 (✨) /crypto/defi/ $ vaults
                                   Top DeFi Vaults
┌──────────────┬───────────┬──────────┬────────────────────┬──────────┬──────────────┐
│ Name         │ Chain     │ Protocol │ APY (%)            │ TVL ($)  │ Risk         │
├──────────────┼───────────┼──────────┼────────────────────┼──────────┼──────────────┤
│ PAE-FTM      │ Fantom    │ Beefy    │ 1155258727603.13 % │ 1.091 M  │ Low          │
├──────────────┼───────────┼──────────┼────────────────────┼──────────┼──────────────┤
│ pFTM-FTM     │ Fantom    │ Beefy    │ 14226994274.36 %   │ 2.023 M  │ Low          │
├──────────────┼───────────┼──────────┼────────────────────┼──────────┼──────────────┤
│ 2OMB-2SHARES │ Fantom    │ Beefy    │ 333473840.53 %     │ 1.027 M  │ Low          │
├──────────────┼───────────┼──────────┼────────────────────┼──────────┼──────────────┤
│ 2SHARES-FTM  │ Fantom    │ Beefy    │ 29069185.59 %      │ 7.788 M  │ Low          │
├──────────────┼───────────┼──────────┼────────────────────┼──────────┼──────────────┤
│ 2OMB-FTM     │ Fantom    │ Beefy    │ 8150077.64 %       │ 10.576 M │ Low          │
├──────────────┼───────────┼──────────┼────────────────────┼──────────┼──────────────┤
│ DIBS-BNB     │ BSC       │ Beefy    │ 50031.69 %         │ 1.097 M  │ Low          │
├──────────────┼───────────┼──────────┼────────────────────┼──────────┼──────────────┤
│ STATIC-BUSD  │ BSC       │ Beefy    │ 11663.57 %         │ 1.083 M  │ Low          │
├──────────────┼───────────┼──────────┼────────────────────┼──────────┼──────────────┤
│ CHARGE-BUSD  │ BSC       │ Beefy    │ 1289.33 %          │ 1.195 M  │ Low          │
├──────────────┼───────────┼──────────┼────────────────────┼──────────┼──────────────┤
│ AVAX-FIRE    │ Avalanche │ Pangolin │ 969.09 %           │ 3.829 M  │ Medium       │
├──────────────┼───────────┼──────────┼────────────────────┼──────────┼──────────────┤
│ PROTO-USDC   │ Fantom    │ ProtoFi  │ 824.41 %           │ 11.483 M │ Non Eligible │
└──────────────┴───────────┴──────────┴────────────────────┴──────────┴──────────────┘
```
