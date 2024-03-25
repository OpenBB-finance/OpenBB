---
title: "bbands"
description: "Learn about Bollinger Bands, a popular trading indicator used to identify  volatility, overbought or oversold conditions, support and resistance levels, and  price targets. Understand how they work, their parameters, and how to use them effectively  in your trading strategy."
keywords:
- Bollinger Bands
- trading indicator
- volatility
- buy or sell signals
- overbought or oversold conditions
- support or resistance level
- price targets
- moving average
- standard deviation
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical/bbands - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the Bollinger Bands.

 Consist of three lines. The middle band is a simple moving average (generally 20
 periods) of the typical price (TP). The upper and lower bands are F standard
 deviations (generally 2) above and below the middle band.
 The bands widen and narrow when the volatility of the price is higher or lower,
 respectively.

 Bollinger Bands do not, in themselves, generate buy or sell signals;
 they are an indicator of overbought or oversold conditions. When the price is near the
 upper or lower band it indicates that a reversal may be imminent. The middle band
 becomes a support or resistance level. The upper and lower bands can also be
 interpreted as price targets. When the price bounces off of the lower band and crosses
 the middle band, then the upper band becomes the price target.


Examples
--------

```python
from openbb import obb
# Get the Chande Momentum Oscillator.
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')
bbands_data = obb.technical.bbands(data=stock_data.results, target='close', length=50, std=2, mamode='sma')
obb.technical.bbands(length=2, data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | List of data to be used for the calculation. |  | False |
| target | str | Target column name. |  | False |
| index | str, optional | Index column name to use with `data`, by default "date". |  | False |
| length | int, optional | Number of periods to be used for the calculation, by default 50. |  | False |
| std | NonNegativeFloat, optional | Standard deviation to be used for the calculation, by default 2. |  | False |
| mamode | Literal["sma", "ema", "wma", "rma"], optional | Moving average mode to be used for the calculation, by default "sma". |  | False |
| offset | int, optional | Offset to be used for the calculation, by default 0. |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        The calculated data.
```

