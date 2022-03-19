```
usage: candles [-g GRANULARITY] [-l CANDLECOUNT] [-a] [-b] [-c] [-e] [-o] [-r] [-s] [-v] [-h]
```

Display Candle Data

```
optional arguments:
  -g GRANULARITY, --granularity GRANULARITY
			The timeframe to get for the candle chart (Seconds: S5, S10, S15, S30 Minutes: M1, M2, M4, M5, M10, M15, M30 Hours: H1, H2, H3, H4, H6, H8, H12 Day (default): D, Week: W Month: M
  -l CANDLECOUNT, --limit CANDLECOUNT
			The number of candles to retrieve. Default:180
  -a, --ad              Adds ad (Accumulation/Distribution Indicator) to the chart
  -b, --bbands          Adds Bollinger Bands to the chart
  -c, --cci             Adds cci (Commodity Channel Index) to the chart
  -e, --ema             Adds ema (Exponential Moving Average) to the chart
  -o, --obv             Adds obv (On Balance Volume) to the chart
  -r, --rsi             Adds rsi (Relative Strength Index) to the chart
  -s, --sma             Adds sma (Simple Moving Average) to the chart
  -v, --vwap            Adds vwap (Volume Weighted Average Price) to the chart
  -h, --help            show this help message
```
