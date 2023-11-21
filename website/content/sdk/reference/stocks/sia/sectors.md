---
title: sectors
description: This documentation page offers details on how to retrieve all sectors
  in Yahoo Finance data based on criteria such as country or industry. The source
  code and the parameters for the function are provided.
keywords:
- Yahoo Finance data
- Finance Database
- Sector analysis
- Industry filter
- Country filter
- Stocks
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.sia.sectors - Reference | OpenBB SDK Docs" />

Get all sectors in Yahoo Finance data based on country or industry. [Source: Finance Database]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/sector_industry_analysis/financedatabase_model.py#L44)]

```python
openbb.stocks.sia.sectors(industry: str = "", country: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| industry | str | Filter retrieved sectors by industry |  | True |
| country | str | Filter retrieved sectors by country |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| list | List of possible sectors |
---
