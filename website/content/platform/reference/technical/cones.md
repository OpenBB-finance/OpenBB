---
title: "cones"
description: "Calculate realized volatility quantiles over rolling windows of time  using different volatility models. Understand the parameters and their effects,  such as index, quantile values, and is_crypto. Examples and code snippets provided."
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

<HeadTitle title="technical/cones - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the realized volatility quantiles over rolling windows of time.

 The cones indicator is designed to map out the ebb and flow of price movements through a detailed analysis of
 volatility quantiles. By examining the range of volatility within specific time frames, it offers a nuanced view of
 market behavior, highlighting periods of stability and turbulence.

 The model for calculating volatility is selectable and can be one of the following:
 - Standard deviation
 - Parkinson
 - Garman-Klass
 - Hodges-Tompkins
 - Rogers-Satchell
 - Yang-Zhang

 Read more about it in the model parameter description.


Examples
--------

```python
from openbb import obb
# Get the cones indicator.
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')
cones_data = obb.technical.cones(data=stock_data.results, lower_q=0.25, upper_q=0.75, model='STD')
obb.technical.cones(data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | The data to use for the calculation. |  | False |
| index | str, optional | Index column name to use with `data`, by default "date" |  | False |
| lower_q | float, optional | The lower quantile value for calculations |  | False |
| upper_q | float, optional | The upper quantile value for calculations |  | False |
| model | Literal["STD", "Parkinson", "Garman-Klass", "Hodges-Tompkins", "Rogers-Satchell", "Yang-Zhang"], optional | The model used to calculate realized volatility |  | False |
| is_crypto | bool, optional | Whether the data is crypto or not. If True, volatility is calculated for 365 days instead of 252 |  | False |
| trading_periods | Optional[int] [default: 252] | Number of trading periods in a year. |  | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        The cones data.
```

