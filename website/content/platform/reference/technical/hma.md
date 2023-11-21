---
title: hma
description: Learn about the Hull Moving Average (HMA), a responsive and smooth moving
  average indicator. Understand how to use the HMA, its parameters, and see examples
  using the OBBject library.
keywords:
- Hull Moving Average
- moving average
- lag
- smoothing
- data
- target column
- index column
- length
- offset
- OBBject
- examples
- openbb
- equity
- price
- historical
- symbol
- start date
- provider
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical /hma - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

The Hull Moving Average.

Solves the age old dilemma of making a moving average more responsive to current
price activity whilst maintaining curve smoothness.
In fact the HMA almost eliminates lag altogether and manages to improve smoothing
at the same time.
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
hma_data = obb.technical.hma(data=stock_data.results,target="close",length=50,offset=0)
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
| length | int | Number of periods for the HMA, by default 50. | 50 | True |
| offset | int | Offset of the HMA, by default 0. | 0 | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
The calculated data.
```

---

