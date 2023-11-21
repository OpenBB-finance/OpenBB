---
title: rm
description: The page consists of two main components or features. Initially, it details
  a function designed to return the roadmap for each individual cryptocurrency, explaining
  how data can be sorted and what the output will look like. Later, it describes a
  function aimed at plotting the roadmap for each cryptocurrency, including details
  on the parameters users will need to understand and adjust for the purpose of the
  function.
keywords:
- cryptocurrency
- roadmap
- data sorting
- function parameters
- plotting
- matplotlib
- crypto symbol
- python programming
- dataframe
- reverse order
- export data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.rm - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns coin roadmap

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/messari_model.py#L243)]

```python wordwrap
openbb.crypto.dd.rm(symbol: str, ascend: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check roadmap | None | False |
| ascend | bool | reverse order | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | roadmap |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots coin roadmap

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/messari_view.py#L277)]

```python wordwrap
openbb.crypto.dd.rm_chart(symbol: str, ascend: bool = True, limit: int = 5, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check roadmap | None | False |
| ascend | bool | reverse order | True | True |
| limit | int | number to show | 5 | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>