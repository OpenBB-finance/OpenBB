---
title: heatmap
description: Learn how to use the heatmap command to easily view stock market performance.
  This guide outlines its usage, parameters, and provides examples for both the market
  and sector filters.
keywords:
- heatmap command
- stock market performance
- market filter
- sector filter
- usage of heatmap
- parameters of heatmap
- example of heatmap command
- S&P 500
- NASDAQ 100
- Russell 2000
- Russell 1000
- Dow Jones 30
- Crypto
- Basic Materials
- Conglomerates
- Consumer Goods
- Financial
- Healthcare
- Industrial Goods
- Services
- Technology
- Utilities
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="general: heatmap - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve Daily Heat Maps by Market and Sector. The Daily Heat Maps will allow the user a quick overview of current stock market performance.

### Usage

```python wordwrap
/heatmap market [sector]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| market | Market to filter by. | False | S&P 500 (sp500), NASDAQ 100 (nasdaq100), Russell 2000 (iwm2000), Russell 1000 (iwb1000), Dow Jones 30 (dow30), Crypto (crypto) |
| sector | Sector to filter by. If not specified, all sectors are returned. | True | Basic Materials (1), Conglomerates (2), Consumer Goods (3), Financial (4), Healthcare (5), Industrial Goods (6), Services (7), Technology (8), Utilities (9) |


---

## Examples

```
/heatmap market:S&P 500
```
```
/heatmap market:S&P 500 sector:Services
```

---
