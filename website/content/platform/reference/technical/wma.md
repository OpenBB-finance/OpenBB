---
title: "wma"
description: "Learn about the Weighted Moving Average (WMA) and how it is used to give  more weight to recent data. Understand its unique calculation and how it compares  to the Simple Moving Average. Find out the parameters for the WMA function, such  as the target and index column names, length, and offset. See an example of using  the WMA function in Python with the OpenBB library to calculate WMA data for historical  stock prices."
keywords:
- weighted moving average
- WMA
- moving average
- weighting factor
- price
- data
- calculation
- simple moving average
- parameters
- target column
- index column
- length
- offset
- returns
- examples
- python
- openbb
- equity
- price
- historical
- symbol
- start date
- provider
- wma data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical/wma - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the Weighted Moving Average (WMA).

 A Weighted Moving Average puts more weight on recent data and less on past data.
 This is done by multiplying each bar's price by a weighting factor. Because of its
 unique calculation, WMA will follow prices more closely than a corresponding Simple
 Moving Average.


Examples
--------

```python
from openbb import obb
# Get the Average True Range (ATR).
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')
wma_data = obb.technical.wma(data=stock_data.results, target='close', length=50, offset=0)
obb.technical.wma(length=2, data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | The data to use for the calculation. |  | False |
| target | str | Target column name. |  | False |
| index | str, optional | Index column name to use with `data`, by default "date". |  | False |
| length | int, optional | The length of the WMA, by default 50. |  | False |
| offset | int, optional | The offset of the WMA, by default 0. |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        The WMA data.
```

