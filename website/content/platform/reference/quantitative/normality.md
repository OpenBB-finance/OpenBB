---
title: normality
description: Learn about normality statistics and their significance in data analysis.
  Discover different techniques such as kurtosis, skewness, Jarque-Bera, Shapiro-Wilk,
  and Kolmogorov-Smirnov for evaluating normality in time series data. Explore how
  these tests can help determine if a data sample follows a normal distribution.
keywords:
- normality statistics
- kurtosis
- skewness
- Jarque-Bera
- Shapiro-Wilk
- Kolmogorov-Smirnov
- time series data
- target column
- normality tests
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="quantitative /normality - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get Normality Statistics.

- **Kurtosis**: whether the kurtosis of a sample differs from the normal distribution.
- **Skewness**: whether the skewness of a sample differs from the normal distribution.
- **Jarque-Bera**: whether the sample data has the skewness and kurtosis matching a normal distribution.
- **Shapiro-Wilk**: whether a random sample comes from a normal distribution.
- **Kolmogorov-Smirnov**: whether two underlying one-dimensional probability distributions differ.

```python wordwrap
obb.quantitative.normality(data: Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], numpy.ndarray, Data, List[Data]], target: str)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | Time series data. | None | False |
| target | str | Target column name. | None | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
Normality tests summary. See qa_models.NormalityModel for details.
```

---

