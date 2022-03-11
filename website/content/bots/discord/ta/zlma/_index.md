ta zlma - Zero Lag Exponential Moving Average

The Zero Lag EMA is a Trend indicator, and the primary aim is to eliminate the inherent lag associated with all trend-following indicators, which average a price over time.

```
Lag = (Period-1)/2

Ema Data = {Data+(Data-Data(Lag days ago)) 

ZLEMA = EMA(EmaData,Period) 
```

![Screen Shot 2022-02-24 at 10 14 12 PM](https://user-images.githubusercontent.com/85772166/155664169-fc54dee7-3668-4434-8e28-c2aec9f35bdf.png)

```
/ta zlma ticker: NFLX
```

![Screen Shot 2022-02-24 at 10 15 42 PM](https://user-images.githubusercontent.com/85772166/155664335-d9132540-57d9-4b5c-b444-66db38e4ba0c.png)
