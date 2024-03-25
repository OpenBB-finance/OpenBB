---
title: "rsi"
description: "Learn about Relative Strength Index (RSI) and how to calculate it. Understand  its interpretation as an overbought/oversold indicator and its relevance in identifying  price movements and reversals. Explore the various parameters involved in the RSI  calculation with practical examples."
keywords:
- Relative Strength Index
- RSI
- oversold indicator
- overbought indicator
- divergence
- price movements
- reversal
- parameters
- data
- target
- index
- length
- scalar
- drift
- examples
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical/rsi - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the Relative Strength Index (RSI).

 RSI calculates a ratio of the recent upward price movements to the absolute price
 movement. The RSI ranges from 0 to 100.
 The RSI is interpreted as an overbought/oversold indicator when
 the value is over 70/below 30. You can also look for divergence with price. If
 the price is making new highs/lows, and the RSI is not, it indicates a reversal.


Examples
--------

```python
from openbb import obb
# Get the Relative Strength Index (RSI).
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')
rsi_data = obb.technical.rsi(data=stock_data.results, target='close', length=14, scalar=100.0, drift=1)
obb.technical.rsi(length=2, data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | The data to use for the RSI calculation. |  | False |
| target | str | Target column name. |  | False |
| index | str, optional | Index column name to use with `data`, by default "date" |  | False |
| length | int, optional | The length of the RSI, by default 14 |  | False |
| scalar | float, optional | The scalar to use for the RSI, by default 100.0 |  | False |
| drift | int, optional | The drift to use for the RSI, by default 1 |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        The RSI data.
```

