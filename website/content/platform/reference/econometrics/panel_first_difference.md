---
title: panel_first_difference
description: Learn how to perform a first-difference estimate for panel data using
  this Python function. Understand the parameters and the object returned by the function.
keywords:
- panel data
- first-difference estimate
- perform
- parameters
- data
- dataset
- target column
- exogenous variables
- fit model
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics /panel_first_difference - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Perform a first-difference estimate for panel data.

```python wordwrap
obb.econometrics.panel_first_difference(data: Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], numpy.ndarray, Data, List[Data]], y_column: str, x_columns: List[str])
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | Input dataset. | None | False |
| y_column | str | Target column. | None | False |
| x_columns | List[str] | List of columns to use as exogenous variables. | None | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject with the fit model returned
```

---

