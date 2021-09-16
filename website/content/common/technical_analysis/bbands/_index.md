```
usage: bbands [-l N_LENGTH] [-s N_STD] [-m S_MAMODE] [--export {csv,json,xlsx}] [-h]
```

Bollinger Bands consist of three lines. The middle band is a simple moving average (generally 20 periods) of the typical price (TP). The upper and lower bands are F standard deviations (generally 2) above and below the middle band. The bands widen and narrow when the volatility of the price is higher or lower, respectively. Bollinger Bands do not, in themselves, generate buy or sell signals; they are an indicator of overbought or oversold conditions. When the price is near the upper or lower band it indicates that a reversal may be imminent. The middle band becomes a support or resistance level. The upper and lower bands can also be interpreted as price targets. When the price bounces off of the lower band and crosses the middle band, then the upper band becomes the price target.

```
optional arguments:
  -l N_LENGTH, --length N_LENGTH
                        length (default: 5)
  -s N_STD, --std N_STD
                        std (default: 2)
  -m S_MAMODE, --mamode S_MAMODE
                        mamode (default: sma)
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

![bbands](https://user-images.githubusercontent.com/25267873/108602984-28699580-739d-11eb-9b82-2683a9840145.png)
