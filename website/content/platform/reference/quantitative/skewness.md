---
title: skewness
description: Learn how to calculate skewness using the 'Get Skewness' function. This
  Python function is used to calculate the skewness of time series data. Understand
  the parameters such as data, target column, and window size, and the return type
  of the function. Perform data analysis with this powerful function.
keywords:
- skewness
- get skewness
- time series data
- target column
- window size
- function parameters
- return type
- Python
- data analysis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="quantitative /skewness - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get Skewness.

```python wordwrap
obb.quantitative.skewness(data: Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], numpy.ndarray, Data, List[Data]], target: str, window: int)
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
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
Skewness.
```

---

