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

Example:

```
2022 Feb 15, 04:51 (✨) /economy/ $ feargreed
Fear & Greed Now: 32 (Fear)
   Previous Close: 34 (Fear)
   1 Week Ago: 34 (Fear)
   1 Month Ago: 58 (Greed)
   1 Year Ago: 63 (Greed)

Junk Bond Demand: Extreme Greed                                                                     [Updated Feb 11 at 2:09am]
   During the last five trading days, volume in put options has lagged volume in call options by 87.34% as investors make bullish bets in their portfolios. This is among the lowest levels of put buying seen during the last two years, indicating extreme greed on the part of investors.
   (Last changed Dec 29 from a Fear rating)

Market Volatility: Neutral                                                                          [Updated Feb 13 at 7:00pm]
   The CBOE Volatility Index (VIX) is at 28.33. This is a neutral reading and indicates that market risks appear low.
   (Last changed Jan 27 from an Extreme Fear rating)

Put and Call Options: Fear                                                                          [Updated Feb 13 at 7:00pm]
   Investors in low quality junk bonds are accepting 1.78 percentage points in additional yield over safer investment grade corporate bonds. This spread is higher than what has been typical for the last two years and indicates that investors are risk averse.
   (Last changed Feb 9 from a Neutral rating)

Market Momentum: Fear                                                                               [Updated Feb 14 at 4:06pm]
   The McClellan Volume Summation Index measures advancing and declining volume on the NYSE. During the last month, approximately 5.69% more of each day's volume has traded in declining issues than in advancing issues, pushing this indicator towards the lower end of its range for the last two years.
   (Last changed Feb 4 from an Extreme Fear rating)

Stock Price Strength: Extreme Fear                                                                  [Updated Feb 13 at 7:00pm]
   Bonds have outperformed stocks by 3.67 percentage points during the last 20 trading days. This is close to the weakest performance for stocks relative to bonds in the past two years and indicates investors are fleeing risky stocks for the safety of bonds.
   (Last changed Feb 9 from a Fear rating)

Stock Price Breadth: Extreme Fear                                                                   [Updated Feb 14 at 4:00pm]
   The number of stocks hitting 52-week lows exceeds the number hitting highs and is at the lower end of its range, indicating extreme fear.
   (Last changed Jan 20 from a Fear rating)

Safe Heaven Demand: Extreme Fear                                                                    [Updated Feb 14 at 5:14pm]
   The S&P 500 is 3.33% below its 125-day average. During the last two years, the S&P 500 has typically been above this average, so rapid declines like this indicate extreme levels of fear.
   (Last changed Jan 14 from a Fear rating)
```

![feargreed](https://user-images.githubusercontent.com/46355364/154037228-773886a2-dda8-4d7b-aad6-a6f53cbe24cb.png)



