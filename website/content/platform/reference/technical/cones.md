---
title: cones
description: Calculate realized volatility quantiles over rolling windows of time
  using different volatility models. Understand the parameters and their effects,
  such as index, quantile values, and is_crypto. Examples and code snippets provided.
keywords:
- realized volatility quantiles
- rolling windows of time
- calculate volatility
- parameter data
- quantile value
- volatility models
- standard deviation
- Parkinson volatility
- Garman-Klass volatility
- Hodges-Tompkins volatility
- Rogers-Satchell volatility
- Yang-Zhang volatility
- is_crypto
- cones data
- code example
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical /cones - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the realized volatility quantiles over rolling windows of time.

The model for calculating volatility is selectable.
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
cones_data = obb.technical.cones(data=stock_data.results, lower_q=0.25, upper_q=0.75, model="STD")
```


---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | The data to use for the calculation. | None | False |
| index | str | Index column name to use with `data`, by default "date" | date | True |
| lower_q | float | The lower quantile value for calculations | 0.25 | True |
| upper_q | float | The upper quantile value for calculations | 0.75 | True |
| model | Literal["STD", "Parkinson", "Garman-Klass", "Hodges-Tompkins", "Rogers-Satchell", "Yang-Zhang"] | The model used to calculate realized volatility

    Standard deviation measures how widely returns are dispersed from the average return.
    It is the most common (and biased) estimator of volatility.

    Parkinson volatility uses the high and low price of the day rather than just close to close prices.
    It is useful for capturing large price movements during the day.

    Garman-Klass volatility extends Parkinson volatility by taking into account the opening and closing price.
    As markets are most active during the opening and closing of a trading session;
    it makes volatility estimation more accurate.

    Hodges-Tompkins volatility is a bias correction for estimation using an overlapping data sample.
    It produces unbiased estimates and a substantial gain in efficiency.

    Rogers-Satchell is an estimator for measuring the volatility with an average return not equal to zero.
    Unlike Parkinson and Garman-Klass estimators, Rogers-Satchell incorporates a drift term,
    mean return not equal to zero.

    Yang-Zhang volatility is the combination of the overnight (close-to-open volatility).
    It is a weighted average of the Rogers-Satchell volatility and the open-to-close volatility. | STD | True |
| is_crypto | bool | Whether the data is crypto or not. If True, volatility is calculated for 365 days instead of 252 | False | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
The cones data.
```

---

