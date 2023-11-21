---
title: residual_autocorrelation
description: Perform Breusch-Godfrey Lagrange Multiplier tests for residual autocorrelation
  in a Python function. Learn about the parameters used and the returned object.
keywords:
- Breusch-Godfrey Lagrange Multiplier tests
- residual autocorrelation
- Python function
- parameter description
- function returns
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics /residual_autocorrelation - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Perform Breusch-Godfrey Lagrange Multiplier tests for residual autocorrelation.

```python wordwrap
obb.econometrics.residual_autocorrelation(data: Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], numpy.ndarray, Data, List[Data]], y_column: str, x_columns: List[str], lags: int = 1)
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
| lags | PositiveInt | Number of lags to use in the test. | 1 | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject with the results being the score from the test.
```

---

