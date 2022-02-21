```
usage: lowfloat [-l LIMIT] [-h] [--export {csv,json,xlsx}]
```

Print top stocks with lowest float. LowFloat.com provides a convenient sorted database of stocks which have a float of under 10 million shares. Additional key data such as the number of outstanding shares, short interest, and company industry is displayed. Data is presented for the Nasdaq Stock Market, the New York Stock Exchange, the American Stock Exchange, and the Over the Counter Bulletin Board. [Source: www.lowfloat.com]

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        limit of stocks to display (default: 5)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx (default: )
```

Example:
```
2022 Feb 16, 04:09 (✨) /stocks/disc/ $ lowfloat -l 10
                                                           Top Float Stocks
┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Ticker ┃ Company                               ┃ Exchange ┃ Float ┃ Outstd ┃ ShortInt ┃ Industry                                   ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ DIT    │ Amcon Distributing Co                 │ AMEX     │ 160K  │ 580K   │ 1.09%    │ Retail (Grocery)                           │
├────────┼───────────────────────────────────────┼──────────┼───────┼────────┼──────────┼────────────────────────────────────────────┤
│ SEB    │ Seaboard Corp                         │ AMEX     │ 240K  │ 1.16M  │ 0.78%    │ Fish/Livestock                             │
├────────┼───────────────────────────────────────┼──────────┼───────┼────────┼──────────┼────────────────────────────────────────────┤
│ MAYS   │ JW Mays Inc                           │ Nasdaq   │ 390K  │ 2.02M  │ 0.85%    │ Real Estate Operations                     │
├────────┼───────────────────────────────────────┼──────────┼───────┼────────┼──────────┼────────────────────────────────────────────┤
│ HMG    │ HMG Courtland Properties              │ AMEX     │ 400K  │ 1.02M  │ 0.28%    │ Real Estate Operations                     │
├────────┼───────────────────────────────────────┼──────────┼───────┼────────┼──────────┼────────────────────────────────────────────┤
│ VBFC   │ Village Bank and Trust Financial Corp │ Nasdaq   │ 530K  │ 1.47M  │ 0.10%    │ Regional Banks                             │
├────────┼───────────────────────────────────────┼──────────┼───────┼────────┼──────────┼────────────────────────────────────────────┤
│ BDL    │ Flanigan's Enterprises Inc            │ AMEX     │ 550K  │ 1.86M  │ 0.05%    │ Restaurants                                │
├────────┼───────────────────────────────────────┼──────────┼───────┼────────┼──────────┼────────────────────────────────────────────┤
│ RAND   │ Rand Capital Corp                     │ Nasdaq   │ 620K  │ 2.58M  │ 0.01%    │ Misc. Financial Services                   │
├────────┼───────────────────────────────────────┼──────────┼───────┼────────┼──────────┼────────────────────────────────────────────┤
│ NCSM   │ NCS Multistage Holdings Inc           │ Nasdaq   │ 630K  │ 2.38M  │ 0.69%    │ Oil & Gas - Related Services and Equipment │
├────────┼───────────────────────────────────────┼──────────┼───────┼────────┼──────────┼────────────────────────────────────────────┤
│ INTG   │ Intergroup Corp                       │ Nasdaq   │ 650K  │ 2.20M  │ 0.62%    │ Real Estate Operations                     │
└────────┴───────────────────────────────────────┴──────────┴───────┴────────┴──────────┴────────────────────────────────────────────┘
```
