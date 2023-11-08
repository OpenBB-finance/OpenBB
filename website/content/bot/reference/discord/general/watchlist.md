---
title: watchlist
description: 'Learn how to use the watchlist command: add or remove stock tickers,
  retrieve an overview on current price, high/low, volume and change; get quick access
  to related data like flow, darkpool data, technical analysis and news.'
keywords:
- watchlist
- stocks
- add ticker
- edit ticker
- technical analysis
- stock price
- high/low
- volume
- change
- darkpool data
- stock news
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="general: watchlist - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve an overview of their watchlist, which includes the current price, high/low, volume, and change. You can also get other related information with a quick click like flow, darkpool data, technical analysis, and news - all from one spot.

### Usage

```python wordwrap
/watchlist [add] [edit]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| add | Add a ticker to your watchlist. You can add multiple tickers by separating them with a comma. | True | None |
| edit | Remove tickers from your watchlist. Choose Remove to bring up the interactive menu. | True | Remove |


---

## Examples

```
/watchlist
```
```
/watchlist add:AMD
```
```
/watchlist add:AMD,GOOG,TSLA
```
```
/watchlist edit:Remove
```

---
