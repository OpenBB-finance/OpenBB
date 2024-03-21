---
title: "adx"
description: "Learn about ADX, a Welles Wilder style moving average of the Directional  Movement Index. Understand its calculation, interpretation, and usage with stock  data. Explore examples for implementation."
keywords:
- ADX
- Welles Wilder
- moving average
- Directional Movement Index
- trend
- calculation
- data
- index column
- length
- scalar value
- drift
- interpretation
- stock data
- historical data
- examples
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical/adx - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the Average Directional Index (ADX).

 The ADX is a Welles Wilder style moving average of the Directional Movement Index (DX).
 The values range from 0 to 100, but rarely get above 60. To interpret the ADX, consider
 a high number to be a strong trend, and a low number, a weak trend.


Examples
--------

```python
from openbb import obb
# Get the Average Directional Index (ADX).
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')
adx_data = obb.technical.adx(data=stock_data.results, length=50, scalar=100.0, drift=1)
obb.technical.adx(length=2, data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | List of data to be used for the calculation. |  | False |
| index | str, optional | Index column name to use with `data`, by default "date". |  | False |
| length | int, optional | Number of periods for the ADX, by default 50. |  | False |
| scalar | float, optional | Scalar value for the ADX, by default 100.0. |  | False |
| drift | int, optional | Drift value for the ADX, by default 1. |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        The calculated data.
```

