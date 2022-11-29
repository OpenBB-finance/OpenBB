---
title: funot
description: OpenBB Terminal Function
---

# funot

Display fundamental metric over time [Source: Token Terminal]

### Usage

```python
funot [-m {twitter_followers,gmv_annualized,market_cap,take_rate,revenue,revenue_protocol,tvl,pe,pe_circulating,ps,ps_circulating}] -p {0x,1inch,88mph,aave,abracadabra-money,alchemist,alchemix-finance,algorand,alpha-finance,arweave,autofarm,avalanche,axie-infinity,balancer,bancor,barnbridge,basket-dao,benqi,binance-smart-chain,bitcoin,cap,cardano,centrifuge,clipper,compound,convex-finance,cosmos,cryptex,curve,decentral-games,decred,dforce,dhedge,dodo,dogecoin,dydx,ellipsis-finance,elrond,enzyme-finance,erasure-protocol,ethereum,ethereum-name-service,euler,fantom,fei-protocol,filecoin,futureswap,gmx,goldfinch,harvest-finance,helium,hurricaneswap,idle-finance,index-cooperative,instadapp,integral-protocol,karura,keeperdao,keep-network,kusama,kyber,lido-finance,liquity,litecoin,livepeer,looksrare,loopring,maiar,makerdao,maple-finance,mcdex,metamask,mstable,near-protocol,nexus-mutual,nftx,notional-finance,opensea,optimism,osmosis,pancakeswap,pangolin,perpetual-protocol,piedao,pocket-network,polkadot,polygon,polymarket,pooltogether,powerpool,quickswap,rarible,rari-capital,reflexer,ren,ribbon-finance,rocket-pool,saddle-finance,set-protocol,solana,solend,spookyswap,stake-dao,stellar,sushiswap,synthetix,terra,tezos,the-graph,thorchain,tokemak,tokenlon,tornado-cash,trader-joe,uma,uniswap,unit-protocol,venus,vesper-finance,volmex,wakaswap,yearn-finance,yield-guild-games,yield-yak,zcash,zora}
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| metric | Choose metric of interest |  | True | twitter_followers, gmv_annualized, market_cap, take_rate, revenue, revenue_protocol, tvl, pe, pe_circulating, ps, ps_circulating |
| project | Choose project of interest | None | False | 0x, 1inch, 88mph, aave, abracadabra-money, alchemist, alchemix-finance, algorand, alpha-finance, arweave, autofarm, avalanche, axie-infinity, balancer, bancor, barnbridge, basket-dao, benqi, binance-smart-chain, bitcoin, cap, cardano, centrifuge, clipper, compound, convex-finance, cosmos, cryptex, curve, decentral-games, decred, dforce, dhedge, dodo, dogecoin, dydx, ellipsis-finance, elrond, enzyme-finance, erasure-protocol, ethereum, ethereum-name-service, euler, fantom, fei-protocol, filecoin, futureswap, gmx, goldfinch, harvest-finance, helium, hurricaneswap, idle-finance, index-cooperative, instadapp, integral-protocol, karura, keeperdao, keep-network, kusama, kyber, lido-finance, liquity, litecoin, livepeer, looksrare, loopring, maiar, makerdao, maple-finance, mcdex, metamask, mstable, near-protocol, nexus-mutual, nftx, notional-finance, opensea, optimism, osmosis, pancakeswap, pangolin, perpetual-protocol, piedao, pocket-network, polkadot, polygon, polymarket, pooltogether, powerpool, quickswap, rarible, rari-capital, reflexer, ren, ribbon-finance, rocket-pool, saddle-finance, set-protocol, solana, solend, spookyswap, stake-dao, stellar, sushiswap, synthetix, terra, tezos, the-graph, thorchain, tokemak, tokenlon, tornado-cash, trader-joe, uma, uniswap, unit-protocol, venus, vesper-finance, volmex, wakaswap, yearn-finance, yield-guild-games, yield-yak, zcash, zora |


---

## Examples

```python
2022 Aug 28, 19:08 (🦋) /crypto/dd/ $ funot -m revenue -p solana
```
---
