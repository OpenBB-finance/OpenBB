---
title: summary
description: Learn how to get summary statistics on time series data using Python.
  This documentation page provides information on the parameters and return value
  of the function.
keywords:
- summary statistics
- get summary statistics
- summary table
- python
- time series data
- target column
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="quantitative /summary - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get Summary Statistics.

```python wordwrap
obb.quantitative.summary(data: Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], numpy.ndarray, Data, List[Data]], target: str)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | Time series data. | None | False |
| target | str | Target column name. | None | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
Summary table.
```

---

