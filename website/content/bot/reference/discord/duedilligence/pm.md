---
title: pm
description: This page describes the command that retrieves premarket data for a given
  stock ticker. It is a valuable resource for those keen on understanding a stock's
  performance before the regular market commences.
keywords:
- stock
- premarket data
- stock ticker
- market performance
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="duedilligence: pm - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve premarket data for a given stock ticker. It will fetch the latest price, the premarket change, and the premarket percentage change of the selected stock. This is useful for those who want to get an idea of the stock's performance before the regular market opens.

### Usage

```python wordwrap
/dd pm ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/dd pm ticker:AMD
```
---
