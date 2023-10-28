---
title: allblocks
description: Page explaining the allblocks command in a trading platform, used to
  retrieve and summarise the last 15 block trades of a specified security.
keywords:
- allblocks
- block trades
- security
- stock ticker
- trade summary
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="darkpool: allblocks - Telegram Reference | OpenBB Bot Docs" />

The command allows the user to retrieve the last 15 block trades of a given security. This command will provide a summary of the last 15 block trades, including the time, price, quantity, and total gross value of each trade.

### Usage

```python wordwrap
/allblocks ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/allblocks AMD
```

---
