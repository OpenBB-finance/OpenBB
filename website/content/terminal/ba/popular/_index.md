```
usage: popular [-l LIMIT] [-n NUM] [-s S_SUBREDDIT] [-h]
```

The current popular tickers on [Reddit](https://Reddit.com)

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        limit of top tickers to retrieve (default: 10)
  -n NUM, --num NUM     number of posts retrieved per sub reddit. (default: 50)
  -s S_SUBREDDIT, --sub S_SUBREDDIT
                        subreddits to look for tickers, e.g. pennystocks,stocks. Default: pennystocks, RobinHoodPennyStocks, Daytrading, StockMarket, stocks, investing, wallstreetbets (default: None)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 16, 10:31 (✨) /stocks/ba/ $ popular
Search for latest tickers for 50 'Superstonk' posts
  217 potential tickers found.
Search for latest tickers for 50 'pennystocks' posts
  107 potential tickers found.
Search for latest tickers for 50 'RobinHoodPennyStocks' posts
  7 potential tickers found.
Search for latest tickers for 50 'Daytrading' posts
  56 potential tickers found.
Search for latest tickers for 50 'StockMarket' posts
  77 potential tickers found.
Search for latest tickers for 50 'stocks' posts
  97 potential tickers found.
Search for latest tickers for 50 'investing' posts
  37 potential tickers found.
Search for latest tickers for 50 'wallstreetbets' posts
  31 potential tickers found.
  
                                                             The following TOP 10 tickers have been mentioned:
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Mentions ┃ Ticker ┃ Company                                                ┃ Sector               ┃ Price  ┃ Change  ┃ Perf Month ┃ URL                                  ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 57       │ GME    │ GameStop Corp.                                         │ Consumer Cyclical    │ 129.34 │ 2.52%   │ 8.15%      │ https://finviz.com/quote.ashx?t=GME  │
├──────────┼────────┼────────────────────────────────────────────────────────┼──────────────────────┼────────┼─────────┼────────────┼──────────────────────────────────────┤
│ 40       │ POST   │ Post Holdings, Inc.                                    │ Consumer Defensive   │ 109.14 │ -0.18%  │ -7.18%     │ https://finviz.com/quote.ashx?t=POST │
├──────────┼────────┼────────────────────────────────────────────────────────┼──────────────────────┼────────┼─────────┼────────────┼──────────────────────────────────────┤
│ 10       │ SPY    │ Financial                                              │ Exchange Traded Fund │ 442.48 │ -0.81%  │ -4.01%     │ https://finviz.com/quote.ashx?t=SPY  │
├──────────┼────────┼────────────────────────────────────────────────────────┼──────────────────────┼────────┼─────────┼────────────┼──────────────────────────────────────┤
│ 8        │ QQQ    │ Financial                                              │ Exchange Traded Fund │ 351.15 │ -1.40%  │ -6.28%     │ https://finviz.com/quote.ashx?t=QQQ  │
├──────────┼────────┼────────────────────────────────────────────────────────┼──────────────────────┼────────┼─────────┼────────────┼──────────────────────────────────────┤
│ 6        │ VTI    │ Vanguard Index Funds - Vanguard Total Stock Market ETF │ Financial            │ 224.13 │ -0.86%  │ -3.81%     │ https://finviz.com/quote.ashx?t=VTI  │
├──────────┼────────┼────────────────────────────────────────────────────────┼──────────────────────┼────────┼─────────┼────────────┼──────────────────────────────────────┤
│ 5        │ AAPL   │ Apple Inc.                                             │ Technology           │ 170.53 │ -1.31%  │ -0.16%     │ https://finviz.com/quote.ashx?t=AAPL │
├──────────┼────────┼────────────────────────────────────────────────────────┼──────────────────────┼────────┼─────────┼────────────┼──────────────────────────────────────┤
│ 5        │ ESG    │ Financial                                              │ Exchange Traded Fund │ 107.88 │ -0.65%  │ -4.64%     │ https://finviz.com/quote.ashx?t=ESG  │
├──────────┼────────┼────────────────────────────────────────────────────────┼──────────────────────┼────────┼─────────┼────────────┼──────────────────────────────────────┤
│ 5        │ SHOP   │ Shopify Inc.                                           │ Technology           │ 728.52 │ -18.10% │ -19.35%    │ https://finviz.com/quote.ashx?t=SHOP │
├──────────┼────────┼────────────────────────────────────────────────────────┼──────────────────────┼────────┼─────────┼────────────┼──────────────────────────────────────┤
│ 4        │ AMD    │ Advanced Micro Devices, Inc.                           │ Technology           │ 117.21 │ -3.51%  │ -11.26%    │ https://finviz.com/quote.ashx?t=AMD  │
├──────────┼────────┼────────────────────────────────────────────────────────┼──────────────────────┼────────┼─────────┼────────────┼──────────────────────────────────────┤
│ 4        │ NVDA   │ NVIDIA Corporation                                     │ Technology           │ 258.61 │ -2.39%  │ -1.66%     │ https://finviz.com/quote.ashx?t=NVDA │
├──────────┼────────┼────────────────────────────────────────────────────────┼──────────────────────┼────────┼─────────┼────────────┼──────────────────────────────────────┤
│ 3        │ RESN   │ Resonant Inc.                                          │ Technology           │ 4.35   │ -1.01%  │ 185.06%    │ https://finviz.com/quote.ashx?t=RESN │
└──────────┴────────┴────────────────────────────────────────────────────────┴──────────────────────┴────────┴─────────┴────────────┴──────────────────────────────────────┘
```
