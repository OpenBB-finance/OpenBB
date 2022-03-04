ta hma - Hull Moving Average

The Hull Moving Average (HMA), developed by Alan Hull, is an extremely fast and smooth moving average. In fact, the HMA almost eliminates lag altogether and manages to improve smoothing at the same time.

A longer period HMA may be used to identify trend. If the HMA is rising, the prevailing trend is rising, indicating it may be better to enter long positions. If the HMA is falling, the prevailing trend is also falling, indicating it may be better to enter short positions.

A shorter period HMA may be used for entry signals in the direction of the prevailing trend. A long entry signal, when the prevailing trend is rising, occurs when the HMA turns up and a short entry signal, when the prevailing trend is falling, occurs when the HMA turns down.

Calculation

Calculate a Weighted Moving Average with period n / 2 and multiply it by 2
Calculate a Weighted Moving Average for period n and subtract if from step 1
Calculate a Weighted Moving Average with period sqrt(n) using the data from step 2

HMA= WMA(2*WMA(n/2) − WMA(n)),sqrt(n))

https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/hull-moving-average

![Screen Shot 2022-02-24 at 10 02 12 PM](https://user-images.githubusercontent.com/85772166/155662979-981a635b-cd3e-40e4-8b5c-2b154be5e901.png)

```
/ta hma ticker: GME
```

![Screen Shot 2022-02-24 at 10 03 43 PM](https://user-images.githubusercontent.com/85772166/155663131-48d9cf5a-119f-45c2-9d30-915c371431a3.png)
