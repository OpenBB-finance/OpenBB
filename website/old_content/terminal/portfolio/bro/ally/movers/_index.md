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

Sample Output:

```
(🦋) (bro)>(ally)> movers -n 5 -l toplosers
╒══════╤════════╤════════════╤═════════╤═══════════════════════╤════════╤═════════╤════════╤═════════╕
│      │    chg │ chg_sign   │    last │ name                  │   pchg │    pcls │   rank │      vl │
╞══════╪════════╪════════════╪═════════╪═══════════════════════╪════════╪═════════╪════════╪═════════╡
│ CABO │ -19.90 │ u          │ 1915.98 │ CABLE ONE INC         │   1.03 │ 1935.88 │      1 │   12311 │
├──────┼────────┼────────────┼─────────┼───────────────────────┼────────┼─────────┼────────┼─────────┤
│ BILL │ -12.28 │ u          │  271.47 │ BILL.COM HOLDINGS INC │   4.33 │  283.75 │      2 │ 2340470 │
├──────┼────────┼────────────┼─────────┼───────────────────────┼────────┼─────────┼────────┼─────────┤
│ BLK  │ -10.06 │ u          │  847.21 │ BLACKROCK INC         │   1.17 │  857.27 │      3 │  410960 │
├──────┼────────┼────────────┼─────────┼───────────────────────┼────────┼─────────┼────────┼─────────┤
│ CVNA │  -6.90 │ u          │  319.60 │ CARVANA CO            │   2.11 │  326.50 │      4 │  551151 │
├──────┼────────┼────────────┼─────────┼───────────────────────┼────────┼─────────┼────────┼─────────┤
│ FICO │  -5.50 │ u          │  421.06 │ FAIR ISAAC CORP       │   1.29 │  426.56 │      5 │  118449 │
╘══════╧════════╧════════════╧═════════╧═══════════════════════╧════════╧═════════╧════════╧═════════╛
```
