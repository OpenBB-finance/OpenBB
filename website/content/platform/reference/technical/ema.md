---
title: ema
description: Learn how to calculate the Exponential Moving Average (EMA) in Python
  using the openbb library. Understand its benefits as a cumulative calculation and
  how it maintains data responsiveness. Find details on parameters like data, target
  column, index column, length, and offset. Get code examples to implement EMA calculations
  in your projects.
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

<HeadTitle title="technical /ema - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Exponential Moving Average.

EMA is a cumulative calculation, including all data. Past values have
a diminishing contribution to the average, while more recent values have a greater
contribution. This method allows the moving average to be more responsive to changes
in the data.
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
ema_data = obb.technical.ema(data=stock_data.results,target="close",length=50,offset=0)
```


---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | The data to use for the calculation. | None | False |
| target | str | Target column name. | close | True |
| index | str | Index column name to use with `data`, by default "date" | date | True |
| length | int | The length of the calculation, by default 50. | 50 | True |
| offset | int | The offset of the calculation, by default 0. | 0 | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
The calculated data.
```

---

