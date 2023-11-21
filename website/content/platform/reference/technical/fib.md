---
title: fib
description: Learn how to create Fibonacci Retracement Levels using the openbb Python
  library for technical analysis. Apply the Fibonacci indicator to stock data and
  visualize the results.
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

<HeadTitle title="technical /fib - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Create Fibonacci Retracement Levels.
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
fib_data = obb.technical.fib(data=stock_data.results, period=120)
```


---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | List of data to apply the indicator to. | None | False |
| index | str | Index column name, by default "date" | date | True |
| period | PositiveInt | Period to calculate the indicator, by default 120 | 120 | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
List of data with the indicator applied.
```

---

