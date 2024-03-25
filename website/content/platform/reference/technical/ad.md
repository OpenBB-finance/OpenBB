---
title: "ad"
description: "Learn about the Accumulation/Distribution Line and how it is interpreted  to detect trends in price movement. Explore its parameters, usage, and see code  examples."
keywords:
- Accumulation/Distribution Line
- On Balance Volume
- CLV
- divergence
- price
- trending upward
- flat
- flattening of the price
- Parameters
- data
- index
- offset
- Returns
- Examples
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical/ad - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the Accumulation/Distribution Line.

 Similar to the On Balance Volume (OBV).
 Sums the volume times +1/-1 based on whether the close is higher than the previous
 close. The Accumulation/Distribution indicator, however multiplies the volume by the
 close location value (CLV). The CLV is based on the movement of the issue within a
 single bar and can be +1, -1 or zero.


 The Accumulation/Distribution Line is interpreted by looking for a divergence in
 the direction of the indicator relative to price. If the Accumulation/Distribution
 Line is trending upward it indicates that the price may follow. Also, if the
 Accumulation/Distribution Line becomes flat while the price is still rising (or falling)
 then it signals an impending flattening of the price.


Examples
--------

```python
from openbb import obb
# Get the Accumulation/Distribution Line.
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')
ad_data = obb.technical.ad(data=stock_data.results, offset=0)
obb.technical.ad(data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | List of data to be used for the calculation. |  | False |
| index | str, optional | Index column name to use with `data`, by default "date". |  | False |
| offset | int, optional | Offset of the AD, by default 0. |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        The calculated data.
```

