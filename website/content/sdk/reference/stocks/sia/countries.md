---
title: countries
description: This documentation page discusses how to retrieve all countries in Yahoo
  Finance data based on sector or industry. It provides an analysis method using the
  OpenBB stocks sia function with Python.
keywords:
- Yahoo Finance data
- sector industry analysis
- finance database
- OpenBB stocks
- filter by industry
- filter by sector
- countries data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.sia.countries - Reference | OpenBB SDK Docs" />

Get all countries in Yahoo Finance data based on sector or industry. [Source: Finance Database]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/sector_industry_analysis/financedatabase_model.py#L19)]

```python
openbb.stocks.sia.countries(industry: str = "", sector: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| industry | str | Filter retrieved countries by industry |  | True |
| sector | str | Filter retrieved countries by sector |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| list | List of possible countries |
---
