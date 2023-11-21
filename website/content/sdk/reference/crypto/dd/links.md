---
title: links
description: 'This documentation page includes instructions on how to use two specific
  functions: ''links'' and ''links_chart'', part of OpenBB''s crypto asset due diligence
  utilities. These functions help users understand and demonstrate how to handle crypto
  asset links using Python within the OpenBB terminal.'
keywords:
- OpenBB crypto due diligence
- Crypto asset links utility
- Python cryptocurrency utilities
- Crypto symbol link checking
- Dataframe export to CSV, JSON, XLS
- External axes in Python
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.links - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns asset's links

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/messari_model.py#L197)]

```python
openbb.crypto.dd.links(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check links | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | asset links |
---

</TabItem>
<TabItem value="view" label="Chart">

Prints table showing coin links

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/messari_view.py#L249)]

```python
openbb.crypto.dd.links_chart(symbol: str, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check links | None | False |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
