---
title: "vwap"
description: "Learn about the Volume Weighted Average Price (VWAP) and how it measures  the average typical price by volume. Discover how it can be used with intraday charts  to identify general direction. Explore Python examples using the OpenBB OBB package."
keywords:
- Volume Weighted Average Price
- average typical price by volume
- intraday charts
- general direction identification
- timeseries offset aliases
- python examples
- openbb obb package
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical/vwap - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the Volume Weighted Average Price (VWAP).

 Measures the average typical price by volume.
 It is typically used with intraday charts to identify general direction.
 It helps to understand the true average price factoring in the volume of transactions,
 and serves as a benchmark for assessing the market's direction over short periods, such as a single trading day.


Examples
--------

```python
from openbb import obb
# Get the Volume Weighted Average Price (VWAP).
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')
vwap_data = obb.technical.vwap(data=stock_data.results, anchor='D', offset=0)
obb.technical.vwap(data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | List of data to be used for the calculation. |  | False |
| index | str, optional | Index column name to use with `data`, by default "date". |  | False |
| anchor | str, optional | Anchor period to use for the calculation, by default "D". |  | False |
| https | //pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#timeseries-offset-aliases | offset : int, optional |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        The calculated data.
```

