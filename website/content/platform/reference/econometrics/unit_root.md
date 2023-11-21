---
title: unit_root
description: Learn how to use the Augmented Dickey-Fuller unit root test to check
  for stationarity in time series data. This function takes in an input dataset and
  performs the test on specified data columns. The regression type can be customized,
  and the function returns the results.
keywords:
- Augmented Dickey-Fuller
- unit root test
- data
- data columns
- unit root
- regression
- constant
- trend
- trend-squared
- results
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics /unit_root - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Perform Augmented Dickey-Fuller unit root test.

```python wordwrap
obb.econometrics.unit_root(data: Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], numpy.ndarray, Data, List[Data]], column: str, regression: Literal[str] = c)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | Input dataset. | None | False |
| column | str | Data columns to check unit root | None | False |
| regression | Literal["c", "ct", "ctt"] | Regression type to use in the test.  Either "c" for constant only, "ct" for constant and trend, or "ctt" for
constant, trend, and trend-squared. | c | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject with the results being the score from the test.
```

---

