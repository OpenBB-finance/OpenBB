---
title: "cci"
description: "Learn about the Commodity Channel Index (CCI) and how it can be used  to detect market trends, overbought or oversold conditions, and price divergence.  This documentation provides an overview of the CCI, its parameters, and its calculation,  along with an explanation of the CCI data it returns."
keywords:
- Commodity Channel Index
- CCI
- market trends
- trading range
- overbought
- oversold
- price divergence
- price correction
- data
- index column
- length
- scalar
- CCI calculation
- CCI data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical/cci - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the Commodity Channel Index (CCI).

 The CCI is designed to detect beginning and ending market trends.
 The range of 100 to -100 is the normal trading range. CCI values outside of this
 range indicate overbought or oversold conditions. You can also look for price
 divergence in the CCI. If the price is making new highs, and the CCI is not,
 then a price correction is likely.


Examples
--------

```python
from openbb import obb
# Get the Commodity Channel Index (CCI).
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')
cci_data = obb.technical.cci(data=stock_data.results, length=14, scalar=0.015)
obb.technical.cci(length=2, data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | The data to use for the CCI calculation. |  | False |
| index | str, optional | Index column name to use with `data`, by default "date". |  | False |
| length | PositiveInt, optional | The length of the CCI, by default 14. |  | False |
| scalar | PositiveFloat, optional | The scalar of the CCI, by default 0.015. |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        The CCI data.
```

