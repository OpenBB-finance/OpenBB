---
title: "cointegration"
description: "Learn how to use the two-step Engle-Granger test to show co-integration  between two time series in Python. Explore the parameters, input dataset, data columns,  and the OBBject returned with the test results."
keywords:
- co-integration
- Engle-Granger test
- time series
- data
- columns
- cointegration
- maxlag
- Python
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics/cointegration - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Show co-integration between two timeseries using the two step Engle-Granger test.

 The two-step Engle-Granger test is a method designed to detect co-integration between two time series.
 Co-integration is a statistical property indicating that two or more time series move together over the long term,
 even if they are individually non-stationary. This concept is crucial in economics and finance, where identifying
 pairs or groups of assets that share a common stochastic trend can inform long-term investment strategies
 and risk management practices. The Engle-Granger test first checks for a stable, long-term relationship by
 regressing one time series on the other and then tests the residuals for stationarity.
 If the residuals are found to be stationary, it suggests that despite any short-term deviations,
 the series are bound by an equilibrium relationship over time.


Examples
--------

```python
from openbb import obb
# Perform co-integration test between two timeseries.
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()
obb.econometrics.cointegration(data=stock_data, columns=["open", "close"])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | Input dataset. |  | False |
| columns | List[str] | Data columns to check cointegration |  | False |
| maxlag | PositiveInt | Number of lags to use in the test. |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : Data
        OBBject with the results being the score from the test.
```

