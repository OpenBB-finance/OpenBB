---
title: "mean"
description: "Calculate the mean (average) of a target column"
keywords:
- quantitative
- stats
- mean
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="quantitative/stats/mean - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the mean (average) of a target column.

 The rolling mean is a simple moving average that calculates the average of a target variable.
 This function is widely used in financial analysis to smooth short-term fluctuations and highlight longer-term trends
 or cycles in time series data.


Examples
--------

```python
from openbb import obb
# Get Mean.
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()
returns = stock_data["close"].pct_change().dropna()
obb.quantitative.stats.mean(data=returns, target="close")
obb.quantitative.stats.mean(target='close', data=[{'date': '2023-01-02', 'close': 0.05}, {'date': '2023-01-03', 'close': 0.08}, {'date': '2023-01-04', 'close': 0.07}, {'date': '2023-01-05', 'close': 0.06}, {'date': '2023-01-06', 'close': 0.06}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | The time series data as a list of data points. |  | False |
| target | str | The name of the column for which to calculate the mean. |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        An object containing the mean value.
```

