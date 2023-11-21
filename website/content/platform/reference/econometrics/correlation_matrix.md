---
title: correlation_matrix
description: Learn how to get the correlation matrix of an input dataset using Python.
  Find information on the parameters and return value of the function.
keywords:
- correlation matrix
- input dataset
- Python
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics /correlation_matrix - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the correlation matrix of an input dataset.

```python wordwrap
obb.econometrics.correlation_matrix(data: Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], numpy.ndarray, Data, List[Data]])
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | Input dataset. | None | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
Correlation matrix.
```

---

