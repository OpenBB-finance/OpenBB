---
title: panel_random_effects
description: Learn how to perform One-way Random Effects model for panel data using
  a Python function. This function takes an input dataset, target column, and exogenous
  variables as parameters and returns the fit model.
keywords:
- One-way Random Effects model
- panel data
- perform
- Python function
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics /panel_random_effects - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Perform One-way Random Effects model for panel data.

```python wordwrap
obb.econometrics.panel_random_effects(data: Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], numpy.ndarray, Data, List[Data]], y_column: str, x_columns: List[str])
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

