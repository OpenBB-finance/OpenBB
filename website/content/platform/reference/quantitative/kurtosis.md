---
title: kurtosis
description: Learn how to calculate Kurtosis using the provided time series data in
  Python.
keywords:
- Kurtosis
- data
- time series data
- target column name
- window size
- OBBject
- Python
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="quantitative /kurtosis - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the Kurtosis.

```python wordwrap
obb.quantitative.kurtosis(data: Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], numpy.ndarray, Data, List[Data]], target: str, window: int)
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
Kurtosis.
```

---

