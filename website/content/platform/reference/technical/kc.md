---
title: "kc"
description: "Learn how to use Keltner Channels, volatility-based bands used to determine  the direction of a trend. This documentation covers the Keltner Channels calculation,  breakout signals, and parameters like the moving average mode, length, scalar value,  and offset."
keywords:
- Keltner Channels
- volatility-based bands
- direction of a trend
- average true range
- ATR
- breakout signals
- Keltner Channels calculation
- moving average mode
- length of Keltner Channels
- scalar value for Keltner Channels
- offset for Keltner Channels
- Keltner Channels data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical/kc - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Calculate the Keltner Channels.

 Keltner Channels are volatility-based bands that are placed
 on either side of an asset's price and can aid in determining
 the direction of a trend.The Keltner channel uses the average
 true range (ATR) or volatility, with breaks above or below the top
 and bottom barriers signaling a continuation.


Examples
--------

```python
from openbb import obb
# Get the Keltner Channels.
stock_data = obb.equity.price.historical(symbol='TSLA', start_date='2023-01-01', provider='fmp')
kc_data = obb.technical.kc(data=stock_data.results, length=20, scalar=20, mamode='ema', offset=0)
obb.technical.kc(length=2, data=[{'date': '2023-01-02', 'open': 110.0, 'high': 120.0, 'low': 100.0, 'close': 115.0, 'volume': 10000.0}, {'date': '2023-01-03', 'open': 165.0, 'high': 180.0, 'low': 150.0, 'close': 172.5, 'volume': 15000.0}, {'date': '2023-01-04', 'open': 146.67, 'high': 160.0, 'low': 133.33, 'close': 153.33, 'volume': 13333.33}, {'date': '2023-01-05', 'open': 137.5, 'high': 150.0, 'low': 125.0, 'close': 143.75, 'volume': 12500.0}, {'date': '2023-01-06', 'open': 132.0, 'high': 144.0, 'low': 120.0, 'close': 138.0, 'volume': 12000.0}])
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | The data to use for the Keltner Channels calculation. |  | False |
| index | str, optional | Index column name to use with `data`, by default "date" |  | False |
| length | PositiveInt, optional | The length of the Keltner Channels, by default 20 |  | False |
| scalar | PositiveFloat, optional | The scalar to use for the Keltner Channels, by default 20 |  | False |
| mamode | Literal["ema", "sma", "wma", "hma", "zlma"], optional | The moving average mode to use for the Keltner Channels, by default "ema" |  | False |
| offset | NonNegativeInt, optional | The offset to use for the Keltner Channels, by default 0 |  | False |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[Data]
        The Keltner Channels data.
```

