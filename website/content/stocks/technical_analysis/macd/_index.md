```
usage: macd [-f N_FAST] [-s N_SLOW] [--signal N_SIGNAL] [--export {csv,json,xlsx}] [-h]
```

The Moving Average Convergence Divergence (MACD) is the difference between two Exponential Moving Averages. The Signal line is an Exponential Moving Average of the MACD. The MACD signals trend changes and indicates the start of new trend direction. High values indicate overbought conditions, low values indicate oversold conditions. Divergence with the price indicates an end to the current trend, especially if the MACD is at extreme high or
low values. When the MACD line crosses above the signal line a buy signal is generated. When the MACD crosses below the signal line a sell signal is generated. To confirm the signal, the MACD should be above zero for a buy, and below zero for a sell.

```
optional arguments:
  -f N_FAST, --fast N_FAST
                        The short period. (default: 12)
  -s N_SLOW, --slow N_SLOW
                        The long period. (default: 26)
  --signal N_SIGNAL     The signal period. (default: 9)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

![macd](https://user-images.githubusercontent.com/25267873/108602739-92813b00-739b-11eb-8a4e-8fa7ed66b2b6.png)
