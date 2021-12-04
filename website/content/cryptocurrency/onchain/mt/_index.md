```
usage: mt [-t TOP]
          [-e {1inch,AfroDex,AirSwap,Amplbitcratic,Balancer,BestSwap,Bitox,CellSwap,Cellswap,Cofix,Coinchangex,Curve,DDEX,DUBIex,DecentrEx,DeversiFi,Dodo,ETHERCExchange,EtherBlockchain,EtherDelta,Ethernext,Ethfinex,FEGex,FFFSwap,Fordex,GUDecks,GUDeks,HiSwap,IDEX,Ledger
Dex,Matcha,Miniswap,Mooniswap,Oasis,OpenRelay,S.Finance,SakeSwap,SeedDex,SingularX,StarBitEx,SushiSwap,SwapX,SwitchDex,TacoSwap,TokenJar,TokenStore,TokenTrove,Tokenlon,TradexOne,Uniswap,ZeusSwap,dYdX,dex.blue}]
          [-d DAYS] [-s {base,quoted,trades,tradeAmount}] [--descend] [-h]
          [--export {csv,json,xlsx}]

```

Display most traded crypto pairs on given decentralized exchange in chosen
time period [Source: https://graphql.bitquery.io/]

```
optional arguments:
  -t TOP, --top TOP     top N number records (default: 10)
  -e {1inch,AfroDex,AirSwap,Amplbitcratic,Balancer,BestSwap,Bitox,CellSwap,Cellswap,Cofix,Coinchangex,Curve,DDEX,DUBIex,DecentrEx,DeversiFi,Dodo,ETHERCExchange,EtherBlockchain,EtherDelta,Ethernext,Ethfinex,FEGex,FFFSwap,Fordex,GUDecks,GUDeks,HiSwap,IDEX,LedgerDex,Match
a,Miniswap,Mooniswap,Oasis,OpenRelay,S.Finance,SakeSwap,SeedDex,SingularX,StarBitEx,SushiSwap,SwapX,SwitchDex,TacoSwap,TokenJar,TokenStore,TokenTrove,Tokenlon,TradexOne,Uniswap,ZeusSwap,dYdX,dex.blue}, --exchange {1inch,AfroDex,AirSwap,Amplbitcratic,Balancer,BestSwap,B
itox,CellSwap,Cellswap,Cofix,Coinchangex,Curve,DDEX,DUBIex,DecentrEx,DeversiFi,Dodo,ETHERCExchange,EtherBlockchain,EtherDelta,Ethernext,Ethfinex,FEGex,FFFSwap,Fordex,GUDecks,GUDeks,HiSwap,IDEX,LedgerDex,Matcha,Miniswap,Mooniswap,Oasis,OpenRelay,S.Finance,SakeSwap,SeedD
ex,SingularX,StarBitEx,SushiSwap,SwapX,SwitchDex,TacoSwap,TokenJar,TokenStore,TokenTrove,Tokenlon,TradexOne,Uniswap,ZeusSwap,dYdX,dex.blue}
                        Decentralized exchange name. (default: Uniswap)
  -d DAYS, --days DAYS  Number of days to display data for. (default: 90)
  -s {base,quoted,trades,tradeAmount}, --sort {base,quoted,trades,tradeAmount}
                        Sort by given column. (default: tradeAmount)
  --descend             Flag to sort in descending order (lowest first)
                        (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```
