---
title: ols_regression_summary
description: Learn how to perform OLS regression using statsmodels in Python. Explore
  the parameters and returns of the function, including the data, target column, exogenous
  variables, and summary object.
keywords:
- OLS regression
- statsmodels
- summary object
- parameters
- data
- y_column
- x_columns
- exogenous variables
- returns
- OBBject
- model
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics /ols_regression_summary - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Perform OLS regression. This returns the summary object from statsmodels.

```python wordwrap
obb.econometrics.ols_regression_summary(data: Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], numpy.ndarray, Data, List[Data]], y_column: str, x_columns: List[str])
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
OBBject with the results being summary object.
```

---

