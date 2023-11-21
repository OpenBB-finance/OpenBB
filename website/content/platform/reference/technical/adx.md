---
title: adx
description: Learn about ADX, a Welles Wilder style moving average of the Directional
  Movement Index. Understand its calculation, interpretation, and usage with stock
  data. Explore examples for implementation.
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

<HeadTitle title="technical /adx - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

ADX.

The ADX is a Welles Wilder style moving average of the Directional Movement Index (DX).
The values range from 0 to 100, but rarely get above 60. To interpret the ADX, consider
a high number to be a strong trend, and a low number, a weak trend.
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
adx_data = obb.technical.adx(data=stock_data.results,length=50,scalar=100.0,drift=1)
```


---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | List of data to be used for the calculation. | None | False |
| index | str | Index column name to use with `data`, by default "date". | date | True |
| length | int | Number of periods for the ADX, by default 50. | 50 | True |
| scalar | float | Scalar value for the ADX, by default 100.0. | 100.0 | True |
| drift | int | Drift value for the ADX, by default 1. | 1 | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
The calculated data.
```

---

