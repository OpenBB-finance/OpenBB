---
title: stats
description: The page gives insight into the use of the command to retrieve Options
  Statistics for a stock. It provides data on parameters like Open Interest, Volume,
  Implied Volatility and Earnings Move.
keywords:
- Options Statistics
- Stock Ticker
- Open Interest
- Volume
- Implied Volatility
- Earnings Move Data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="options: stats - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve Options Statistics for a stock with the given ticker symbol. This includes information such as Open Interest, Volume, Implied Volatility, and Earnings move data.

### Usage

```python wordwrap
/op stats ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/op stats ticker:AMC
```

---
