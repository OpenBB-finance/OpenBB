---
title: "obv"
description: "Learn about On Balance Volume (OBV), a cumulative volume indicator that  helps to interpret price moves, identify trends, and determine market trends. This  documentation page provides an explanation of how OBV works, its parameters, and  a Python example."
keywords:
- On Balance Volume
- OBV
- cumulative volume
- up and down volume
- running total
- price moves
- non-confirmed move
- rising peaks
- falling troughs
- strong trend
- flat OBV
- interpret OBV
- how to use OBV
- Python example
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical/obv - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the On Balance Volume (OBV).

 Is a cumulative total of the up and down volume. When the close is higher than the
 previous close, the volume is added to the running total, and when the close is
 lower than the previous close, the volume is subtracted from the running total.

 To interpret the OBV, look for the OBV to move with the price or precede price moves.
 If the price moves before the OBV, then it is a non-confirmed move. A series of rising peaks,
 or falling troughs, in the OBV indicates a strong trend. If the OBV is flat, then the market
 is not trending.


Examples
--------

```python
from openbb import obb
# Get the On Balance Volume (OBV).
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')
obv_data = obb.technical.obv(data=stock_data.results, offset=0)
obb.technical.obv(data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | List of data to apply the indicator to. |  | False |
| index | str, optional | Index column name, by default "date" |  | False |
| offset | int, optional | How many periods to offset the result, by default 0. |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        List of data with the indicator applied.
```

