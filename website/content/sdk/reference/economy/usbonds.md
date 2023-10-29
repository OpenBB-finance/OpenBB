---
title: usbonds
description: This page provides a comprehensive guide on how to use OpenBB-finance's
  us bonds data scraping function from OpenBBTerminal's wsj_model python script. The
  function returns a dataframe containing bond's name, its coupon rate, yield and
  change in yield.
keywords:
- us bonds
- data scraping
- OpenBB-finance
- economy
- wsj_model
- parameters
- dataframe
- name
- coupon rate
- yield
- change in yield
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.usbonds - Reference | OpenBB SDK Docs" />

Scrape data for us bonds

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/wsj_model.py#L161)]

```python
openbb.economy.usbonds()
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
