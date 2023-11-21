---
title: quantile
description: Learn how to get the quantile from a time series data using a Python
  function. This documentation page provides information about the parameters and
  returns of the function.
keywords:
- quantile
- get quantile
- time series data
- target column
- window size
- quantile percentage
- python
- function
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="quantitative /quantile - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get Quantile.

```python wordwrap
obb.quantitative.quantile(data: Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], numpy.ndarray, Data, List[Data]], target: str, window: int, quantile_pct: float = 0.5)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | Time series data. | None | False |
| target | str | Target column name. | None | False |
| window | PositiveInt | Window size. | None | False |
| quantile_pct | NonNegativeFloat | Quantile percentage, by default 0.5 | 0.5 | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
Quantile.
```

---

