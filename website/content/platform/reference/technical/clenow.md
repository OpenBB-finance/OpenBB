---
title: "clenow"
description: "Learn about Clenow Volatility Adjusted Momentum and how to calculate  it using Python code with openbb library. Explore the parameters, examples, and  returns of this technical analysis function."
keywords:
- Clenow Volatility Adjusted Momentum
- Clenow
- momentum
- data
- index column
- target column
- period
- calculation
- examples
- Python code
- openbb
- equity
- price
- historical
- symbol
- start date
- provider
- technical analysis
- stock data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical/clenow - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the Clenow Volatility Adjusted Momentum.

 The Clenow Volatility Adjusted Momentum is a sophisticated approach to understanding market momentum with a twist.
 It adjusts for volatility, offering a clearer picture of true momentum by considering how price movements are
 influenced by their volatility over a set period. It helps in identifying stronger, more reliable trends.


Examples
--------

```python
from openbb import obb
# Get the Clenow Volatility Adjusted Momentum.
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')
clenow_data = obb.technical.clenow(data=stock_data.results, period=90)
obb.technical.clenow(period=2, data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | List of data to be used for the calculation. |  | False |
| index | str, optional | Index column name to use with `data`, by default "date". |  | False |
| target | str, optional | Target column name, by default "close". |  | False |
| period | PositiveInt, optional | Number of periods for the momentum, by default 90. |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        The calculated data.
```

