---
title: sharpe_ratio
description: Learn how to calculate the Sharpe Ratio using time series data in Python.
  Understand the parameters required, including the target column, risk-free rate,
  and window size. Enhance your investment analysis by computing the Sharpe ratio.
keywords:
- Sharpe Ratio
- time series data
- target column
- risk-free rate
- window size
- python
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="quantitative /sharpe_ratio - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get Sharpe Ratio.

```python wordwrap
obb.quantitative.sharpe_ratio(data: Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], numpy.ndarray, Data, List[Data]], target: str, rfr: float = 0.0, window: int = 252)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | Time series data. | None | False |
| target | str | Target column name. | None | False |
| rfr | float | Risk-free rate, by default 0.0 | 0.0 | True |
| window | PositiveInt | Window size, by default 252 | 252 | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
Sharpe ratio.
```

---

