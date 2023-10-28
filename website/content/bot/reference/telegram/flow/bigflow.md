---
title: bigflow
description: The page illustrates the 'bigflow' command for retrieving the top 20
  largest flows by premium for a stock, considering the price of the option at the
  time of the trade and the trade volume.
keywords:
- bigflow
- stock analysis
- option trading
- stock ticker
- trade volume
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="flow: bigflow - Telegram Reference | OpenBB Bot Docs" />

This command retrieves the top 20 largest flow by premium for a stock. We calculate the largest flow by multiplying the price of the option at the time of the trade by the volume of that trade.

### Usage

```python wordwrap
/bigflow ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/bigflow AMD
```
---
