---
title: "kurtosis"
description: "Calculate the rolling kurtosis of a target column within a given window size"
keywords:
- quantitative
- rolling
- kurtosis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="quantitative/rolling/kurtosis - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the rolling kurtosis of a target column within a given window size.

 Kurtosis measures the "tailedness" of the probability distribution of a real-valued random variable.
 High kurtosis indicates a distribution with heavy tails (outliers), suggesting a higher risk of extreme outcomes.
 Low kurtosis indicates a distribution with lighter tails (less outliers), suggesting less risk of extreme outcomes.
 This function helps in assessing the risk of outliers in financial returns or other time series data over a specified
 rolling window.


Examples
--------

```python
from openbb import obb
# Get Rolling Kurtosis.
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp").to_df()
returns = stock_data["close"].pct_change().dropna()
obb.quantitative.rolling.kurtosis(data=returns, target="close", window=252)
obb.quantitative.rolling.kurtosis(target='close', window=2, data=[{'date': '2023-01-02', 'close': 0.05}, {'date': '2023-01-03', 'close': 0.08}, {'date': '2023-01-04', 'close': 0.07}, {'date': '2023-01-05', 'close': 0.06}, {'date': '2023-01-06', 'close': 0.06}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | The time series data as a list of data points. |  | False |
| target | str | The name of the column for which to calculate kurtosis. |  | False |
| window | PositiveInt | The number of observations used for calculating the rolling measure. |  | False |
| index | str, optional | The name of the index column, default is "date". |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        An object containing the rolling kurtosis values.
```

