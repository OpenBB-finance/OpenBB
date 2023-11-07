---
title: smile
description: The page provides a user guide on how to retrieve the Options Volatility
  Smile for a specific stock ticker and expiry, offering examples and parameters for
  enhanced understanding.
keywords:
- Options Volatility Smile
- Volatility
- Market Sentiment
- expiry
- Minimum Strike Price
- Maximum Strike Price
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="options: smile - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the Options Volatility Smile for the given ticker and expiry. The Options Volatility Smile is a graphical representation of the implied volatility for a given option that can be used to gauge the market sentiment for a particular security.

### Usage

```python wordwrap
/smile ticker expiry [min_sp] [max_sp]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| expiry | Expiration Date | False | None |
| min_sp | Minimum Strike Price | True | None |
| max_sp | Maximum Strike Price | True | None |


---

## Examples

```
/smile AMD 2022-07-29
```
```
/smile AMD 2022-07-29 10 100
```
---
