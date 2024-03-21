---
title: "ema"
description: "Learn how to calculate the Exponential Moving Average (EMA) in Python  using the openbb library. Understand its benefits as a cumulative calculation and  how it maintains data responsiveness. Find details on parameters like data, target  column, index column, length, and offset. Get code examples to implement EMA calculations  in your projects."
keywords:
- Exponential Moving Average
- EMA
- cumulative calculation
- moving average
- data responsiveness
- parameters
- target column
- index column
- length
- offset
- calculated data
- examples
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical/ema - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the Exponential Moving Average (EMA).

 EMA is a cumulative calculation, including all data. Past values have
 a diminishing contribution to the average, while more recent values have a greater
 contribution. This method allows the moving average to be more responsive to changes
 in the data.


Examples
--------

```python
from openbb import obb
# Get the Exponential Moving Average (EMA).
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')
ema_data = obb.technical.ema(data=stock_data.results, target='close', length=50, offset=0)
obb.technical.ema(length=2, data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | The data to use for the calculation. |  | False |
| target | str | Target column name. |  | False |
| index | str, optional | Index column name to use with `data`, by default "date" |  | False |
| length | int, optional | The length of the calculation, by default 50. |  | False |
| offset | int, optional | The offset of the calculation, by default 0. |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        The calculated data.
```

