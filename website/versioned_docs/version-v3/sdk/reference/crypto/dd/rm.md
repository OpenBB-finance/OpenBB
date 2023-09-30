---
title: rm
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# rm

<Tabs>
<TabItem value="model" label="Model" default>

Returns coin roadmap

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/messari_model.py#L236)]

```python
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

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/messari_view.py#L284)]

```python
openbb.crypto.dd.rm_chart(symbol: str, ascend: bool = True, limit: int = 5, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check roadmap | None | False |
| ascend | bool | reverse order | True | True |
| limit | int | number to show | 5 | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>