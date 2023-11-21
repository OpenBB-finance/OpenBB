---
title: bbands
description: Learn about Bollinger Bands, a popular trading indicator used to identify
  volatility, overbought or oversold conditions, support and resistance levels, and
  price targets. Understand how they work, their parameters, and how to use them effectively
  in your trading strategy.
keywords:
- Bollinger Bands
- trading indicator
- volatility
- buy or sell signals
- overbought or oversold conditions
- support or resistance level
- price targets
- moving average
- standard deviation
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="technical /bbands - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Bollinger Bands.

Consist of three lines. The middle band is a simple moving average (generally 20
periods) of the typical price (TP). The upper and lower bands are F standard
deviations (generally 2) above and below the middle band.
The bands widen and narrow when the volatility of the price is higher or lower,
respectively.

Bollinger Bands do not, in themselves, generate buy or sell signals;
they are an indicator of overbought or oversold conditions. When the price is near the
upper or lower band it indicates that a reversal may be imminent. The middle band
becomes a support or resistance level. The upper and lower bands can also be
interpreted as price targets. When the price bounces off of the lower band and crosses
the middle band, then the upper band becomes the price target.
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
bbands = obb.technical.bbands(
    data=stock_data.results, target="close", length=50, std=2, mamode="sma", offset=0
)
```


---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | List[Data] | List of data to be used for the calculation. | None | False |
| target | str | Target column name. | close | True |
| index | str | Index column name to use with `data`, by default "date". | date | True |
| length | int | Number of periods to be used for the calculation, by default 50. | 50 | True |
| std | NonNegativeFloat | Standard deviation to be used for the calculation, by default 2. | 2 | True |
| mamode | Literal["sma", "ema", "wma", "rma"] | Moving average mode to be used for the calculation, by default "sma". | sma | True |
| offset | int | Offset to be used for the calculation, by default 0. | 0 | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
The calculated data.
```

---

