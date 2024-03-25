---
title: "unit_root"
description: "Learn how to use the Augmented Dickey-Fuller unit root test to check  for stationarity in time series data. This function takes in an input dataset and  performs the test on specified data columns. The regression type can be customized,  and the function returns the results."
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

<HeadTitle title="econometrics/unit_root - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Perform Augmented Dickey-Fuller (ADF) unit root test.

 The ADF test is a popular method for testing the presence of a unit root in a time series.
 A unit root indicates that the series may be non-stationary, meaning its statistical properties such as mean,
 variance, and autocorrelation can change over time. The presence of a unit root suggests that the time series might
 be influenced by a random walk process, making it unpredictable and challenging for modeling and forecasting.
 The 'regression' parameter allows you to specify the model used in the test: 'c' for a constant term,
 'ct' for a constant and trend term, and 'ctt' for a constant, linear, and quadratic trend.
 This flexibility helps tailor the test to the specific characteristics of your data, providing a more accurate
 assessment of its stationarity.


Examples
--------

```python
from openbb import obb
# Perform Augmented Dickey-Fuller (ADF) unit root test.
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()
obb.econometrics.unit_root(data=stock_data, column="close")
obb.econometrics.unit_root(data=stock_data, column="close", regression="ct")
obb.econometrics.unit_root(column='close', data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | Input dataset. |  | False |
| column | str | Data columns to check unit root |  | False |
| regression | Literal["c", "ct", "ctt"] | Regression type to use in the test.  Either "c" for constant only, "ct" for constant and trend, or "ctt" for |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : Data
        OBBject with the results being the score from the test.
```

