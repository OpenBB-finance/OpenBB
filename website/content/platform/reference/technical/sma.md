---
title: "sma"
description: "Learn about the Simple Moving Average and how it can be used to smooth  data, eliminate noise, and identify trends. Gain insights into the simple form of  moving averages, equal weighting, responsiveness to changes, and filtering data.  Understand the parameters involved in the calculation, such as length and offset."
keywords:
- Simple Moving Average
- moving averages
- smoothing data
- identify trends
- noise elimination
- simplest form of moving average
- equal weight
- responsive to changes
- filtering data
- data calculation
- length parameter
- offset parameter
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical/sma - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the Simple Moving Average (SMA).

 Moving Averages are used to smooth the data in an array to
 help eliminate noise and identify trends. The Simple Moving Average is literally
 the simplest form of a moving average. Each output value is the average of the
 previous n values. In a Simple Moving Average, each value in the time period carries
 equal weight, and values outside of the time period are not included in the average.
 This makes it less responsive to recent changes in the data, which can be useful for
 filtering out those changes.


Examples
--------

```python
from openbb import obb
# Get the Chande Momentum Oscillator.
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')
sma_data = obb.technical.sma(data=stock_data.results, target='close', length=50, offset=0)
obb.technical.sma(length=2, data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
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
| offset | int, optional | Offset from the current period, by default 0. |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        The calculated data.
```

