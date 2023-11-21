---
title: ols_regression
description: Learn how to perform OLS regression using statsmodels in Python. This
  documentation explains the parameters required and the object returned.
keywords:
- OLS regression
- statsmodels
- perform OLS regression
- data
- target column
- exogenous variables
- model
- results objects
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics /ols_regression - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Perform OLS regression.  This returns the model and results objects from statsmodels.

```python wordwrap
obb.econometrics.ols_regression(data: Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], numpy.ndarray, Data, List[Data]], y_column: str, x_columns: List[str])
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
OBBject with the results being model and results objects.
```

---

