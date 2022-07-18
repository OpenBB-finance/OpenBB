```
usage: hotpenny [-l LIMIT] [-h] [--export {csv,json,xlsx}]
```

This site provides a list of todays most active and hottest penny stocks. While not for everyone, penny stocks can be exciting and rewarding investments in many ways. With penny stocks, you can get more bang for the buck. You can turn a few hundred dollars into thousands, just by getting in on the right penny stock at the right time. Penny stocks are increasing in popularity. More and more investors of all age groups and skill levels are getting involved, and the dollar amounts they are putting into these speculative investments are representing a bigger portion of their portfolios. [Source: www.pennystockflow.com]

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
2022 Feb 16, 04:04 (✨) /stocks/disc/ $ hotpenny
                        Top Penny Stocks
┏━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┓
┃       ┃ Price  ┃ Change ┃ $ Volume     ┃ Volume    ┃ # Trades ┃
┡━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━┩
│ TCEHY │ $61.01 │ 1.55%  │ $303,380,785 │ 4,994,963 │ 17,401   │
├───────┼────────┼────────┼──────────────┼───────────┼──────────┤
│ GBTC  │ $31.28 │ 6.25%  │ $110,596,120 │ 3,545,597 │ 14,364   │
├───────┼────────┼────────┼──────────────┼───────────┼──────────┤
│ BHPLF │ $33.74 │ -1.06% │ $65,818,744  │ 1,962,313 │ 23       │
├───────┼────────┼────────┼──────────────┼───────────┼──────────┤
│ RHHBY │ $46.92 │ 1.49%  │ $56,390,274  │ 1,201,629 │ 2,463    │
└───────┴────────┴────────┴──────────────┴───────────┴──────────┘
```
