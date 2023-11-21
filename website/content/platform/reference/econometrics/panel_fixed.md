---
title: panel_fixed
description: Learn about the one- and two-way fixed effects estimator for panel data
  analysis. Explore the parameters and returns of this function for panel data regression
  and modeling.
keywords:
- panel data
- fixed effects estimator
- panel data analysis
- two-way fixed effects
- panel data regression
- panel data modeling
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics /panel_fixed - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

One- and two-way fixed effects estimator for panel data.

```python wordwrap
obb.econometrics.panel_fixed(data: Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], numpy.ndarray, Data, List[Data]], y_column: str, x_columns: List[str])
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

