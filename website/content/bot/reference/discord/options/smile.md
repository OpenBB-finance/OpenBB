---
title: smile
description: This page instructs users on how to use the '/op smile' command to retrieve
  the Options Volatility Smile for given stock tickers and expiry dates. It is especially
  beneficial for those seeking to understand market sentiments and implied volatility.
keywords:
- Options Volatility Smile
- Stock Ticker
- Expiration Date
- Strike Price
- Market Sentiment
- Implied Volatility
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="options: smile - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the Options Volatility Smile for the given ticker and expiry. The Options Volatility Smile is a graphical representation of the implied volatility for a given option that can be used to gauge the market sentiment for a particular security.

### Usage

```python wordwrap
/op smile ticker expiry [min_sp] [max_sp]
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
/op smile ticker:AMD expiry:2022-07-29
```

```
/op smile ticker:AMD expiry:2022-07-29 min_sp:10 max_sp:100
```

---
