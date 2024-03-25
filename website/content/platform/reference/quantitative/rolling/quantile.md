---
title: "quantile"
description: "Calculate the rolling quantile of a target column within a given window size at a specified quantile percentage"
keywords:
- quantitative
- rolling
- quantile
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="quantitative/rolling/quantile - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the rolling quantile of a target column within a given window size at a specified quantile percentage.

 Quantiles are points dividing the range of a probability distribution into intervals with equal probabilities,
 or dividing the sample in the same way. This function is useful for understanding the distribution of data
 within a specified window, allowing for analysis of trends, identification of outliers, and assessment of risk.


Examples
--------

```python
from openbb import obb
# Get Rolling Quantile.
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()
returns = stock_data["close"].pct_change().dropna()
obb.quantitative.rolling.quantile(data=returns, target="close", window=252, quantile_pct=0.25)
obb.quantitative.rolling.quantile(data=returns, target="close", window=252, quantile_pct=0.75)
obb.quantitative.rolling.quantile(target='close', window=2, data=[{'date': '2023-01-02', 'close': 0.05}, {'date': '2023-01-03', 'close': 0.08}, {'date': '2023-01-04', 'close': 0.07}, {'date': '2023-01-05', 'close': 0.06}, {'date': '2023-01-06', 'close': 0.06}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | The time series data as a list of data points. |  | False |
| target | str | The name of the column for which to calculate the quantile. |  | False |
| window | PositiveInt | The number of observations used for calculating the rolling measure. |  | False |
| quantile_pct | NonNegativeFloat, optional | The quantile percentage to calculate (e.g., 0.5 for median), default is 0.5. |  | False |
| index | str, optional | The name of the index column, default is "date". |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        An object containing the rolling quantile values with the median.
```

