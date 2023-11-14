---
title: bigflow
description: Detailed documentation on the use of the 'bigflow' command to retrieve
  the top 20 largest flows by premium for a stock. Learn how to use it, understand
  its parameters, and see examples to better your trading strategies.
keywords:
- bigflow command
- stock trading
- largest flow by premium
- trading strategy
- stock ticker
- option price
- trade volume
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="flow: bigflow - Discord Reference | OpenBB Bot Docs" />

This command retrieves the top 20 largest flow by premium for a stock. We calculate the largest flow by multiplying the price of the option at the time of the trade by the volume of that trade.

### Usage

```python wordwrap
/flow bigflow ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/flow bigflow ticker:AMD
```

---
