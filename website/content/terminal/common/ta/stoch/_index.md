```
usage: stoch [-k N_FASTKPERIOD] [-d N_SLOWDPERIOD] [--slowkperiod N_SLOWKPERIOD] [--export {csv,json,xlsx}] [-h]
```

The Stochastic Oscillator measures where the close is in relation to the recent trading range. The values range from zero to 100. %D values over 75
indicate an overbought condition; values under 25 indicate an oversold condition. When the Fast %D crosses above the Slow %D, it is a buy signal;
when it crosses below, it is a sell signal. The Raw %K is generally considered too erratic to use for crossover signals.

```
optional arguments:
  -k N_FASTKPERIOD, --fastkperiod N_FASTKPERIOD
                        The time period of the fastk moving average (default: 14)
  -d N_SLOWDPERIOD, --slowdperiod N_SLOWDPERIOD
                        The time period of the slowd moving average (default: 3)
  --slowkperiod N_SLOWKPERIOD
                        The time period of the slowk moving average (default: 3)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

![stoch](https://user-images.githubusercontent.com/46355364/154311913-d58e58bb-d116-44dd-ae4b-44e59c25f22a.png)
