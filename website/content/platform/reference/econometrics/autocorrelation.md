---
title: "autocorrelation"
description: "Learn how to perform the Durbin-Watson test for autocorrelation in Python.  Understand the parameters and return value of the function, and how to use exogenous  variables in the analysis. This documentation provides a detailed explanation."
keywords:
- Durbin-Watson test
- autocorrelation
- Python
- data analysis
- exogenous variables
- parameter
- return
- documentation
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics/autocorrelation - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Perform Durbin-Watson test for autocorrelation.

 The Durbin-Watson test is a widely used method for detecting the presence of autocorrelation in the residuals
 from a statistical or econometric model. Autocorrelation occurs when past values in the data series influence
 future values, which can be a critical issue in time-series analysis, affecting the reliability of
 model predictions. The test provides a statistic that ranges from 0 to 4, where a value around 2 suggests
 no autocorrelation, values towards 0 indicate positive autocorrelation, and values towards 4 suggest
 negative autocorrelation. Understanding the degree of autocorrelation helps in refining models to better capture
 the underlying dynamics of the data, ensuring more accurate and trustworthy results.


Examples
--------

```python
from openbb import obb
# Perform Durbin-Watson test for autocorrelation.
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()
obb.econometrics.autocorrelation(data=stock_data, y_column="close", x_columns=["open", "high", "low"])
obb.econometrics.autocorrelation(y_column='close', x_columns=['open', 'high', 'low'], data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
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
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : Dict
        OBBject with the results being the score from the test.
```

