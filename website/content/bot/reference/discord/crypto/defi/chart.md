---
title: chart
description: This page provides a guide on how to retrieve a chart of the top DeFi
  protocols by market capitalization. It explains the usage, parameters, and examples
  of '/crypto defi chart' command to have a visual overview of the current DeFi landscape.
keywords:
- DeFi
- market capitalization
- visual representation
- total DeFi market size
- ' crypto'
- chart
- protocols
- Total Value Locked
- Market Cap
- sort data
- chain
- sort order
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="defi - crypto: chart - Discord Reference | OpenBB Bot Docs" />

This command will retrieve a chart of the top DeFi protocols by market capitalization. It will provide a visual representation of the relative size of each protocol, as well as an overview of the total DeFi market size. This will enable users to get a better understanding of the current DeFi landscape and identify which protocols are leading the way.

### Usage

```python wordwrap
/crypto defi chart
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
/crypto defi chart
```
---
