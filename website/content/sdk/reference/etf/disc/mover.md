---
title: mover
description: This page provides details and source code documentation for a function
  titled 'mover', used in scraping data for top etf movers. There's also a description
  of its parameters and returned values.
keywords:
- mover function
- scrape top etf movers
- source code documentation
- gainers
- decliners
- active
- etf volume
- etf price
- etf change
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf.disc.mover - Reference | OpenBB SDK Docs" />

Scrape data for top etf movers.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/discovery/wsj_model.py#L15)]

```python
openbb.etf.disc.mover(sort_type: str = "gainers", export: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sort_type | str | Data to get. Can be "gainers", "decliners" or "active" | gainers | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Datafame containing the name, price, change and the volume of the etf |
---
