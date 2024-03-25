---
title: "zlma"
description: "Learn about the zero lag exponential moving average (ZLEMA) and how it  can be used to perform EMA calculations on de-lagged data. Explore the parameters  and get examples of implementing ZLEMA in Python."
keywords:
- zero lag exponential moving average
- ZLEMA
- EMA calculation
- de-lagged data
- moving average
- lagged data
- cumulative effect
- parameters
- target column
- index column
- length
- offset
- calculation
- calculated data
- example
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical/zlma - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the zero lag exponential moving average (ZLEMA).

 Created by John Ehlers and Ric Way. The idea is do a
 regular exponential moving average (EMA) calculation but
 on a de-lagged data instead of doing it on the regular data.
 Data is de-lagged by removing the data from "lag" days ago
 thus removing (or attempting to) the cumulative effect of
 the moving average.


Examples
--------

```python
from openbb import obb
# Get the Chande Momentum Oscillator.
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')
zlma_data = obb.technical.zlma(data=stock_data.results, target='close', length=50, offset=0)
obb.technical.zlma(length=2, data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
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

