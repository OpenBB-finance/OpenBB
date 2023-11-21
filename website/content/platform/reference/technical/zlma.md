---
title: zlma
description: Learn about the zero lag exponential moving average (ZLEMA) and how it
  can be used to perform EMA calculations on de-lagged data. Explore the parameters
  and get examples of implementing ZLEMA in Python.
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

<HeadTitle title="technical /zlma - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

The zero lag exponential moving average (ZLEMA).

Created by John Ehlers and Ric Way. The idea is do a
regular exponential moving average (EMA) calculation but
on a de-lagged data instead of doing it on the regular data.
Data is de-lagged by removing the data from "lag" days ago
thus removing (or attempting to) the cumulative effect of
the moving average.
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
zlma_data = obb.technical.zlma(data=stock_data.results, target="close", length=50, offset=0)
```


---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | List of data to be used for the calculation. | None | False |
| target | str | Target column name. | close | True |
| index | str | Index column name to use with `data`, by default "date". | date | True |
| length | int | Number of periods to be used for the calculation, by default 50. | 50 | True |
| offset | int | Offset to be used for the calculation, by default 0. | 0 | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
The calculated data.
```

---

