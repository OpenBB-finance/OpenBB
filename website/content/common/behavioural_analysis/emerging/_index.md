```
usage: emerging [-l LIMIT] [-h]
```

The emerging command prints the stocks with highest Relative Hype Index right now.

RHI (Relative Hype Index)
---
RHI is a measure of whether people are talking about a stock more or less than
usual, calculated by dividing the mean AHI for the past day by the mean AHI for
for the past week for that stock.

===

Sentiment Investor analyzes data from four major social media platforms to
generate hourly metrics on over 2,000 stocks. Sentiment provides volume and
sentiment metrics powered by proprietary NLP models.

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        the maximum number of stocks to retrieve
  -h, --help            show this help message
  ```

  ```
  (✨) (stocks)>(ba)> emerging
  Rank  Ticker      RHI
------  --------  -----
     1  FINV      6.432
     2  GOVX      6.282
     3  JZXN      5.368
     4  GOGO      5.311
     5  GWW       4.993
     6  SHW       4.937
     7  EYES      4.772
     8  FSD       4.387
     9  NUAN      4.019
    10  JNUG      3.970
    ```
