---
title: "macd"
description: "Learn about the Moving Average Convergence Divergence (MACD), a powerful  technical indicator used in financial analysis. Understand how the MACD signals  trend changes, identifies overbought and oversold conditions, and generates buy/sell  signals. Explore the parameters and see examples of how to use this indicator in  Python."
keywords:
- Moving Average Convergence Divergence
- MACD
- Exponential Moving Averages
- Signal line
- trend changes
- overbought conditions
- oversold conditions
- divergence with price
- buy signal
- sell signal
- zero line
- parameters
- data
- target column
- fast EMA
- slow EMA
- signal EMA
- calculated data
- examples
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical/macd - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the Moving Average Convergence Divergence (MACD).

 Difference between two Exponential Moving Averages. The Signal line is an
 Exponential Moving Average of the MACD.

 The MACD signals trend changes and indicates the start of new trend direction.
 High values indicate overbought conditions, low values indicate oversold conditions.
 Divergence with the price indicates an end to the current trend, especially if the
 MACD is at extreme high or low values. When the MACD line crosses above the
 signal line a buy signal is generated. When the MACD crosses below the signal line a
 sell signal is generated. To confirm the signal, the MACD should be above zero for a buy,
 and below zero for a sell.


Examples
--------

```python
from openbb import obb
# Get the Moving Average Convergence Divergence (MACD).
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')
macd_data = obb.technical.macd(data=stock_data.results, target='close', fast=12, slow=26, signal=9)
# Example with mock data.
obb.technical.macd(fast=2, slow=3, signal=1, data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | List of data to be used for the calculation. |  | False |
| target | str | Target column name. |  | False |
| fast | int, optional | Number of periods for the fast EMA, by default 12. |  | False |
| slow | int, optional | Number of periods for the slow EMA, by default 26. |  | False |
| signal | int, optional | Number of periods for the signal EMA, by default 9. |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        The calculated data.
```

