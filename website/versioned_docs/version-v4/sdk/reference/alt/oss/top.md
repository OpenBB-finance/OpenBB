---
title: top
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# top

<Tabs>
<TabItem value="model" label="Model" default>

Get repos sorted by stars or forks. Can be filtered by categories.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/oss/github_model.py#L135)]

```python
openbb.alt.oss.top(sortby: str, limit: int = 50, categories: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sortby | str | Sort repos by {stars, forks} | None | False |
| categories | str | Check for repo categories. If more than one separate with a comma: e.g., finance,investment. Default: None |  | True |
| limit | int | Number of repos to search for | 50 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with repos |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots repo summary [Source: https://api.github.com].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/oss/github_view.py#L65)]

```python
openbb.alt.oss.top_chart(sortby: str, categories: str = "", limit: int = 10, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sortby | str | Sort repos by {stars, forks} | None | False |
| categories | str | Check for repo categories. If more than one separate with a comma: e.g., finance,investment. Default: None |  | True |
| limit | int | Number of repos to look at | 10 | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>