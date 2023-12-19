---
title: ermove
description: The documentation page provides a detailed explanation of the ermove
  command that allows users to fetch the implied stock move based on current option
  prices. It also guides on using the stock ticker to retrieve this information.
keywords:
- ermove command
- retrieve implied move
- stock
- option prices
- stock movement measure
- option's expiration
- stock ticker
- stock market
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="duedilligence: ermove - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the implied move for a stock based on the current option prices. The implied move is a measure of how far the stock is expected to move during the option's expiration.

### Usage

```python wordwrap
/dd ermove ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/dd ermove ticker:AMD
```
---
