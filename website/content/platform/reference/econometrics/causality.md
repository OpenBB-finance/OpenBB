---
title: "causality"
description: "Learn how to perform a Granger causality test to determine if X causes  y. Understand the parameters and the results returned by the test."
keywords:
- Granger causality test
- causality
- perform
- determine
- exogenous variables
- lags
- data
- target column
- results
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics/causality - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Perform Granger causality test to determine if X 'causes' y.

 The Granger causality test is a statistical hypothesis test to determine if one time series is useful in
 forecasting another. While 'causality' in this context does not imply a cause-and-effect relationship in
 the philosophical sense, it does test whether changes in one variable are systematically followed by changes
 in another variable, suggesting a predictive relationship. By specifying a lag, you set the number of periods to
 look back in the time series to assess this relationship. This test is particularly useful in economic and
 financial data analysis, where understanding the lead-lag relationship between indicators can inform investment
 decisions and policy making.


Examples
--------

```python
from openbb import obb
# Perform Granger causality test to determine if X 'causes' y.
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()
obb.econometrics.causality(data=stock_data, y_column="close", x_column="open")
# Example with mock data.
obb.econometrics.causality(y_column='close', x_column='open', lag=1, data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | Input dataset. |  | False |
| y_column | str | Target column. |  | False |
| x_column | str | Columns to use as exogenous variables. |  | False |
| lag | PositiveInt | Number of lags to use in the test. |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : Data
        OBBject with the results being the score from the test.
```

