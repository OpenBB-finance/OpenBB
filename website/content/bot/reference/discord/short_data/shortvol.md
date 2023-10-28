---
title: shortvol
description: The page describes the 'shortvol' command used to retrieve 30-day history
  of short volume vs total volume of a stock ticker. It can be a useful tool to predict
  future price movements based on trade activity.
keywords:
- shortvol command
- stock ticker
- trade activity
- price movements
- total volume
- short volume
- trade data analysis
- stock trading
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="short_data: shortvol - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve a graph of the 30 day history of the short volume versus the total volume of the stock ticker. The graph also displays the ratio of the total amount of shares that have been sold short versus the total amount of shares traded over the past 30 days. This data can be used to get a better understanding of the stock's trading activity and potential future price movements.

### Usage

```python wordwrap
/sh shortvol ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/sh shortvol ticker:AMD
```

---
