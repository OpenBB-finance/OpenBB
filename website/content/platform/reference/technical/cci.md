---
title: cci
description: Learn about the Commodity Channel Index (CCI) and how it can be used
  to detect market trends, overbought or oversold conditions, and price divergence.
  This documentation provides an overview of the CCI, its parameters, and its calculation,
  along with an explanation of the CCI data it returns.
keywords:
- Commodity Channel Index
- CCI
- market trends
- trading range
- overbought
- oversold
- price divergence
- price correction
- data
- index column
- length
- scalar
- CCI calculation
- CCI data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical /cci - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Commodity Channel Index (CCI).

The CCI is designed to detect beginning and ending market trends.
The range of 100 to -100 is the normal trading range. CCI values outside of this
range indicate overbought or oversold conditions. You can also look for price
divergence in the CCI. If the price is making new highs, and the CCI is not,
then a price correction is likely.

```python wordwrap
obb.technical.cci(data: Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], numpy.ndarray, Data, List[Data]], index: str = date, length: int = 14, scalar: float = 0.015)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | The data to use for the CCI calculation. | None | False |
| index | str | Index column name to use with `data`, by default "date". | date | True |
| length | PositiveInt | The length of the CCI, by default 14. | 14 | True |
| scalar | PositiveFloat | The scalar of the CCI, by default 0.015. | 0.015 | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
The CCI data.
```

---

