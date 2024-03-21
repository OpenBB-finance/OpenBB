---
title: "cg"
description: "Learn about the Center of Gravity (COG) indicator, how it predicts price  movements and reversals, and its use in range-bound markets. Explore the parameters,  examples, and how to calculate COG data with OpenBB for technical analysis."
keywords:
- center of gravity
- COG indicator
- price movements
- price reversals
- oscillators
- range-bound markets
- upcoming price change
- asset trading
- data
- COG calculation
- index column
- length
- COG data
- openbb
- equity price historical
- stock data
- symbol
- start date
- provider
- technical analysis
- TSLA
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical/cg - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the Center of Gravity.

 The Center of Gravity indicator, in short, is used to anticipate future price movements
 and to trade on price reversals as soon as they happen. However, just like other oscillators,
 the COG indicator returns the best results in range-bound markets and should be avoided when
 the price is trending. Traders who use it will be able to closely speculate the upcoming
 price change of the asset.


Examples
--------

```python
from openbb import obb
# Get the Center of Gravity (CG).
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')
cg_data = obb.technical.cg(data=stock_data.results, length=14)
obb.technical.cg(length=2, data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | The data to use for the COG calculation. |  | False |
| index | str, optional | Index column name to use with `data`, by default "date" |  | False |
| length | PositiveInt, optional | The length of the COG, by default 14 |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        The COG data.
```

