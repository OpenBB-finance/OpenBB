---
title: allprints
description: This page provides a guide on the command 'allprints', which retrieves
  the last 15 combinations of Dark Pool and Blocks for a given stock ticker symbol,
  showing the date, time, price, and volume of the trades.
keywords:
- allprints command
- ticker symbol
- Dark Pool trades
- Blocks in stock market
- stock market trades
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="darkpool: allprints - Telegram Reference | OpenBB Bot Docs" />

This command retrieves the Last 15 Combination of Dark Pool and Blocks for a given ticker symbol. This can be used to view the most recent reported trades that involve Dark Pool and Blocks in the stock market. The results of this command will show the date, time, price, and volume of the trades.

### Usage

```python wordwrap
/allprints ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/allprints AMD
```

---
