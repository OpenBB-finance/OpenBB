---
title: unitroot_test
description: Learn about the Unit Root Test function in Python, including the Augmented
  Dickey-Fuller test and the Kwiatkowski-Phillips-Schmidt-Shin test. Explore the parameters,
  such as data, target, fuller_reg, and kpss_reg, and understand how to interpret
  the unit root tests summary.
keywords:
- Unit Root Test
- Augmented Dickey-Fuller test
- Kwiatkowski-Phillips-Schmidt-Shin test
- data
- target
- fuller_reg
- kpss_reg
- Time series data
- unit root tests
- unit root tests summary
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="quantitative /unitroot_test - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get Unit Root Test.

Augmented Dickey-Fuller test for unit root.
Kwiatkowski-Phillips-Schmidt-Shin test for unit root.

```python wordwrap
obb.quantitative.unitroot_test(data: Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], numpy.ndarray, Data, List[Data]], target: str, fuller_reg: Literal[str] = c, kpss_reg: Literal[str] = c)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | Time series data. | None | False |
| target | str | Target column name. | None | False |
| fuller_reg | Literal["c", "ct", "ctt", "nc", "c"] | Regression type for ADF test. | c | True |
| kpss_reg | Literal["c", "ct"] | Regression type for KPSS test. | c | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
Unit root tests summary.
```

---

