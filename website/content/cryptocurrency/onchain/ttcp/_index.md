```
usage: ttcp [-l N]
            [-e {1inch,afrodex,airswap,amplbitcratic,balancer,bestswap,bitox,cellswap,cofix,coinchangex,curve,ddex,dubiex,decentrex,deversifi,dodo,ethercexchange,etherblockchain,etherdelta,ethernext,ethfinex,fegex,fffswap,fordex,gudecks,gudeks,hiswap,idex,ledgerdex,mat
cha,miniswap,mooniswap,oasis,openrelay,s.finance,sakeswap,seeddex,singularx,starbitex,sushiswap,swapx,switchdex,tacoswap,tokenjar,tokenstore,tokentrove,tokenlon,tradexone,uniswap,zeusswap,dydx,dex.blue}]
            [-d DAYS] [-s {base,quoted,trades,tradeAmount}] [--descend] [-h]
            [--export {csv,json,xlsx}]
```

Display most traded crypto pairs on given decentralized exchange in chosen
time period [Source: https://graphql.bitquery.io/]

```
optional arguments:
  -l N, --limit N     display N number records (default: 10)
  -e {1inch,afrodex,airswap,amplbitcratic,balancer,bestswap,bitox,cellswap,cofix,coinchangex,curve,ddex,dubiex,decentrex,deversifi,dodo,ethercexchange,etherblockchain,etherdelta,ethernext,ethfinex,fegex,fffswap,fordex,gudecks,gudeks,hiswap,idex,ledgerdex,matcha,miniswa
p,mooniswap,oasis,openrelay,s.finance,sakeswap,seeddex,singularx,starbitex,sushiswap,swapx,switchdex,tacoswap,tokenjar,tokenstore,tokentrove,tokenlon,tradexone,uniswap,zeusswap,dydx,dex.blue}, --exchange {1inch,afrodex,airswap,amplbitcratic,balancer,bestswap,bitox,cell
swap,cofix,coinchangex,curve,ddex,dubiex,decentrex,deversifi,dodo,ethercexchange,etherblockchain,etherdelta,ethernext,ethfinex,fegex,fffswap,fordex,gudecks,gudeks,hiswap,idex,ledgerdex,matcha,miniswap,mooniswap,oasis,openrelay,s.finance,sakeswap,seeddex,singularx,starb
itex,sushiswap,swapx,switchdex,tacoswap,tokenjar,tokenstore,tokentrove,tokenlon,tradexone,uniswap,zeusswap,dydx,dex.blue}
                        Decentralized exchange name. (default: Uniswap)
  -d DAYS, --days DAYS  Number of days to display data for. (default: 30)
  -s {base,quoted,trades,tradeAmount}, --sort {base,quoted,trades,tradeAmount}
                        Sort by given column. (default: tradeAmount)
  --descend             Flag to sort in descending order (lowest first)
                        (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```
