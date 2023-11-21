---
title: stvl
description: 'The documentation explores the stvl functionality: a tool for returning
  and plotting historical values of the total sum of Total Value Locked (TVL) from
  all listed protocols. Source code links are included.'
keywords:
- stvl
- Total Value Locked
- cryptocurrency
- historical values
- OpenBB-terminal
- defi
- dataframe
- plotting
- export
- returns
- protocols
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.defi.stvl - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns historical values of the total sum of TVLs from all listed protocols.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/llama_model.py#L190)]

```python wordwrap
openbb.crypto.defi.stvl()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Historical values of total sum of Total Value Locked from all listed protocols. |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots historical values of the total sum of TVLs from all listed protocols.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/llama_view.py#L186)]

```python wordwrap
openbb.crypto.defi.stvl_chart(limit: int = 5, export: Optional[str] = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of records to display, by default 5 | 5 | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>