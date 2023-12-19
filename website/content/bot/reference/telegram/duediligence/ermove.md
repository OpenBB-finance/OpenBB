---
title: ermove
description: The ermove command allows users to retrieve the implied move for any
  given stock, based on current option prices. Learn more about its usage, parameters,
  and examples.
keywords:
- ermove
- implied move
- option prices
- stock
- expiration
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="duediligence: ermove - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the implied move for a stock based on the current option prices. The implied move is a measure of how far the stock is expected to move during the option's expiration.

### Usage

```python wordwrap
/ermove ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/ermove AMD
```

---
