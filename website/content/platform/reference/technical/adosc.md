---
title: "adosc"
description: "Learn about the Accumulation/Distribution Oscillator, also known as the  Chaikin Oscillator. This momentum indicator examines the strength of price moves  and underlying buying and selling pressure. Discover how divergence between the  indicator and price signals market turning points. Explore the parameters, data,  and examples for using this oscillator in your analysis."
keywords:
- Accumulation/Distribution Oscillator
- Chaikin Oscillator
- momentum indicator
- Accumulation-Distribution line
- buying pressure
- selling pressure
- divergence
- market turning points
- parameters
- data
- fast calculation
- slow calculation
- offset
- returns
- examples
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical/adosc - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the Accumulation/Distribution Oscillator.

 Also known as the Chaikin Oscillator.

 Essentially a momentum indicator, but of the Accumulation-Distribution line
 rather than merely price. It looks at both the strength of price moves and the
 underlying buying and selling pressure during a given time period. The oscillator
 reading above zero indicates net buying pressure, while one below zero registers
 net selling pressure. Divergence between the indicator and pure price moves are
 the most common signals from the indicator, and often flag market turning points.


Examples
--------

```python
from openbb import obb
# Get the Accumulation/Distribution Oscillator.
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')
adosc_data = obb.technical.adosc(data=stock_data.results, fast=3, slow=10, offset=0)
obb.technical.adosc(fast=2, slow=4, data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | List of data to be used for the calculation. |  | False |
| fast | PositiveInt, optional | Number of periods to be used for the fast calculation, by default 3. |  | False |
| slow | PositiveInt, optional | Number of periods to be used for the slow calculation, by default 10. |  | False |
| offset | int, optional | Offset to be used for the calculation, by default 0. |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        The calculated data.
```

