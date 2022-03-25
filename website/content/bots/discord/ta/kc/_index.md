ta-vlt kc - Keltner Channels

https://school.stockcharts.com/doku.php?id=technical_indicators:keltner_channels

Keltner Channels are volatility-based bands that are placed on either side of an asset's price and can aid in determining the direction of a trend. The Keltner channel uses the average true range (ATR) or volatility, with breaks above or below the top and bottom barriers signaling a continuation. The channels are typically set two Average True Range values above and below the 20-day EMA. The exponential moving average dictates direction and the Average True Range sets channel width. Keltner Channels are a trend following indicator used to identify reversals with channel breakouts and channel direction. Channels can also be used to identify overbought and oversold levels when the trend is flat.

In his 1960 book, How to Make Money in Commodities, Chester Keltner introduced the “Ten-Day Moving Average Trading Rule,” which is credited as the original version of Keltner Channels. This original version started with a 10-day SMA of the typical price {(H+L+C)/3)} as the centerline. The 10-day SMA of the High-Low range was added and subtracted to set the upper and lower channel lines. Linda Bradford Raschke introduced the newer version of Keltner Channels in the 1980s. Like Bollinger Bands, this new version used a volatility based indicator, Average True Range (ATR), to set channel width. StockCharts.com uses this newer version of Keltner Channels.

```
Middle Line: 20-day exponential moving average 
Upper Channel Line: 20-day EMA + (2 x ATR(10))
Lower Channel Line: 20-day EMA - (2 x ATR(10))
```

![Screen Shot 2022-03-22 at 7 39 48 PM](https://user-images.githubusercontent.com/85772166/159613248-326d1a32-1940-4d19-aa34-1d624822bae0.png)

```
/ta-vlt kc ticker: TSLA interval: 60 ma_mode: ema past_days: 180 extended_hours: true heikin_candles: true
```

![Screen Shot 2022-03-22 at 7 45 50 PM](https://user-images.githubusercontent.com/85772166/159613790-eedafa4e-8810-4059-9bdd-499981748b19.png)
