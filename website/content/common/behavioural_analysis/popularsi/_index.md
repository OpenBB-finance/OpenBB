```
usage: popularsi [-l LIMIT] [-h]
```

The stocks with highest Average Hype Index right now.

AHI (Absolute Hype Index)
---
AHI is a measure of how much people are talking about a stock on social media.
It is calculated by dividing the total number of mentions for the chosen stock on a social network by the mean number of mentions any stock receives on that social medium.

Sentiment Investor analyzes data from four major social media platforms to generate hourly metrics on over 2,000 stocks. Sentiment provides volume and
sentiment metrics powered by proprietary NLP models.

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        the maximum number of stocks to retrieve
  -h, --help            show this help message
```
Sample output:
```
(✨) (stocks)>(ba)> popularsi
  Rank  Ticker      AHI
------  --------  -----
     1  AMC       4.514
     2  TSLA      4.184
     3  BTC       4.045
     4  SPY       3.890
     5  WISH      3.175
     6  NAKD      2.220
     7  SOFI      2.153
     8  SAND      1.813
     9  AMD       1.628
    10  MMAT      1.617
