```
usage: ally_movers [-l {toplosers,toppctlosers,topvolume,topactive,topgainers,toppctgainers}]
                   [-e {A,N,Q,U,V}] [-n NUM] [--export {csv,json,xlsx}] [-h]
```
Get stock movers
```
optional arguments:
  -l {toplosers,toppctlosers,topvolume,topactive,topgainers,toppctgainers}, --list {toplosers,toppctlosers,topvolume,topactive,topgainers,toppctgainers}
                        List to get movers of (default: topactive)
  -e {A,N,Q,U,V}, --exchange {A,N,Q,U,V}
                        Exchange to look at. Can be A:American Stock Exchange. N:New York Stock Exchange.
                        Q:NASDAQ U:NASDAQ Bulletin Board V:NASDAQ OTC Other (default: N)
  -n NUM, --num NUM     Number to show (default: 15)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```
