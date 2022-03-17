```
usage: score [--export {csv,json,xlsx}] [-h]
```

In this view you can find different kind of scores for loaded coin. Those scores represents different rankings, sentiment metrics, some user stats
and others. You will see CoinGecko scores, Developer Scores, Community Scores, Sentiment, Reddit scores and many others.

```
optional arguments:
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 15, 07:47 (✨) /crypto/dd/ $ score

        Different Scores for Loaded Coin
┌─────────────────────────────────┬────────────┐
│ Metric                          │ Value      │
├─────────────────────────────────┼────────────┤
│ Coingecko Rank                  │ 1.00       │
├─────────────────────────────────┼────────────┤
│ Coingecko Score                 │ 80.77      │
├─────────────────────────────────┼────────────┤
│ Developer Score                 │ 98.91      │
├─────────────────────────────────┼────────────┤
│ Community Score                 │ 72.62      │
├─────────────────────────────────┼────────────┤
│ Liquidity Score                 │ 100.25     │
├─────────────────────────────────┼────────────┤
│ Sentiment Votes Up Percentage   │ 83.17      │
├─────────────────────────────────┼────────────┤
│ Sentiment Votes Down Percentage │ 16.83      │
├─────────────────────────────────┼────────────┤
│ Public Interest Score           │ 0.34       │
├─────────────────────────────────┼────────────┤
│ Facebook Likes                  │            │
├─────────────────────────────────┼────────────┤
│ Twitter Followers               │ 4669906.00 │
├─────────────────────────────────┼────────────┤
│ Reddit Average Posts 48H        │ 7.46       │
├─────────────────────────────────┼────────────┤
│ Reddit Average Comments 48H     │ 1298.00    │
├─────────────────────────────────┼────────────┤
│ Reddit Subscribers              │ 3908131.00 │
├─────────────────────────────────┼────────────┤
│ Reddit Accounts Active 48H      │ 5154.00    │
├─────────────────────────────────┼────────────┤
│ Telegram Channel User Count     │            │
├─────────────────────────────────┼────────────┤
│ Alexa Rank                      │ 9440.00    │
├─────────────────────────────────┼────────────┤
│ Bing Matches                    │            │
└─────────────────────────────────┴────────────┘
```
