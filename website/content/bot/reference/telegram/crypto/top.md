---
title: top
description: The page provides instructions on the use of the 'top' command, a feature
  to retrieve top cryptocurrencies by market capitalization, inclusive of component
  parameters and usage examples.
keywords:
- cryptocurrencies
- market capitalization
- top command
- user instructions
- command usage
- sortby parameter
- category filter
- reverse sort
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto: top - Telegram Reference | OpenBB Bot Docs" />

This command will retrieve the top cryptocurrencies, ranked by market capitalization, allowing the user to quickly get a snapshot of the current market.

### Usage

```python wordwrap
/top [sortby] [category] [reverse]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| sortby | Column to sort data by (e.g., mc) | True | mc, vol, 1hr, 1d, 1wk |
| category | Category to filter by (e.g., stablecoins) | True | None |
| reverse | Reverse the sort order (e.g., True) (default: False) | True | None |


---

## Examples

```
/top
```

```
/top mc marketing
```

---
