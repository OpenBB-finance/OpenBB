---
title: candles
description: This page is a comprehensive guide on how to display candle data for
  different technical analysis indicators like Bollinger Bands, Accumulation/Distribution
  Indicator, Commodity Channel Index, Exponential Moving Average, On Balance Volume,
  Relative Strength Index, Simple Moving Average, and Volume Weighted Average Price.
keywords:
- candle data
- technical analysis
- data visualization
- Bollinger Bands
- Accumulation/Distribution Indicator
- Commodity Channel Index
- Exponential Moving Average
- On Balance Volume
- Relative Strength Index
- Simple Moving Average
- Volume Weighted Average Price
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forex/oanda/candles - Reference | OpenBB Terminal Docs" />

Display Candle Data

### Usage

```python
candles [-g GRANULARITY] [-l CANDLECOUNT] [-a] [-b] [-c] [-e] [-o] [-r] [-s] [-v]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| granularity | The timeframe to get for the candle chart (Seconds: S5, S10, S15, S30 Minutes: M1, M2, M4, M5, M10, M15, M30 Hours: H1, H2, H3, H4, H6, H8, H12 Day (default): D, Week: W Month: M | D | True | None |
| candlecount | The number of candles to retrieve. Default:180 | 180 | True | None |
| ad | Adds ad (Accumulation/Distribution Indicator) to the chart | False | True | None |
| bbands | Adds Bollinger Bands to the chart | False | True | None |
| cci | Adds cci (Commodity Channel Index) to the chart | False | True | None |
| ema | Adds ema (Exponential Moving Average) to the chart | False | True | None |
| obv | Adds obv (On Balance Volume) to the chart | False | True | None |
| rsi | Adds rsi (Relative Strength Index) to the chart | False | True | None |
| sma | Adds sma (Simple Moving Average) to the chart | False | True | None |
| vwap | Adds vwap (Volume Weighted Average Price) to the chart | False | True | None |

---
