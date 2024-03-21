---
title: "hma"
description: "Learn about the Hull Moving Average (HMA), a responsive and smooth moving  average indicator. Understand how to use the HMA, its parameters, and see examples  using the OBBject library."
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

<HeadTitle title="technical/hma - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the Hull Moving Average (HMA).

 Solves the age old dilemma of making a moving average more responsive to current
 price activity whilst maintaining curve smoothness.
 In fact the HMA almost eliminates lag altogether and manages to improve smoothing
 at the same time.


Examples
--------

```python
from openbb import obb
# Calculate HMA with historical stock data.
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')
hma_data = obb.technical.hma(data=stock_data.results, target='close', length=50, offset=0)
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
| length | int, optional | Number of periods for the HMA, by default 50. |  | False |
| offset | int, optional | Offset of the HMA, by default 0. |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        The calculated data.
```

