---
title: ad
description: Learn about the Accumulation/Distribution Line and how it is interpreted
  to detect trends in price movement. Explore its parameters, usage, and see code
  examples.
keywords:
- Accumulation/Distribution Line
- On Balance Volume
- CLV
- divergence
- price
- trending upward
- flat
- flattening of the price
- Parameters
- data
- index
- offset
- Returns
- Examples
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical /ad - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

The Accumulation/Distribution Line.

Similar to the On Balance Volume (OBV).
Sums the volume times +1/-1 based on whether the close is higher than the previous
close. The Accumulation/Distribution indicator, however multiplies the volume by the
close location value (CLV). The CLV is based on the movement of the issue within a
single bar and can be +1, -1 or zero.


The Accumulation/Distribution Line is interpreted by looking for a divergence in
the direction of the indicator relative to price. If the Accumulation/Distribution
Line is trending upward it indicates that the price may follow. Also, if the
Accumulation/Distribution Line becomes flat while the price is still rising (or falling)
then it signals an impending flattening of the price.
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
ad_data = obb.technical.ad(data=stock_data.results,offset=0)
```


---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | List of data to be used for the calculation. | None | False |
| index | str | Index column name to use with `data`, by default "date". | date | True |
| offset | int | Offset of the AD, by default 0. | 0 | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap

```

---

