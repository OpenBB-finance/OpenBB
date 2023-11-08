---
title: instholdings
description: This page provides details on the instholdings command which retrieves
  the top 15 institutional holdings for a given stock, as reported to the United States
  Securities and Exchange Commission.
keywords:
- instholdings command
- institutional holdings
- stock
- United States Securities and Exchange Commission
- SEC
- stock ticker
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="duedilligence: instholdings - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the top 15 institutional holdings for a given stock. This list is retrieved from the most recent available institutional holdings reported to the United States Securities and Exchange Commission.

### Usage

```python wordwrap
/dd instholdings ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/dd instholdings ticker:AMD
```
---
