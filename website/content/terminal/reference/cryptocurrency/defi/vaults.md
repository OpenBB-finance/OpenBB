---
title: vaults
description: OpenBB Terminal Function
---

# vaults

Display Top DeFi Vaults. [Source: https://coindix.com/]

### Usage

```python
usage: vaults
              [-c {ethereum,polygon,avalanche,bsc,terra,fantom,moonriver,celo,heco,okex,cronos,arbitrum,eth,harmony,fuse,defichain,solana,optimism,kusama,metis,osmosis}]
              [-p {aave,acryptos,alpaca,anchor,autofarm,balancer,bancor,beefy,belt,compound,convex,cream,curve,defichain,geist,lido,liquity,mirror,pancakeswap,raydium,sushi,tarot,traderjoe,tulip,ubeswap,uniswap,venus,yearn,osmosis,tulip}]
              [-k {lp,single,noimploss,stable}] [-t TOP] [-s {name,chain,protocol,apy,tvl,link}] [-r] [-l]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| chain | Blockchain name e.g. ethereum, terra | None | True | ethereum, polygon, avalanche, bsc, terra, fantom, moonriver, celo, heco, okex, cronos, arbitrum, eth, harmony, fuse, defichain, solana, optimism, kusama, metis, osmosis |
| protocol | DeFi protocol name e.g. aave, uniswap | None | True | aave, acryptos, alpaca, anchor, autofarm, balancer, bancor, beefy, belt, compound, convex, cream, curve, defichain, geist, lido, liquity, mirror, pancakeswap, raydium, sushi, tarot, traderjoe, tulip, ubeswap, uniswap, venus, yearn, osmosis, tulip |
| kind | Kind/type of vault e.g. lp, single, noimploss, stable | None | True | lp, single, noimploss, stable |
| limit | Number of records to display | 10 | True | range(1, 1000) |
| sortby | Sort by given column. Default: timestamp | apy | True | name, chain, protocol, apy, tvl, link |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
| link | Flag to show vault link | True | True | None |
---

