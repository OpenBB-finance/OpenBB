---
title: "unitroot_test"
description: "Learn about the Unit Root Test function in Python, including the Augmented  Dickey-Fuller test and the Kwiatkowski-Phillips-Schmidt-Shin test. Explore the parameters,  such as data, target, fuller_reg, and kpss_reg, and understand how to interpret  the unit root tests summary."
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

<HeadTitle title="quantitative/unitroot_test - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get Unit Root Test.

 This function applies two renowned tests to assess whether your data series is stationary or if it contains a unit
 root, indicating it may be influenced by time-based trends or seasonality. The Augmented Dickey-Fuller (ADF) test
 helps identify the presence of a unit root, suggesting that the series could be non-stationary and potentially
 unpredictable over time. On the other hand, the Kwiatkowski-Phillips-Schmidt-Shin (KPSS) test checks for the
 stationarity of the series, where failing to reject the null hypothesis indicates a stable, stationary series.
 Together, these tests provide a comprehensive view of your data's time series properties, essential for
 accurate modeling and forecasting.


Examples
--------

```python
from openbb import obb
# Get Unit Root Test.
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp').to_df()
obb.quantitative.unitroot_test(data=stock_data, target='close')
obb.quantitative.unitroot_test(target='close', data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | Time series data. |  | False |
| target | str | Target column name. |  | False |
| fuller_reg | Literal["c", "ct", "ctt", "nc", "c"] | Regression type for ADF test. |  | False |
| kpss_reg | Literal["c", "ct"] | Regression type for KPSS test. |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : UnitRootModel
        Unit root tests summary.
```

