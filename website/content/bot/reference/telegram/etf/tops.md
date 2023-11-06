---
title: tops
description: The page offers comprehensive details about the command 'ETF tops' which
  enables users to fetch the top ETFs for the day, sorted by gainers, losers, or active.
  The sort option is optional with default sort set to gainers.
keywords:
- ETF tops
- ETF gainers
- ETF losers
- active ETFs
- ETF sorting
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf: tops - Telegram Reference | OpenBB Bot Docs" />

This command returns the top ETFs for the day - sorted by gainers, losers, or active.

### Usage

```python wordwrap
/etf tops [sort]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| sort | Possible sort options to run. If not provided, defaults to gainers | True | gainers, losers, active |


---

## Examples

```
/etf tops
```
---
