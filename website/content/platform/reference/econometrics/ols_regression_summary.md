---
title: "ols_regression_summary"
description: "Learn how to perform OLS regression using statsmodels in Python. Explore  the parameters and returns of the function, including the data, target column, exogenous  variables, and summary object."
keywords:
- OLS regression
- statsmodels
- summary object
- parameters
- data
- y_column
- x_columns
- exogenous variables
- returns
- OBBject
- model
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics/ols_regression_summary - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Perform Ordinary Least Squares (OLS) regression.

 This returns the summary object from statsmodels.


Examples
--------

```python
from openbb import obb
# Perform Ordinary Least Squares (OLS) regression and return the summary.
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()
obb.econometrics.ols_regression_summary(data=stock_data, y_column="close", x_columns=["open", "high", "low"])
obb.econometrics.ols_regression_summary(y_column='close', x_columns=['open', 'high', 'low'], data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
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
    results : Data
        OBBject with the results being summary object.
```

