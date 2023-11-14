---
title: shortvol
description: Provides a 30 day history graph of the short volume vs the total volume
  of a stock ticker. It gives an understanding of trading activity & potential future
  price movements.
keywords:
- short volume
- stock
- trading
- stock ticker
- shares sold short
- shares traded
- future price movements
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="short_data: shortvol - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to retrieve a graph of the 30 day history of the short volume versus the total volume of the stock ticker. The graph also displays the ratio of the total amount of shares that have been sold short versus the total amount of shares traded over the past 30 days. This data can be used to get a better understanding of the stock's trading activity and potential future price movements.

### Usage

```python wordwrap
/shortvol ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/shortvol AMD
```
---
