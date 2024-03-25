---
title: "residual_autocorrelation"
description: "Perform Breusch-Godfrey Lagrange Multiplier tests for residual autocorrelation  in a Python function. Learn about the parameters used and the returned object."
keywords:
- Breusch-Godfrey Lagrange Multiplier tests
- residual autocorrelation
- Python function
- parameter description
- function returns
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics/residual_autocorrelation - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Perform Breusch-Godfrey Lagrange Multiplier tests for residual autocorrelation.

 The Breusch-Godfrey Lagrange Multiplier test is a sophisticated tool for uncovering autocorrelation within the
 residuals of a regression model. Autocorrelation in residuals can indicate that a model fails to capture some
 aspect of the underlying data structure, possibly leading to biased or inefficient estimates.
 By specifying the number of lags, you can control the depth of the test to check for autocorrelation,
 allowing for a tailored analysis that matches the specific characteristics of your data.
 This test is particularly valuable in econometrics and time-series analysis, where understanding the independence
 of errors is crucial for model validity.


Examples
--------

```python
from openbb import obb
# Perform Breusch-Godfrey Lagrange Multiplier tests for residual autocorrelation.
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()
obb.econometrics.residual_autocorrelation(data=stock_data, y_column="close", x_columns=["open", "high", "low"])
obb.econometrics.residual_autocorrelation(y_column='close', x_columns=['open', 'high', 'low'], data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | Input dataset. |  | False |
| y_column | str | Target column. |  | False |
| x_columns | List[str] | List of columns to use as exogenous variables. |  | False |
| lags | PositiveInt | Number of lags to use in the test. |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : Data
        OBBject with the results being the score from the test.
```

