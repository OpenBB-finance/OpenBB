---
title: ichimoku
description: Learn about Ichimoku Cloud, a versatile indicator that defines support
  and resistance, identifies trend direction, gauges momentum, and provides trading
  signals. Explore its parameters and usage in Python.
keywords:
- Ichimoku Cloud
- Ichimoku Kinko Hyo
- versatile indicator
- support and resistance
- trend direction
- momentum
- trading signals
- conversion line
- base line
- lagging span
- Chikou Span Column
- data leak
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical /ichimoku - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

The Ichimoku Cloud.

Also known as Ichimoku Kinko Hyo, is a versatile indicator that defines support and
resistance, identifies trend direction, gauges momentum and provides trading
signals. Ichimoku Kinko Hyo translates into "one look equilibrium chart". With
one look, chartists can identify the trend and look for potential signals within
that trend.

```python wordwrap
obb.technical.ichimoku(data: Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], numpy.ndarray, Data, List[Data]], index: str = date, conversion: int = 9, base: int = 26, lagging: int = 52, offset: int = 26, lookahead: bool = False)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | List of data to be used for the calculation. | None | False |
| index | str | Index column name to use with `data`, by default "date". | date | True |
| conversion | PositiveInt | Number of periods for the conversion line, by default 9. | 9 | True |
| base | PositiveInt | Number of periods for the base line, by default 26. | 26 | True |
| lagging | PositiveInt | Number of periods for the lagging span, by default 52. | 52 | True |
| offset | PositiveInt | Number of periods for the offset, by default 26. | 26 | True |
| lookahead | bool | drops the Chikou Span Column to prevent potential data leak | False | True |
</TabItem>

</Tabs>

---

## Returns

This function does not return a standardized model

---

