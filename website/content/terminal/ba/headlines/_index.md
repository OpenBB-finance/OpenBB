```
usage: headlines [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}]
```

FinBrain collects the news headlines from 15+ major financial news sources on a daily basis and analyzes them to generate sentiment scores for more than 4500 US stocks.FinBrain Technologies develops deep learning algorithms for financial analysis and prediction, which
currently serves traders from more than 150 countries all around the world. [Source: <https://finbrain.tech>]

```
optional arguments:
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```

Example:

```
2022 Feb 16, 10:20 (🦋) /stocks/ba/ $ headlines

FinBrain Ticker Sentiment
┏━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃            ┃ Sentiment ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ 2022-02-03 │ 0.107     │
├────────────┼───────────┤
│ 2022-02-04 │ 0.354     │
├────────────┼───────────┤
│ 2022-02-07 │ 0.129     │
├────────────┼───────────┤
│ 2022-02-08 │ 0.173     │
├────────────┼───────────┤
│ 2022-02-09 │ 0.187     │
├────────────┼───────────┤
│ 2022-02-10 │ 0.161     │
├────────────┼───────────┤
│ 2022-02-11 │ 0.311     │
├────────────┼───────────┤
│ 2022-02-14 │ 0.174     │
├────────────┼───────────┤
│ 2022-02-15 │ 0.275     │
├────────────┼───────────┤
│ 2022-02-16 │ 0.329     │
└────────────┴───────────┘
```

![headlines](https://user-images.githubusercontent.com/46355364/154296211-b0380095-5f84-4bae-955e-9ef96c9704af.png)
