---
title: "ols_regression"
description: "Learn how to perform OLS regression using statsmodels in Python. This  documentation explains the parameters required and the object returned."
keywords:
- OLS regression
- statsmodels
- perform OLS regression
- data
- target column
- exogenous variables
- model
- results objects
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics/ols_regression - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Perform Ordinary Least Squares (OLS) regression.

 OLS regression is a fundamental statistical method to explore and model the relationship between a
 dependent variable and one or more independent variables. By fitting the best possible linear equation to the data,
 it helps uncover how changes in the independent variables are associated with changes in the dependent variable.
 This returns the model and results objects from statsmodels library.


Examples
--------

```python
from openbb import obb
# Perform Ordinary Least Squares (OLS) regression.
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()
obb.econometrics.ols_regression(data=stock_data, y_column="close", x_columns=["open", "high", "low"])
obb.econometrics.ols_regression(y_column='close', x_columns=['open', 'high', 'low'], data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
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
        OBBject with the results being model and results objects.
```

