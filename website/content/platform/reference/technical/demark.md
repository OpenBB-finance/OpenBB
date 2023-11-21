---
title: demark
description: Learn how to use the Demark sequential indicator function in the OBBject
  library to analyze stock market data and calculate specific values. See examples
  of its implementation with the OpenBB package.
keywords:
- Demark sequential indicator
- data
- index
- target
- show_all
- asint
- offset
- OBBject
- List[Data]
- calculated data
- examples
- openbb
- equity
- price
- historical
- symbol
- start_date
- provider
- fmp
- technical
- demark
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical /demark - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Demark sequential indicator.
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
demark_data = obb.technical.demark(data=stock_data.results,offset=0)
```


---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | List of data to be used for the calculation. | None | False |
| index | str | Index column name to use with `data`, by default "date". | date | True |
| target | str | Target column name, by default "close". | close | True |
| show_all | bool | Show 1 - 13. If set to False, show 6 - 9 | True | True |
| asint | bool | If True, fill NAs with 0 and change type to int, by default True. | True | True |
| offset | int | How many periods to offset the result | 0 | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
The calculated data.
```

---

