---
title: vwap
description: Learn about the Volume Weighted Average Price (VWAP) and how it measures
  the average typical price by volume. Discover how it can be used with intraday charts
  to identify general direction. Explore Python examples using the OpenBB OBB package.
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

<HeadTitle title="technical /vwap - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

The Volume Weighted Average Price.

Measures the average typical price by volume.
It is typically used with intraday charts to identify general direction.
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
vwap_data = obb.technical.vwap(data=stock_data.results,anchor="D",offset=0)
```


---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | List of data to be used for the calculation. | None | False |
| index | str | Index column name to use with `data`, by default "date". | date | True |
| anchor | str | Anchor period to use for the calculation, by default "D".
See Timeseries Offset Aliases below for additional options:
https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#timeseries-offset-aliases | D | True |
| offset | int | Offset from the current period, by default 0. | 0 | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
The calculated data.
```

---

