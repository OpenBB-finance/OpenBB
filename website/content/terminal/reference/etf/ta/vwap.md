---
title: vwap
description: Learn how to use the Volume Weighted Average Price, a tool that measures
  the average typical price by volume. It is used with intraday charts to identify
  the general direction of the market.
keywords:
- VWAP
- intraday charts
- average price
- volume
- market direction
- stock analysis
- GOOGL
- USD
- financial data
- trading
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf/ta/vwap - Reference | OpenBB Terminal Docs" />

The Volume Weighted Average Price that measures the average typical price by volume. It is typically used with intraday charts to identify general direction.

### Usage

```python
vwap [-o N_OFFSET] [--start START] [--end END]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_offset | offset | 0 | True | None |
| start | Starting date to select | None | True | None |
| end | Ending date to select | None | True | None |


---

## Examples

```python
2022 Feb 16, 11:36 (🦋) /stocks/ta/ $ load GOOGL -i 1

Loading Intraday 1min GOOGL stock with starting period 2022-02-10 for analysis.

Datetime: 2022 Feb 16 11:36
Timezone: America/New_York
Currency: USD
Market:   CLOSED

2022 Feb 16, 11:36 (🦋) /stocks/ta/ $ vwap
```
![vwap](https://user-images.githubusercontent.com/46355364/154312502-9377c57c-6e34-42a6-b021-674e7d4561dd.png)

---
