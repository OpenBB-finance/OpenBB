---
title: sortino_ratio
description: Learn how to calculate and use the Sortino Ratio in Python. Understand
  the methodology, terminology, and parameters involved. Compare Sortino ratio to
  Sharpe ratio and adjust it accordingly. Enhance your risk management strategies
  with Sortino ratio.
keywords:
- Sortino Ratio
- Sortino method
- Sortino terminology
- Sortino ratio calculation
- Sortino ratio parameters
- Sortino ratio target return
- Sortino ratio window size
- Sortino ratio adjusted
- Sortino ratio vs Sharpe ratio
- Sortino ratio Python
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="quantitative /sortino_ratio - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get Sortino Ratio.

For method & terminology see:
http://www.redrockcapital.com/Sortino__A__Sharper__Ratio_Red_Rock_Capital.pdf

```python wordwrap
obb.quantitative.sortino_ratio(data: Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], numpy.ndarray, Data, List[Data]], target: str, target_return: float = 0.0, window: int = 252, adjusted: bool = False)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | Time series data. | None | False |
| target | str | Target column name. | None | False |
| target_return | float | Target return, by default 0.0 | 0.0 | True |
| window | PositiveInt | Window size, by default 252 | 252 | True |
| adjusted | bool | Adjust sortino ratio to compare it to sharpe ratio, by default False | False | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
Sortino ratio.
```

---

