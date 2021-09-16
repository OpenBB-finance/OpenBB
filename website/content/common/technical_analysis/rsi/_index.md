```
usage: rsi [-l N_LENGTH] [-s N_SCALAR] [-d N_DRIFT] [--export {csv,json,xlsx}] [-h]
```

The Relative Strength Index (RSI) calculates a ratio of the recent upward price movements to the absolute price movement. The RSI ranges from 0 to 100. The RSI is interpreted as an overbought/oversold indicator when the value is over 70/below 30. You can also look for divergence with price. If the price is making new highs/lows, and the RSI is not, it indicates a reversal.

```
optional arguments:
  -l N_LENGTH, --length N_LENGTH
                        length (default: 14)
  -s N_SCALAR, --scalar N_SCALAR
                        scalar (default: 100)
  -d N_DRIFT, --drift N_DRIFT
                        drift (default: 1)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

![rsi](https://user-images.githubusercontent.com/25267873/108602743-957c2b80-739b-11eb-9d0d-6f530b3abb91.png)
