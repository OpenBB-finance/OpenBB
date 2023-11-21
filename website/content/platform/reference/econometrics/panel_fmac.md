---
title: panel_fmac
description: Learn how to use the Fama-MacBeth estimator for panel data analysis in
  Python. Understand the parameters required and how to specify the input dataset
  and target column. Explore how this function can help you analyze panel data by
  incorporating exogenous variables.
keywords:
- Fama-MacBeth estimator
- panel data analysis
- Python function
- parameters
- exogenous variables
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics /panel_fmac - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Fama-MacBeth estimator for panel data.

```python wordwrap
obb.econometrics.panel_fmac(data: Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], numpy.ndarray, Data, List[Data]], y_column: str, x_columns: List[str])
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

