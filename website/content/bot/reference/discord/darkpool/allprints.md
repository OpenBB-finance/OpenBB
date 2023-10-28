---
title: allprints
description: This page's content revolves around the 'allprints' command used for
  retrieving the last 15 combination of Dark Pool and Blocks for a specified ticker
  symbol. It covers usage, parameters, and examples.
keywords:
- allprints command
- Dark Pool and Blocks
- stock market trades
- ticker symbol
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="darkpool: allprints - Discord Reference | OpenBB Bot Docs" />

This command retrieves the Last 15 Combination of Dark Pool and Blocks for a given ticker symbol. This can be used to view the most recent reported trades that involve Dark Pool and Blocks in the stock market. The results of this command will show the date, time, price, and volume of the trades.

### Usage

```python wordwrap
/dp allprints ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/dp allprints ticker:AMD
```

---
