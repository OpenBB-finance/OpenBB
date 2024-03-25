---
title: "aroon"
description: "Learn about the Aroon Indicator, a trend indicator in technical analysis.  Understand how the Aroon Up and Down lines can help identify upward and downward  trends, and how to calculate and use the Aroon Indicator. Includes examples and  parameters."
keywords:
- Aroon Indicator
- Aroon Up and Down
- Aroon Indicator explanation
- trend indicator
- technical analysis
- Aroon Indicator usage
- Aroon Indicator examples
- Aroon Indicator parameters
- Aroon Indicator calculation
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical/aroon - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the Aroon Indicator.

 The word aroon is Sanskrit for "dawn's early light." The Aroon
 indicator attempts to show when a new trend is dawning. The indicator consists
 of two lines (Up and Down) that measure how long it has been since the highest
 high/lowest low has occurred within an n period range.

 When the Aroon Up is staying between 70 and 100 then it indicates an upward trend.
 When the Aroon Down is staying between 70 and 100 then it indicates an downward trend.
 A strong upward trend is indicated when the Aroon Up is above 70 while the Aroon Down is below 30.
 Likewise, a strong downward trend is indicated when the Aroon Down is above 70 while
 the Aroon Up is below 30. Also look for crossovers. When the Aroon Down crosses above
 the Aroon Up, it indicates a weakening of the upward trend (and vice versa).


Examples
--------

```python
from openbb import obb
# Get the Chande Momentum Oscillator.
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')
aaron_data = obb.technical.aroon(data=stock_data.results, length=25, scalar=100)
obb.technical.aroon(length=2, data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | List of data to be used for the calculation. |  | False |
| index | str, optional | Index column name to use with `data`, by default "date". |  | False |
| length | int, optional | Number of periods to be used for the calculation, by default 25. |  | False |
| scalar | int, optional | Scalar to be used for the calculation, by default 100. |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        The calculated data.
```

