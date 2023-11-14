---
title: watchlist_add
description: This page explains the usage of watchlist_add command which lets the
  user add one or more stocks to their watchlist in a finance related application.
keywords:
- watchlist_add command
- adding stocks to watchlist
- finance application commands
- stock market applications
- user guide for watchlist_add
- usage of watchlist_add
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="overview: watchlist_add - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to add a stock or stocks to their watchlist.

### Usage

```python wordwrap
/watchlist_add tickers
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| tickers | Add a ticker to your watchlist. You can add multiple tickers by separating them with a comma. | False | None |


---

## Examples

```
/watchlist_add AMD,GOOG,TSLA
```
---
