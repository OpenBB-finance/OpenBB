```
usage: feargreed [-i {jbd,mv,pco,mm,sps,spb,shd,index}] [--export {png,jpg,pdf,svg}] [-h]
```

Displays the CNN Fear And Greed Index. Source: https://money.cnn.com/data/fear-and-greed/

```
optional arguments:
  -i {jbd,mv,pco,mm,sps,spb,shd,index}, --indicator {jbd,mv,pco,mm,sps,spb,shd,index}
                        CNN Fear And Greed indicator or index. From Junk Bond Demand, Market Volatility, Put and Call Options, Market Momentum Stock
                        Price Strength, Stock Price Breadth, Safe Heaven Demand, and Index.
  --export {png,jpg,pdf,svg}
                        Export plot to png,jpg,pdf,svg file
  -h, --help            show this help message
```

```
(✨) (economy)> feargreed
Fear & Greed Now: 82 (Extreme Greed)
   Previous Close: 83 (Extreme Greed)
   1 Week Ago: 86 (Extreme Greed)
   1 Month Ago: 50 (Neutral)
   1 Year Ago: 59 (Greed)

Junk Bond Demand: Extreme Greed                                                                     [Updated Nov 14 at 7:00pm]
   Investors in low quality junk bonds are accepting 1.82 percentage points in additional yield over safer investment grade corporate bonds. While this spread is historically high, it is sharply lower than recent prices and suggests that investors are pursuing higher risk strategies.
   (Last changed Oct 27 from a Greed rating)

Market Volatility: Extreme Greed                                                                    [Updated Nov 14 at 7:00pm]
   Stocks have outperformed bonds by 4.68 percentage points during the last 20 trading days. This is close to the strongest performance for stocks relative to bonds in the past two years and indicates investors are rotating into stocks from the relative safety of bonds.
   (Last changed Oct 14 from a Fear rating)

Put and Call Options: Extreme Greed                                                                 [Updated Nov 15 at 4:55pm]
   The S&P 500 is 6.32% above its 125-day average. This is further above the average than has been typical during the last two years and rapid increases like this often indicate extreme greed.
   (Last changed Oct 27 from a Greed rating)

Market Momentum: Extreme Greed                                                                      [Updated Nov 15 at 4:24pm]
   During the last five trading days, volume in put options has lagged volume in call options by 60.83% as investors make bullish bets in their portfolios. This is among the lowest levels of put buying seen during the last two years, indicating extreme greed on the part of investors.
   (Last changed Oct 27 from a Greed rating)

Stock Price Strength: Greed                                                                         [Updated Nov 15 at 4:04pm]
   The McClellan Volume Summation Index measures advancing and declining volume on the NYSE. During the last month, approximately 6.03% more of each day's volume has traded in advancing issues than in declining issues, pushing this indicator towards the upper end of its range for the last two years.
   (Last changed Oct 22 from a Neutral rating)

Stock Price Breadth: Greed                                                                          [Updated Nov 15 at 4:00pm]
   The number of stocks hitting 52-week highs exceeds the number hitting lows and is at the upper end of its range, indicating greed.
   (Last changed Nov 5 from a Neutral rating)

Safe Heaven Demand: Neutral                                                                         [Updated Nov 15 at 4:15pm]
   The CBOE Volatility Index (VIX) is at 16.49. This is a neutral reading and indicates that market risks appear low.
   (Last changed Oct 4 from an Extreme Fear rating)
   ```

<img size="1400" alt="Feature Screenshot - feargreed graphs" src="https://user-images.githubusercontent.com/85772166/141887165-f556eec5-ad6c-4551-a476-b038dd63773b.png">

