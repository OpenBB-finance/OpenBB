---
title: atr
description: Learn about the Average True Range indicator used to measure volatility
  in financial data and how to apply it with examples.
keywords:
- Average True Range
- volatility measurement
- gaps
- limit moves
- data
- index column
- length
- moving average mode
- difference period
- offset
- OBBject
- List
- examples
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical /atr - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Average True Range.

Used to measure volatility, especially volatility caused by gaps or limit moves.
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
atr_data = obb.technical.atr(data=stock_data.results)
```


---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | List of data to apply the indicator to. | None | False |
| index | str | Index column name, by default "date" | date | True |
| length | PositiveInt | It's period, by default 14 | 14 | True |
| mamode | Literal["rma", "ema", "sma", "wma"] | Moving average mode, by default "rma" | rma | True |
| drift | NonNegativeInt | The difference period, by default 1 | 1 | True |
| offset | int | How many periods to offset the result, by default 0 | 0 | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
List of data with the indicator applied.
```

---

