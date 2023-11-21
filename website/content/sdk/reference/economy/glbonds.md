---
title: glbonds
description: Webpage on 'glbonds' function - a data scraping tool for global bonds
  information. It returns name, coupon rate, yield and change in yield.
keywords:
- glbonds
- data scraping
- global bonds
- yield
- rate
- change
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.glbonds - Reference | OpenBB SDK Docs" />

Scrape data for global bonds

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/wsj_model.py#L204)]

```python
openbb.economy.glbonds()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing name, coupon rate, yield and change in yield |
---
