---
title: quote
description: Page describing the 'quote' command, which retrieves display quote stats
  for a stock. This includes information for 52 week high/low, market cap/float and
  200/50 day moving averages based on the specified stock ticker.
keywords:
- quote command
- display quote stats
- stock stats
- 52 week high/low
- market cap/float
- 200/50 day moving averages
- quick access
- stock ticker
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="general: quote - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve display quote stats for a stock - including the 52 week high/low, market cap/float, and 200/50 day moving averages. The command allows you to quickly and easily access the requested quote stats for the given stock.

### Usage

```python wordwrap
/quote ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/quote ticker:AMD
```

---
