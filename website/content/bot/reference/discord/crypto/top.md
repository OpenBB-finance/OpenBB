---
title: top
description: Command to retrieve the top cryptocurrencies by market cap, with optional
  sorting and filtering capabilities. It provides a quick snapshot of the current
  crypto market using specific commands.
keywords:
- crypto
- top cryptocurrencies
- market capitalization
- market cap
- stablecoins
- manufacturing
- sort
- filter
- reverse order
- command usage
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto: top - Discord Reference | OpenBB Bot Docs" />

This command will retrieve the top cryptocurrencies, ranked by market capitalization, allowing the user to quickly get a snapshot of the current market.

### Usage

```python wordwrap
/crypto top [sortby] [category] [reverse]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| sortby | Column to sort data by (e.g., Market Cap) | True | Market Cap (MCap) |
| category | Category to filter by (e.g., stablecoins) | True | None |
| reverse | Reverse the sort order | True | Yes |


---

## Examples

```
/crypto top
```

```
/crypto top sortby: Market Cap category: manufacturing
```
---
