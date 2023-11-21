---
title: autocorrelation
description: Learn how to perform the Durbin-Watson test for autocorrelation in Python.
  Understand the parameters and return value of the function, and how to use exogenous
  variables in the analysis. This documentation provides a detailed explanation.
keywords:
- Durbin-Watson test
- autocorrelation
- Python
- data analysis
- exogenous variables
- parameter
- return
- documentation
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics /autocorrelation - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Perform Durbin-Watson test for autocorrelation.

```python wordwrap
obb.econometrics.autocorrelation(data: Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], numpy.ndarray, Data, List[Data]], y_column: str, x_columns: List[str])
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
OBBject with the results being the score from the test.
```

---

