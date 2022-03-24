ta-vol ad - Accumulation/Distribution Line

The Accumulation/Distribution Line is similar to the On Balance Volume (OBV), which sums the volume times +1/-1 based on whether the close is higher than the previous close. The Accumulation/Distribution indicator, however multiplies the volume by the close location value (CLV). The CLV is based on the movement of the issue within a single bar and can be +1, -1 or zero. The Accumulation/Distribution Line is interpreted by looking for a divergence in the direction of the indicator relative to price. If the Accumulation/Distribution Line is trending upward it indicates that the price may follow. Also, if the Accumulation/Distribution Line becomes flat while the price is still rising (or falling) then it signals an impending flattening of the price.

![Screen Shot 2022-03-17 at 8 04 52 PM](https://user-images.githubusercontent.com/85772166/158929810-194af5f8-7428-4366-ba4e-791911abb1fe.png)

```
/ta-vol ad ticker: TSLA interval: 15 past_days: 60 heiken_candles: True
```

![Screen Shot 2022-03-17 at 9 05 25 PM](https://user-images.githubusercontent.com/85772166/158935496-1d4b3216-dd28-4fcf-ba72-3e291d506677.png)
