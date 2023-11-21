---
title: causality
description: Learn how to perform a Granger causality test to determine if X causes
  y. Understand the parameters and the results returned by the test.
keywords:
- Granger causality test
- causality
- perform
- determine
- exogenous variables
- lags
- data
- target column
- results
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics /causality - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Perform Granger causality test to determine if X "causes" y.

```python wordwrap
obb.econometrics.causality(data: Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], numpy.ndarray, Data, List[Data]], y_column: str, x_column: str, lag: int = 3)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | Input dataset. | None | False |
| y_column | str | Target column. | None | False |
| x_column | str | Columns to use as exogenous variables. | None | False |
| lag | PositiveInt | Number of lags to use in the test. | 3 | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject with the results being the score from the test.
```

---

