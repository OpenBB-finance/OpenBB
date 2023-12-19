---
title: sumday
description: This documentation page details the use of the sumday command in a trading
  platform, explaining its purpose, usage, and parameters, including the concept of
  stock tickers, total premium, and trade categorization.
keywords:
- sumday command
- stock ticker
- total premium
- trading day
- trade categorization
- bid/ask
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="flow: sumday - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the total premium of the given stock ticker for the current trading day. We categorize the calls and puts by where the trade occurred on the bid/ask. For example, Above Ask, means the trade happened over the current Ask price.

### Usage

```python wordwrap
/flow sumday ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/flow sumday ticker:AMD
```

---
