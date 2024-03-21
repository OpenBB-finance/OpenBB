---
title: "normality"
description: "Learn about normality statistics and their significance in data analysis.  Discover different techniques such as kurtosis, skewness, Jarque-Bera, Shapiro-Wilk,  and Kolmogorov-Smirnov for evaluating normality in time series data. Explore how  these tests can help determine if a data sample follows a normal distribution."
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

<HeadTitle title="quantitative/normality - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get Normality Statistics.

 - **Kurtosis**: whether the kurtosis of a sample differs from the normal distribution.
 - **Skewness**: whether the skewness of a sample differs from the normal distribution.
 - **Jarque-Bera**: whether the sample data has the skewness and kurtosis matching a normal distribution.
 - **Shapiro-Wilk**: whether a random sample comes from a normal distribution.
 - **Kolmogorov-Smirnov**: whether two underlying one-dimensional probability distributions differ.


Examples
--------

```python
from openbb import obb
# Get Normality Statistics.
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()
obb.quantitative.normality(data=stock_data, target='close')
obb.quantitative.normality(target='close', data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}, {'date': '2023-01-07', 'open': 128.33, 'high': 140.0, 'low': 116.67, 'close': 134.17, 'volume': 11666.67}, {'date': '2023-01-08', 'open': 125.71, 'high': 137.14, 'low': 114.29, 'close': 131.43, 'volume': 11428.57}, {'date': '2023-01-09', 'open': 123.75, 'high': 135.0, 'low': 112.5, 'close': 129.38, 'volume': 11250.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | Time series data. |  | False |
| target | str | Target column name. |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : NormalityModel
        Normality tests summary. See qa_models.NormalityModel for details.
```

