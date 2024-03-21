---
title: "variance"
description: "Calculate the rolling variance of a target column within a given window size"
keywords:
- quantitative
- rolling
- variance
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="quantitative/rolling/variance - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the rolling variance of a target column within a given window size.

 Variance measures the dispersion of a set of data points around their mean. It is a key metric for
 assessing the volatility and stability of financial returns or other time series data over a specified rolling window.


Examples
--------

```python
from openbb import obb
# Get Rolling Variance.
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()
returns = stock_data["close"].pct_change().dropna()
obb.quantitative.rolling.variance(data=returns, target="close", window=252)
obb.quantitative.rolling.variance(target='close', window=2, data=[{'date': '2023-01-02', 'close': 0.05}, {'date': '2023-01-03', 'close': 0.08}, {'date': '2023-01-04', 'close': 0.07}, {'date': '2023-01-05', 'close': 0.06}, {'date': '2023-01-06', 'close': 0.06}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | The time series data as a list of data points. |  | False |
| target | str | The name of the column for which to calculate variance. |  | False |
| window | PositiveInt | The number of observations used for calculating the rolling measure. |  | False |
| index | str, optional | The name of the index column, default is "date". |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        An object containing the rolling variance values.
```

