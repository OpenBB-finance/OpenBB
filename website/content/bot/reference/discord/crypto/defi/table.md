---
title: table
description: This page provides commands and parameters for retrieving and managing
  data about top DeFi protocols including total value locked, 24-hour volume, and
  price. It also guides on how to sort and filter this data.
keywords:
- DeFi protocols
- total value locked
- /crypto defi table
- 24 hour volume
- price
- sortby parameter
- chain parameter
- reverse parameter
- crypto
- table
- sorted data
- Market Cap
- Total Value Locked
- MCap
- TVL
- ethereum
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="defi - crypto: table - Discord Reference | OpenBB Bot Docs" />

This command allows the user to view a table of the top DeFi protocols and their associated information, such as the total value locked, 24 hour volume, and price. The table is sorted in descending order, with the top DeFi protocols at the top.

### Usage

```python wordwrap
/crypto defi table [sortby] [chain] [reverse]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| sortby | Column to sort data by (e.g., Total Value Locked) | True | Market Cap (MCap), Total Value Locked (TVL) |
| chain | Chain to filter by (e.g., ethereum) | True | None |
| reverse | Reverse the sort order | True | Yes |


---

## Examples

```
/crypto defi table
```
---
