---
title: "fib"
description: "Learn how to create Fibonacci Retracement Levels using the openbb Python  library for technical analysis. Apply the Fibonacci indicator to stock data and  visualize the results."
keywords:
- Fibonacci Retracement Levels
- Fibonacci indicator
- technical analysis
- stock data
- Python
- data visualization
- open source library
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical/fib - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Create Fibonacci Retracement Levels.

 This method draws from a classic technique to pinpoint significant price levels
 that often indicate where the market might find support or resistance.
 It's a tool used to gauge potential turning points in the data by applying a
 mathematical approach rooted in nature's patterns. Is used to get insights into
 where prices could head next, based on historical movements.


Examples
--------

```python
from openbb import obb
# Get the Bollinger Band Width.
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')
fib_data = obb.technical.fib(data=stock_data.results, period=120)
obb.technical.fib(data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | List of data to apply the indicator to. |  | False |
| index | str, optional | Index column name, by default "date" |  | False |
| period | PositiveInt, optional | Period to calculate the indicator, by default 120 |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        List of data with the indicator applied.
```

