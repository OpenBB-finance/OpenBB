---
title: ttcp
description: OpenBB Terminal Function
---

# ttcp

Display most traded crypto pairs on given decentralized exchange in chosen time period. [Source: https://graphql.bitquery.io/]

### Usage

```python
ttcp [-l LIMIT] [-e {1inch,AfroDex,AirSwap,Amplbitcratic,Balancer,BestSwap,Bitox,CellSwap,Cellswap,Cofix,Coinchangex,Curve,DDEX,DUBIex,DecentrEx,DeversiFi,Dodo,ETHERCExchange,EtherBlockchain,EtherDelta,Ethernext,Ethfinex,FEGex,FFFSwap,Fordex,GUDecks,GUDeks,HiSwap,IDEX,LedgerDex,Matcha,Miniswap,Mooniswap,Oasis,OpenRelay,S.Finance,SakeSwap,SeedDex,SingularX,StarBitEx,SushiSwap,SwapX,SwitchDex,TacoSwap,TokenJar,TokenStore,TokenTrove,Tokenlon,TradexOne,Uniswap,ZeusSwap,dYdX,dex.blue}] [-d DAYS] [-s {base,quoted,trades,tradeAmount}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | display N number records | 10 | True | None |
| exchange | Decentralized exchange name. | None | True | 1inch, AfroDex, AirSwap, Amplbitcratic, Balancer, BestSwap, Bitox, CellSwap, Cellswap, Cofix, Coinchangex, Curve, DDEX, DUBIex, DecentrEx, DeversiFi, Dodo, ETHERCExchange, EtherBlockchain, EtherDelta, Ethernext, Ethfinex, FEGex, FFFSwap, Fordex, GUDecks, GUDeks, HiSwap, IDEX, LedgerDex, Matcha, Miniswap, Mooniswap, Oasis, OpenRelay, S.Finance, SakeSwap, SeedDex, SingularX, StarBitEx, SushiSwap, SwapX, SwitchDex, TacoSwap, TokenJar, TokenStore, TokenTrove, Tokenlon, TradexOne, Uniswap, ZeusSwap, dYdX, dex.blue |
| days | Number of days to display data for. | 30 | True | range(1, 100) |
| sortby | Sort by given column. | tradeAmount | True | base, quoted, trades, tradeAmount |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |

---
