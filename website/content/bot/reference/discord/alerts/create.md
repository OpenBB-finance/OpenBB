---
title: create
description: This page provides instructions on how to use the 'create' command to
  set up price alerts for specific trading symbols. It includes usage examples and
  a detailed description of parameters involved such as the ticker, condition, and
  price.
keywords:
- price alerts
- trading symbols
- condition
- price
- creation command
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alerts: create - Discord Reference | OpenBB Bot Docs" />

This command creates an alert for a given symbol (ex. BTCUSD) that will notify the user when the price is equal to or above the user defined price.

### Usage

```python wordwrap
/alerts create ticker condition price
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Ticker to set alert for | False | None |
| condition | Condition to set alert for | False | Equal or Above, Equal or Below |
| price | Price to set alert for | False | None |


---

## Examples

```
/alerts create ticker:BTCUSD condition:Equal or Above price:1000
```

```
/alerts create ticker:SPY condition:Equal or Below price:400
```

---
