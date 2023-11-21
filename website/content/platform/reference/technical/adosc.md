---
title: adosc
description: Learn about the Accumulation/Distribution Oscillator, also known as the
  Chaikin Oscillator. This momentum indicator examines the strength of price moves
  and underlying buying and selling pressure. Discover how divergence between the
  indicator and price signals market turning points. Explore the parameters, data,
  and examples for using this oscillator in your analysis.
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

<HeadTitle title="technical /adosc - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Accumulation/Distribution Oscillator.

Also known as the Chaikin Oscillator.

Essentially a momentum indicator, but of the Accumulation-Distribution line
rather than merely price. It looks at both the strength of price moves and the
underlying buying and selling pressure during a given time period. The oscillator
reading above zero indicates net buying pressure, while one below zero registers
net selling pressure. Divergence between the indicator and pure price moves are
the most common signals from the indicator, and often flag market turning points.
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
adosc_data = obb.technical.adosc(data=stock_data.results, fast=3, slow=10, offset=0)
```


---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | List of data to be used for the calculation. | None | False |
| fast | PositiveInt | Number of periods to be used for the fast calculation, by default 3. | 3 | True |
| slow | PositiveInt | Number of periods to be used for the slow calculation, by default 10. | 10 | True |
| offset | int | Offset to be used for the calculation, by default 0. | 0 | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap

```

---

