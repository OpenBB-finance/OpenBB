---
title: wma
description: Learn about the Weighted Moving Average (WMA) and how it is used to give
  more weight to recent data. Understand its unique calculation and how it compares
  to the Simple Moving Average. Find out the parameters for the WMA function, such
  as the target and index column names, length, and offset. See an example of using
  the WMA function in Python with the OpenBB library to calculate WMA data for historical
  stock prices.
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

<HeadTitle title="technical /wma - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Weighted Moving Average.

A Weighted Moving Average puts more weight on recent data and less on past data.
This is done by multiplying each bar's price by a weighting factor. Because of its
unique calculation, WMA will follow prices more closely than a corresponding Simple
Moving Average.
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
wma_data = obb.technical.wma(data=stock_data.results, target="close", length=50, offset=0)
```


---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | The data to use for the calculation. | None | False |
| target | str | Target column name. | close | True |
| index | str | Index column name to use with `data`, by default "date". | date | True |
| length | int | The length of the WMA, by default 50. | 50 | True |
| offset | int | The offset of the WMA, by default 0. | 0 | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
The WMA data.
```

---

