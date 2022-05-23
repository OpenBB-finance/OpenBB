```
usage: hsi [-n N_NUM] [--export {csv,json,xlsx}] [-h]
```

Browse a sorted database of stocks which have a short interest of over 20 percent. Additional key data such as the float, number of outstanding shares, and company industry is displayed. Data is presented for the Nasdaq Stock Market, the New York Stock Exchange, and the American Stock Exchange. Source: https://www.highshortinterest.com

```
optional arguments:
  -n N_NUM, --num N_NUM
                        Number of top stocks to print. (default: 10)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 08:49 (✨) /stocks/dps/ $ hsi
                                                       Top Interest Stocks
┌────────┬───────────────────────────────┬──────────┬──────────┬─────────┬─────────┬────────────────────────────────────────────┐
│ Ticker │ Company                       │ Exchange │ ShortInt │ Float   │ Outstd  │ Industry                                   │
├────────┼───────────────────────────────┼──────────┼──────────┼─────────┼─────────┼────────────────────────────────────────────┤
│ CRTX   │ Cortexyme Inc                 │ Nasdaq   │ 47.00%   │ 15.56M  │ 29.88M  │ Biotechnology & Medical Research           │
├────────┼───────────────────────────────┼──────────┼──────────┼─────────┼─────────┼────────────────────────────────────────────┤
│ BLNK   │ Blink Charging Co             │ Nasdaq   │ 40.97%   │ 36.46M  │ 42.20M  │ Utilities - Electric                       │
├────────┼───────────────────────────────┼──────────┼──────────┼─────────┼─────────┼────────────────────────────────────────────┤
│ GOGO   │ Gogo Inc                      │ Nasdaq   │ 39.10%   │ 45.62M  │ 109.95M │ Communications Services                    │
├────────┼───────────────────────────────┼──────────┼──────────┼─────────┼─────────┼────────────────────────────────────────────┤
│ FUV    │ Arcimoto Inc                  │ Nasdaq   │ 35.67%   │ 28.76M  │ 37.64M  │ Auto & Truck Manufacturers                 │
├────────┼───────────────────────────────┼──────────┼──────────┼─────────┼─────────┼────────────────────────────────────────────┤
│ ICPT   │ Intercept Pharmaceuticals Inc │ Nasdaq   │ 35.61%   │ 23.52M  │ 29.55M  │ Biotechnology & Medical Research           │
├────────┼───────────────────────────────┼──────────┼──────────┼─────────┼─────────┼────────────────────────────────────────────┤
│ SFT    │ Shift Technologies Inc        │ Nasdaq   │ 35.18%   │ 54.48M  │ 81.31M  │ Retailers - Auto Vehicles, Parts & Service │
├────────┼───────────────────────────────┼──────────┼──────────┼─────────┼─────────┼────────────────────────────────────────────┤
│ BGFV   │ Big 5 Sporting Goods Corp     │ Nasdaq   │ 34.45%   │ 20.01M  │ 22.31M  │ Retailers - Miscellaneous Specialty        │
├────────┼───────────────────────────────┼──────────┼──────────┼─────────┼─────────┼────────────────────────────────────────────┤
│ RMO    │ Romeo Power Inc               │ NYSE     │ 34.28%   │ 90.21M  │ 134.46M │ Electrical Components & Equipment          │
├────────┼───────────────────────────────┼──────────┼──────────┼─────────┼─────────┼────────────────────────────────────────────┤
│ BYND   │ Beyond Meat Inc               │ Nasdaq   │ 33.99%   │ 56.25M  │ 63.33M  │ Food Processing                            │
├────────┼───────────────────────────────┼──────────┼──────────┼─────────┼─────────┼────────────────────────────────────────────┤
│ SDC    │ SmileDirectClub Inc           │ Nasdaq   │ 33.23%   │ 110.88M │ 119.14M │ Medical Equipment, Supplies & Distribution │
└────────┴───────────────────────────────┴──────────┴──────────┴─────────┴─────────┴────────────────────────────────────────────┘
```
