---
title: omega_ratio
description: Learn how to calculate the Omega Ratio using a Python function. This
  documentation page provides information on the parameters required, including time
  series data, target column, and threshold. The function returns a list of Omega
  ratios.
keywords:
- Omega Ratio
- calculate Omega Ratio
- Python function
- documentation page
- time series data
- target column
- threshold
- OmegaModel
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="quantitative /omega_ratio - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the Omega Ratio.

```python wordwrap
obb.quantitative.omega_ratio(data: Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], numpy.ndarray, Data, List[Data]], target: str, threshold_start: float = 0.0, threshold_end: float = 1.5)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | Time series data. | None | False |
| target | str | Target column name. | None | False |
| threshold_start | float | Start threshold, by default 0.0 | 0.0 | True |
| threshold_end | float | End threshold, by default 1.5 | 1.5 | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
Omega ratios.
```

---

