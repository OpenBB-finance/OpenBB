---
title: wf
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# wf

<Tabs>
<TabItem value="model" label="Model" default>

Scrapes top coins withdrawal fees

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/withdrawalfees_model.py#L120)]

```python
openbb.crypto.ov.wf(limit: int = 100)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of coins to search, by default n=100, one page has 100 coins, so 1 page is scraped. | 100 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Coin, Lowest, Average, Median, Highest, Exchanges Compared |
---



</TabItem>
<TabItem value="view" label="Chart">

Top coins withdrawal fees

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/withdrawalfees_view.py#L18)]

```python
openbb.crypto.ov.wf_chart(limit: int = 15, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of coins to search | 15 | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>