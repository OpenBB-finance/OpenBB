---
title: "fisher"
description: "Learn about the Fisher Transform, a technical indicator created by John  F. Ehlers that converts prices into a Gaussian normal distribution. This indicator  can help identify extreme prices and turning points in asset prices. Discover how  to use the Fisher Transform with examples and parameter explanations."
keywords:
- Fisher Transform
- John F. Ehlers
- technical indicator
- Gaussian normal distribution
- extreme prices
- turning points
- price waves
- trend isolation
- indicator parameters
- data
- index column
- Fisher period
- Fisher Signal period
- indicator application
- OBBject
- example
- stock data
- equity
- historical price
- symbol
- start date
- data provider
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical/fisher - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Perform the Fisher Transform.

 A technical indicator created by John F. Ehlers that converts prices into a Gaussian
 normal distribution. The indicator highlights when prices have moved to an extreme,
 based on recent prices.
 This may help in spotting turning points in the price of an asset. It also helps
 show the trend and isolate the price waves within a trend.


Examples
--------

```python
from openbb import obb
# Perform the Fisher Transform.
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')
fisher_data = obb.technical.fisher(data=stock_data.results, length=14, signal=1)
obb.technical.fisher(length=2, data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | List of data to apply the indicator to. |  | False |
| index | str, optional | Index column name, by default "date" |  | False |
| length | PositiveInt, optional | Fisher period, by default 14 |  | False |
| signal | PositiveInt, optional | Fisher Signal period, by default 1 |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        List of data with the indicator applied.
```

